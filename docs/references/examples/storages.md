# Reference: Storages Layer

## Правила storage-методов

- Один метод — одна SQL-операция (`insert`, `select`, `update`, `delete`).
- Без бизнес-логики: никаких `if entity.id > 0`, ветвлений по полям домена, вычислений.
- Без `logger.info(...)` и любого логирования состояния.
- Без `session.commit()` — транзакция управляется DI provider'ом.
- Возвращает domain schema через `model.to_domain()`, не ORM model.

Publication/public-read state machines follow the same storage rules, but use
PostgreSQL atomic operations for shared identifiers and pointers:

- Publication version is allocated in the database, for example by an
  `INSERT ... ON CONFLICT DO UPDATE ... RETURNING` counter row.
- Snapshots are append-only inserts; do not update previous snapshot payloads.
- Active visibility changes through one atomic active-pointer upsert.
- Public IDs and host/path route bindings are reserved by unique insert/upsert
  operations. `SELECT`/`exists` followed by insert or bind is not safe.
- Audit rows are inserted through the same session and rely on the same
  DI-managed Unit of Work for rollback.

**Антипаттерн (запрещено):**

```python
async def create(self, reservation: Reservation) -> Reservation:
    values = {"item_id": reservation.item_id, "quantity": reservation.quantity}
    if reservation.id > 0:           # ← бизнес-логика в storage
        values["id"] = reservation.id
    model = await self.session.scalar(
        insert(ReservationModel).values(**values).returning(ReservationModel)
    )
    if model is None:
        raise ReservationNotFoundError  # ← insert не возвращает None, логика лишняя
    return model.to_domain()
```

**Правильно:** условный выбор ID — ответственность use case или передаётся как явный параметр.


## Publication storage operations

Use placeholder model names here as a pattern, not as required class names.

```python
from sqlalchemy import insert
from sqlalchemy.dialects.postgresql import insert as pg_insert


async def allocate_version(self, entity_id: int) -> int:
    result = await self.session.scalar(
        pg_insert(PublicationCounterModel)
        .values(entity_id=entity_id, next_version=1)
        .on_conflict_do_update(
            index_elements=[PublicationCounterModel.entity_id],
            set_={"next_version": PublicationCounterModel.next_version + 1},
        )
        .returning(PublicationCounterModel.next_version)
    )
    if result is None:
        raise PublicationVersionAllocationError
    return result


async def insert_snapshot(self, snapshot: PublicationSnapshot) -> PublicationSnapshot:
    model = await self.session.scalar(
        insert(PublicationSnapshotModel)
        .values(
            entity_id=snapshot.entity_id,
            version=snapshot.version,
            payload=snapshot.payload,
            created_by=snapshot.created_by,
        )
        .returning(PublicationSnapshotModel)
    )
    if model is None:
        raise PublicationSnapshotInsertError
    return model.to_domain()


async def activate_snapshot(self, entity_id: int, snapshot_id: int, version: int) -> None:
    await self.session.execute(
        pg_insert(ActivePublicationModel)
        .values(entity_id=entity_id, snapshot_id=snapshot_id, version=version)
        .on_conflict_do_update(
            index_elements=[ActivePublicationModel.entity_id],
            set_={"snapshot_id": snapshot_id, "version": version},
        )
    )


async def reserve_public_id(self, public_id: str, entity_id: int) -> None:
    reserved_id = await self.session.scalar(
        pg_insert(PublicIdentifierModel)
        .values(public_id=public_id, entity_id=entity_id)
        .on_conflict_do_nothing(index_elements=[PublicIdentifierModel.public_id])
        .returning(PublicIdentifierModel.id)
    )
    if reserved_id is None:
        raise PublicIdentifierConflictError


async def bind_route(self, canonical_host: str, canonical_path: str, entity_id: int) -> None:
    binding_id = await self.session.scalar(
        pg_insert(RouteBindingModel)
        .values(
            canonical_host=canonical_host,
            canonical_path=canonical_path,
            entity_id=entity_id,
            active=True,
        )
        .on_conflict_do_nothing(
            index_elements=[
                RouteBindingModel.canonical_host,
                RouteBindingModel.canonical_path,
            ],
            index_where=RouteBindingModel.active.is_(True),
        )
        .returning(RouteBindingModel.id)
    )
    if binding_id is None:
        raise RouteBindingConflictError


async def append_audit_event(self, event: PublicationAuditEvent) -> None:
    await self.session.execute(
        insert(PublicationAuditEventModel).values(
            entity_id=event.entity_id,
            event_type=event.event_type.value,
            version=event.version,
            actor_id=event.actor_id,
            payload=event.payload,
        )
    )
```

For public-read storages, `to_domain()`/mapper code validates persisted snapshot
payloads. Malformed JSON, missing required fields, and unknown enum values raise
a domain exception instead of producing a best-effort public response.


## src/storages/models.py — SQLAlchemy ORM model

```python
from decimal import Decimal

from sqlalchemy import DECIMAL, BigInteger, PrimaryKeyConstraint, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from src.core.entities.enums import EntityStatusEnum
from src.core.entities.schemas import Entity


class Base(DeclarativeBase): ...


class EntityModel(Base):
    __tablename__ = "entities"
    __table_args__ = (PrimaryKeyConstraint("id", name="pk_entities"),)

    id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    amount: Mapped[Decimal] = mapped_column(DECIMAL(precision=18, scale=8), nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False)

    def to_domain(self) -> Entity:
        return Entity(
            id=self.id,
            name=self.name,
            amount=self.amount,
            status=EntityStatusEnum(self.status),
        )
```

## src/storages/database_storage.py — Storage implementation

```python
from dataclasses import dataclass

from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.entities.exceptions import EntityNotFoundError
from src.core.entities.schemas import Entity
from src.core.storages import EntityStorage
from src.storages.models import EntityModel


@dataclass
class DatabaseEntityStorage(EntityStorage):
    session: AsyncSession

    async def create(self, entity: Entity) -> None:
        await self.session.execute(
            insert(EntityModel).values(
                id=entity.id,
                name=entity.name,
                amount=entity.amount,
                status=entity.status.value,
            )
        )

    async def get_by_id(self, entity_id: int) -> Entity:
        model = await self.session.scalar(
            select(EntityModel).where(EntityModel.id == entity_id).with_for_update()
        )
        if not model:
            raise EntityNotFoundError
        return model.to_domain()
```

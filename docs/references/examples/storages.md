# Reference: Storages Layer

## Правила storage-методов

- Один метод — одна SQL-операция (`insert`, `select`, `update`, `delete`).
- Без бизнес-логики: никаких `if entity.id > 0`, ветвлений по полям домена, вычислений.
- Без `logger.info(...)` и любого логирования состояния.
- Без `session.commit()` — транзакция управляется DI provider'ом.
- Возвращает domain schema через `model.to_domain()`, не ORM model.

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

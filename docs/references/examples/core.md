# Reference: Core Layer

## src/core/use_case.py — Base UseCase interface

```python
from abc import ABCMeta, abstractmethod
from typing import Any


class UseCase(metaclass=ABCMeta):
    @abstractmethod
    async def execute(self, *args: Any, **kwargs: Any) -> Any:  # noqa: ANN401
        raise NotImplementedError
```

## src/core/exceptions.py

```python
class BaseExceptionError(Exception):
    detail: str = ""

    def __init__(self, detail: str = "") -> None:
        self.detail = detail or self.detail
        super().__init__(self.detail)
```

## src/core/\<domain\>/exceptions.py

```python
from src.core.exceptions import BaseExceptionError


class EntityNotFoundError(BaseExceptionError):
    detail: str = "ENTITY_NOT_FOUND_ERROR"
```

## src/core/\<domain\>/enums.py

```python
from enum import StrEnum


class EntityStatusEnum(StrEnum):
    ACTIVE = "active"
    INACTIVE = "inactive"
```

## src/core/\<domain\>/schemas.py

```python
from dataclasses import dataclass
from decimal import Decimal

from src.core.entities.enums import EntityStatusEnum


@dataclass(frozen=True, slots=True)
class Entity:
    id: int
    name: str
    amount: Decimal
    status: EntityStatusEnum


@dataclass(frozen=True, slots=True, kw_only=True)
class EntityParams:
    name: str
    amount: Decimal
    status: EntityStatusEnum
```

## src/core/storages.py

```python
from abc import ABCMeta, abstractmethod

from src.core.entities.schemas import Entity


class EntityStorage(metaclass=ABCMeta):
    @abstractmethod
    async def create(self, entity: Entity) -> None: ...

    @abstractmethod
    async def get_by_id(self, entity_id: int) -> Entity: ...
```

For publication-style state machines, core interfaces expose explicit atomic
storage operations instead of check-then-write helpers:

```python
class PublicationStorage(metaclass=ABCMeta):
    @abstractmethod
    async def get_publishable(self, entity_id: int) -> PublishableEntity: ...

    @abstractmethod
    async def allocate_version(self, entity_id: int) -> int: ...

    @abstractmethod
    async def insert_snapshot(self, snapshot: PublicationSnapshot) -> PublicationSnapshot: ...

    @abstractmethod
    async def reserve_public_id(self, public_id: str, entity_id: int) -> None: ...

    @abstractmethod
    async def bind_route(
        self,
        canonical_host: str,
        canonical_path: str,
        entity_id: int,
    ) -> None: ...

    @abstractmethod
    async def activate_snapshot(self, entity_id: int, snapshot_id: int, version: int) -> None: ...

    @abstractmethod
    async def append_audit_event(self, event: PublicationAuditEvent) -> None: ...
```

`reserve_public_id()` and `bind_route()` must be backed by unique PostgreSQL
operations. Do not model them as `exists(...)` plus a later insert/update.

## src/core/\<domain\>/use_cases.py

```python
from dataclasses import dataclass

from src.core.entities.schemas import Entity, EntityParams
from src.core.storages import EntityStorage
from src.core.use_case import UseCase


@dataclass(frozen=True, slots=True, kw_only=True)
class GetEntityUseCase(UseCase):
    storage: EntityStorage

    async def execute(self, entity_id: int) -> Entity:
        return await self.storage.get_by_id(entity_id=entity_id)


@dataclass(frozen=True, slots=True, kw_only=True)
class CreateEntityUseCase(UseCase):
    storage: EntityStorage

    async def execute(self, params: EntityParams) -> Entity:
        entity = Entity(
            id=0,
            name=params.name,
            amount=params.amount,
            status=params.status,
        )
        await self.storage.create(entity=entity)
        return entity
```

## Publication state-machine use case pattern

Publication use cases orchestrate domain decisions and storage calls, but they do
not open transactions or commit. The DI-managed request session is the Unit of
Work, so snapshot writes, public identifier reservation, route binding, active
pointer switch, and audit append either commit together or roll back together.

```python
@dataclass(frozen=True, slots=True, kw_only=True)
class PublishEntityUseCase(UseCase):
    storage: PublicationStorage

    async def execute(self, params: PublishEntityParams) -> PublicationResult:
        entity = await self.storage.get_publishable(entity_id=params.entity_id)
        version = await self.storage.allocate_version(entity_id=entity.id)
        snapshot = await self.storage.insert_snapshot(
            snapshot=PublicationSnapshot.from_entity(entity=entity, version=version),
        )
        await self.storage.reserve_public_id(public_id=params.public_id, entity_id=entity.id)
        await self.storage.bind_route(
            canonical_host=params.canonical_host,
            canonical_path=params.canonical_path,
            entity_id=entity.id,
        )
        await self.storage.append_audit_event(
            event=PublicationAuditEvent.published(entity_id=entity.id, version=version),
        )
        await self.storage.activate_snapshot(
            entity_id=entity.id,
            snapshot_id=snapshot.id,
            version=version,
        )
        return PublicationResult(version=version, public_id=params.public_id)
```

Mapping persisted snapshots back to domain/public DTOs is a boundary with an
explicit failure mode. Missing required keys, unknown enum values, or invalid
types raise a domain error such as `MalformedSnapshotError`; do not silently drop
fields or return a partial public response.

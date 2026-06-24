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

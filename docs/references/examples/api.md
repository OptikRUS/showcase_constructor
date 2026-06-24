# Reference: API Layer

## src/api/boundary.py — Base Pydantic models

```python
from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel, to_snake


class BoundaryModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        from_attributes=True,
        populate_by_name=True,
    )


class SnakeBoundaryModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_snake,
        from_attributes=True,
        populate_by_name=True,
    )
```

## src/api/\<domain\>/schemas.py

```python
from decimal import Decimal

from src.api.boundary import SnakeBoundaryModel
from src.core.entities.enums import EntityStatusEnum
from src.core.entities.schemas import Entity, EntityParams


class EntityResponse(SnakeBoundaryModel):
    id: int
    name: str
    amount: Decimal
    status: EntityStatusEnum

    @classmethod
    def from_domain(cls, entity: Entity) -> "EntityResponse":
        return cls(id=entity.id, name=entity.name, amount=entity.amount, status=entity.status)


class CreateEntityRequest(SnakeBoundaryModel):
    name: str
    amount: str
    status: EntityStatusEnum

    def to_domain(self) -> EntityParams:
        return EntityParams(name=self.name, amount=Decimal(self.amount), status=self.status)
```

## src/api/common/endpoints.py — Health route

```python
from fastapi import APIRouter, Response, status

router = APIRouter(prefix="", tags=["default"])


@router.get(path="/health")
async def health() -> Response:
    return Response(status_code=status.HTTP_200_OK)
```

Redirect from `/` to `/docs` is optional and only makes sense when FastAPI docs are enabled.
The current project disables `docs_url`, `openapi_url`, and `redoc_url` in `create_app()`, so
`/health` is the only required common endpoint.

## src/api/routers.py — Root router composition

```python
from fastapi import APIRouter

from src.api.common import endpoints as common
from src.api.entities import endpoints as entities

root_router = APIRouter()
root_router.include_router(common.router, include_in_schema=False)
root_router.include_router(entities.router)
```

Все domain/common routers регистрируются в `src/api/routers.py`. Не дублировать
`include_router(...)` для feature routers в `create_app()`.

Запрещённый вариант:

```python
def create_app(
    lifespan: Lifespan | None = None,
) -> FastAPI:
    app = FastAPI(lifespan=lifespan)
    app.include_router(common_router)
    app.include_router(reservations_router)
    setup_exception_handlers(app=app)
    return app
```

## src/api/exceptions.py — Exception handlers

```python
from collections.abc import Callable, Coroutine
from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse, Response

from src.core.exceptions import BaseExceptionError
from src.core.<domain>.exceptions import EntityNotFoundError

ExceptionHandler = Callable[[Request, Any], Coroutine[Any, Any, Response]]
ExceptionHandlers = dict[int | type[Exception], ExceptionHandler]


async def internal_server_error_exception_handler(_: Request, _exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "INTERNAL SERVER ERROR"},
    )


def handler(status_code: int, message: str | None = None) -> ExceptionHandler:
    async def error(_: Request, exc: BaseExceptionError) -> JSONResponse:
        detail = message or (exc.detail if hasattr(exc, "detail") else str(exc))
        return JSONResponse(status_code=status_code, content={"detail": detail})

    return error


exception_handlers: ExceptionHandlers = {
    status.HTTP_500_INTERNAL_SERVER_ERROR: internal_server_error_exception_handler,
    EntityNotFoundError: handler(status_code=status.HTTP_404_NOT_FOUND),
}


def setup_exception_handlers(app: FastAPI) -> None:
    for exc_type, exc_handler in exception_handlers.items():
        app.add_exception_handler(exc_type, exc_handler)
```

Ключевые правила:
- `ExceptionHandler`/`ExceptionHandlers` — type aliases для ясности типов.
- `handler()` — generic factory; не создавать именованный хендлер на каждое исключение.
- `exception_handlers` dict — единая точка регистрации всех хендлеров.
- `setup_exception_handlers` итерирует dict и регистрирует через `app.add_exception_handler`.
- Не проверять `isinstance` внутри хендлера — FastAPI уже роутит по типу.
- Параметр request именуется `_` если не используется.

## src/api/app.py — FastAPI app factory

```python
from collections.abc import Callable
from contextlib import AbstractAsyncContextManager

from fastapi import FastAPI

from src.api.exceptions import setup_exception_handlers
from src.api.routers import root_router

Lifespan = Callable[[FastAPI], AbstractAsyncContextManager[None]]


def create_app(
    lifespan: Lifespan | None = None,
) -> FastAPI:
    app = FastAPI(lifespan=lifespan)
    app.include_router(root_router)
    setup_exception_handlers(app=app)
    return app
```

## src/api/\<domain\>/endpoints.py

```python
from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, status

from src.api.entities.schemas import CreateEntityRequest, EntityResponse
from src.core.entities.use_cases import CreateEntityUseCase, GetEntityUseCase


router = APIRouter(prefix="/entities", tags=["entities"], route_class=DishkaRoute)


@router.get("/{entity_id}", status_code=status.HTTP_200_OK)
async def get_entity(
    entity_id: int,
    use_case: FromDishka[GetEntityUseCase],
) -> EntityResponse:
    entity = await use_case.execute(entity_id=entity_id)
    return EntityResponse.from_domain(entity=entity)


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_entity(
    body: CreateEntityRequest,
    use_case: FromDishka[CreateEntityUseCase],
) -> EntityResponse:
    entity = await use_case.execute(params=body.to_domain())
    return EntityResponse.from_domain(entity=entity)
```

## Endpoint с server-generated UUID (создание сущности с UUID primary key)

Паттерн применяется когда ID сущности генерируется на сервере. UUID инжектируется через
`FromDishka[UUID]` (из `GeneralProvider`) и передаётся в `to_domain()`.

Схема запроса (`src/api/<domain>/schemas.py`):

```python
from uuid import UUID

from src.api.boundary import SnakeBoundaryModel
from src.core.entities.schemas import Entity


class CreateEntityRequest(SnakeBoundaryModel):
    field_a: str
    field_b: int

    def to_domain(self, uuid_id: UUID) -> Entity:
        return Entity(
            id=uuid_id.hex,
            field_a=self.field_a,
            field_b=self.field_b,
        )
```

Endpoint (`src/api/<domain>/endpoints.py`):

```python
from uuid import UUID

from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, status

from src.api.entities.schemas import CreateEntityRequest, EntityResponse
from src.core.entities.use_cases import CreateEntityUseCase

router = APIRouter(prefix="/entities", tags=["entities"], route_class=DishkaRoute)


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_entity(
    body: CreateEntityRequest,
    uuid_id: FromDishka[UUID],
    use_case: FromDishka[CreateEntityUseCase],
) -> EntityResponse:
    entity = await use_case.execute(entity=body.to_domain(uuid_id=uuid_id))
    return EntityResponse.from_domain(entity=entity)
```

Требует: `GeneralProvider` в `src/di/providers/general.py` и `MockGeneralProvider` в тестах
(см. `docs/references/examples/di.md`).

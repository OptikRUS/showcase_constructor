# Reference: DI Providers

## src/di/providers/database.py

```python
from collections.abc import AsyncIterator

from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.storages import EntityStorage
from src.storages.database import async_session
from src.storages.database_storage import DatabaseEntityStorage


class DatabaseProvider(Provider):
    @provide(scope=Scope.REQUEST)
    async def get_db_session(self) -> AsyncIterator[AsyncSession]:
        async with async_session() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    @provide(scope=Scope.REQUEST)
    def get_entity_storage(self, session: AsyncSession) -> EntityStorage:
        return DatabaseEntityStorage(session=session)
```

## src/di/providers/general.py — UUID и другие инфраструктурные зависимости

```python
from uuid import UUID, uuid4

from dishka import Provider, Scope, provide


class GeneralProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def get_uuid(self) -> UUID:
        return uuid4()
```

Использовать `GeneralProvider` когда endpoint или use case требует server-generated значение
(UUID, datetime, random seed). Каждый тип — отдельный `@provide`-метод в этом провайдере.

## src/di/container.py

```python
from dishka import AsyncContainer, make_async_container

from src.di.providers.database import DatabaseProvider
from src.di.providers.general import GeneralProvider
from src.di.providers.use_cases import UseCaseProvider


def create_container() -> AsyncContainer:
    return make_async_container(
        DatabaseProvider(),
        GeneralProvider(),
        UseCaseProvider(),
    )
```

## Notes

- `Scope.REQUEST` для use cases, storages, clients, services по умолчанию.
- `Scope.APP` + `AsyncMock(spec=UseCaseClass)` для тестовых мок-провайдеров.
- FastAPI интеграция: `setup_dishka_fastapi(container=container, app=app)` + `DishkaRoute`.
- FastStream интеграция: `setup_dishka_faststream(container=container, broker=broker)`.
- `GeneralProvider` включать в контейнер всегда если хоть один endpoint использует server-generated UUID.

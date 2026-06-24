# Reference: Tests Infrastructure

## Обязательные правила

- Общие pytest fixtures живут в `src/tests/conftest.py`; не объявлять `client`, `app`,
  `container`, `session`, `engine`, storage fixtures и migrations setup внутри файлов тестов слоя.
- Fixture mixins живут в `src/tests/fixtures.py`; тестовые классы наследуют только нужные mixins.
- `src/tests/helpers/` обязателен: API calls — в `api.py`, domain builders — в `factory.py`,
  DB setup/readback — в `storage.py`, use case mock access — в `use_case.py`.
- Domain schemas, params и ожидаемые domain-объекты создаются через `FactoryHelper`.
  Не создавать domain dataclass руками в тестах, если для него есть или должен быть factory-метод.
- Storage/API setup и readback выполняются через helpers. Прямой SQL/HTTP внутри теста допускается
  только для проверки низкоуровневого контракта, где helper скрыл бы проверяемое поведение.
- Один test-файл слоя содержит тестовые классы и assertions; инфраструктура выносится в
  `conftest.py`, `fixtures.py`, `helpers/`, `mocks/`.
- Не создавать `src/tests/config/`, `src/tests/di/` или `src/tests/migrations/` для
  unit-тестов infrastructure mechanics. Settings, DI и Alembic wiring проверяются
  через shared fixtures, API/storage integration tests и migration smoke в
  `src/tests/storages/`.
- Если нужного `conftest.py`, `fixtures.py` или helper ещё нет, сначала создать/расширить эту
  инфраструктуру по этому reference, затем писать API/Core/Storage tests.
- Запрещено переносить fixtures в `src/tests/api/*`, `src/tests/core/*`, `src/tests/storages/*`
  из-за отсутствующего helper или conftest setup.

## src/tests/conftest.py — Полный шаблон

```python
from collections.abc import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from dishka import AsyncContainer, make_async_container
from dishka.integrations.fastapi import FastapiProvider
from dishka.integrations.fastapi import setup_dishka as setup_dishka_fastapi
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import NullPool, delete
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine

from src.api.app import create_app
from src.api.auth.deps import access_security
from src.config.settings import settings
from src.migrations.commands import downgrade, migrate
from src.storages.database import async_session
from src.storages.models import EntityModel
from src.tests.mocks.providers import MockGeneralProvider, MockUseCaseProvider


@pytest.fixture(scope="session", autouse=True)
def setup_migrations() -> Generator[None]:
    migrate(revision="heads", db_url=settings.DATABASE.URL.get_secret_value())
    yield
    downgrade(revision="base", db_url=settings.DATABASE.URL.get_secret_value())


@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def engine() -> AsyncGenerator[AsyncEngine]:
    engine = create_async_engine(settings.DATABASE.URL.get_secret_value(), poolclass=NullPool)
    yield engine
    await engine.dispose()


@pytest.fixture
async def clear_tables(engine: AsyncEngine) -> None:
    async with engine.begin() as conn:
        await conn.execute(delete(EntityModel))


@pytest.fixture
async def session(engine: AsyncEngine, clear_tables: None) -> AsyncGenerator:
    _ = clear_tables
    async with async_session(bind=engine) as db:
        yield db
        await db.commit()


@pytest.fixture
async def container() -> AsyncGenerator[AsyncContainer]:
    container = make_async_container(
        FastapiProvider(),
        MockGeneralProvider(),
        MockUseCaseProvider(),
    )
    yield container
    await container.close()


@pytest.fixture
def app(container: AsyncContainer) -> FastAPI:
    application = create_app()
    setup_dishka_fastapi(container=container, app=application)
    return application


@pytest.fixture
def no_auth_client(app: FastAPI) -> Generator[TestClient]:
    with TestClient(app) as client:
        yield client


@pytest.fixture
def client(app: FastAPI) -> Generator[TestClient]:
    token = access_security.create_access_token(
        subject={
            "user_id": "admin-user-1",
            "partner_id": "partner-1",
        },
    )
    with TestClient(app, headers={"Authorization": f"Bearer {token}"}) as client:
        yield client
```

## src/tests/fixtures.py — Fixture mixin классы

```python
import pytest
from dishka import AsyncContainer
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.tests.helpers.api import APIHelper
from src.tests.helpers.factory import FactoryHelper
from src.tests.helpers.storage import StorageHelper
from src.tests.helpers.use_case import ContainerHelper


class APIFixture:
    api: APIHelper
    no_auth_api: APIHelper

    @pytest.fixture(autouse=True)
    def _api_setup(
        self,
        app: FastAPI,
        client: TestClient,
        no_auth_client: TestClient,
    ) -> None:
        _ = app
        self.api = APIHelper(client=client)
        self.no_auth_api = APIHelper(client=no_auth_client)


class FactoryFixture:
    factory: FactoryHelper

    @pytest.fixture(autouse=True)
    def fixture_setup_factory(self) -> None:
        self.factory = FactoryHelper()


class StorageFixture:
    storage_helper: StorageHelper

    @pytest.fixture(autouse=True)
    def _storage_setup(self, session: AsyncSession) -> None:
        self.storage_helper = StorageHelper(session=session)


class ContainerFixture:
    container: ContainerHelper

    @pytest.fixture(autouse=True)
    def _setup_app(self, container: AsyncContainer) -> None:
        self.container = ContainerHelper(container=container)


```

## src/tests/helpers/api.py

```python
from dataclasses import dataclass

from httpx2 import Response
from starlette.testclient import TestClient


@dataclass(kw_only=True, slots=True)
class APIHelper:
    client: TestClient

    def get_health(self) -> Response:
        return self.client.get("/health")

    def get_entity(self, entity_id: int) -> Response:
        return self.client.get(f"/entities/{entity_id}")

    def create_entity(self, name: str, amount: str, status: str = "active") -> Response:
        return self.client.post(
            "/entities",
            json={"name": name, "amount": amount, "status": status},
        )
```

Protected API tests use `self.api`; unauthenticated scenarios use a separate
`Test*NoAuthAPI` class and `self.no_auth_api`.

```python
from httpx2 import codes

from src.tests.fixtures import APIFixture


class TestEntityNoAuthAPI(APIFixture):
    def test_unauthorized(self) -> None:
        response = self.no_auth_api.get_entity(entity_id=1)

        assert response.status_code == codes.UNAUTHORIZED
```

## src/tests/helpers/factory.py

```python
from decimal import Decimal

from src.core.entities.enums import EntityStatusEnum
from src.core.entities.schemas import Entity, EntityParams


class FactoryHelper:
    @classmethod
    def entity(
        cls,
        entity_id: int = 1,
        name: str = "Test Entity",
        amount: str = "100.00",
        status: EntityStatusEnum = EntityStatusEnum.ACTIVE,
    ) -> Entity:
        return Entity(
            id=entity_id,
            name=name,
            amount=Decimal(amount),
            status=status,
        )

    @classmethod
    def entity_params(
        cls,
        name: str = "Test Entity",
        amount: str = "100.00",
        status: EntityStatusEnum = EntityStatusEnum.ACTIVE,
    ) -> EntityParams:
        return EntityParams(name=name, amount=Decimal(amount), status=status)
```

## src/tests/helpers/storage.py

```python
from dataclasses import dataclass

from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.entities.schemas import Entity
from src.storages.models import EntityModel


@dataclass(kw_only=True, slots=True)
class StorageHelper:
    session: AsyncSession

    async def insert_entity(self, entity: Entity) -> None:
        await self.session.execute(
            insert(EntityModel).values(
                id=entity.id,
                name=entity.name,
                amount=entity.amount,
                status=entity.status.value,
            )
        )

    async def get_entity_by_id(self, entity_id: int) -> EntityModel | None:
        return await self.session.scalar(
            select(EntityModel).where(EntityModel.id == entity_id)
        )
```

## src/tests/helpers/use_case.py

```python
from dataclasses import dataclass
from typing import cast
from unittest.mock import AsyncMock

from dishka import AsyncContainer

from src.core.use_case import UseCase


@dataclass(kw_only=True)
class ContainerHelper:
    container: AsyncContainer

    async def override_use_case(self, use_case: type[UseCase]) -> AsyncMock:
        mocked_use_case = await self.container.get(use_case)
        return cast("AsyncMock", mocked_use_case)
```

## src/tests/helpers/kafka.py

```python
from dataclasses import dataclass
from typing import Any

from faststream.kafka.fastapi import KafkaBroker


@dataclass
class KafkaHelper:
    broker: KafkaBroker

    @classmethod
    def assert_called_once(cls, called: Any) -> None:  # noqa: ANN401
        called.mock.assert_called_once()

    @classmethod
    def assert_called_once_with(cls, called: Any, message: dict[str, Any]) -> None:  # noqa: ANN401
        called.mock.assert_called_once_with(message)

    @classmethod
    def reset_mock(cls, called: Any) -> None:  # noqa: ANN401
        called.mock.reset_mock()
```

## src/tests/mocks/providers.py

```python
from unittest.mock import AsyncMock
from uuid import UUID

from dishka import Provider, Scope, provide

from src.core.entities.use_cases import CreateEntityUseCase, GetEntityUseCase


class MockUseCaseProvider(Provider):
    @provide(scope=Scope.APP)
    def get_entity_use_case(self) -> GetEntityUseCase:
        return AsyncMock(spec=GetEntityUseCase)

    @provide(scope=Scope.APP)
    def create_entity_use_case(self) -> CreateEntityUseCase:
        return AsyncMock(spec=CreateEntityUseCase)


class MockGeneralProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def get_uuid(self) -> UUID:
        return UUID(hex="00000000000000000000000000000001")
```

`MockGeneralProvider` должен зеркалить `GeneralProvider`: каждый `@provide`-метод из продакшн
провайдера получает детерминированный аналог (фиксированный UUID, фиксированный datetime и т.д.).
Если проект не использует UUID-инъекцию — `MockGeneralProvider` не добавлять в тестовый контейнер.

---

## Примеры тестов

### Core use case test (src/tests/core/\<domain\>/test_get_entity_use_case.py)

```python
from unittest.mock import AsyncMock

import pytest

from src.core.entities.exceptions import EntityNotFoundError
from src.core.entities.use_cases import GetEntityUseCase
from src.core.storages import EntityStorage
from src.tests.fixtures import FactoryFixture


class TestGetEntityUseCase(FactoryFixture):
    @pytest.fixture(autouse=True)
    async def setup(self) -> None:
        self.mock_storage = AsyncMock(spec=EntityStorage)
        self.use_case = GetEntityUseCase(storage=self.mock_storage)

    async def test_success(self) -> None:
        self.mock_storage.get_by_id.return_value = self.factory.entity(entity_id=1)

        result = await self.use_case.execute(entity_id=1)

        assert result == self.factory.entity(entity_id=1)
        self.mock_storage.get_by_id.assert_awaited_once_with(entity_id=1)

    async def test_not_found(self) -> None:
        self.mock_storage.get_by_id.side_effect = EntityNotFoundError

        with pytest.raises(EntityNotFoundError):
            await self.use_case.execute(entity_id=999)

        self.mock_storage.get_by_id.assert_awaited_once_with(entity_id=999)
```

### Storage test (src/tests/storages/test_entity_storage.py)

```python
import pytest

from src.core.entities.exceptions import EntityNotFoundError
from src.storages.database_storage import DatabaseEntityStorage
from src.tests.fixtures import FactoryFixture, StorageFixture
from sqlalchemy.ext.asyncio import AsyncSession


class TestDatabaseEntityStorage(FactoryFixture, StorageFixture):
    @pytest.fixture(autouse=True)
    def _storage(self, session: AsyncSession) -> None:
        self.storage = DatabaseEntityStorage(session=session)

    async def test_get_by_id_success(self) -> None:
        await self.storage_helper.insert_entity(entity=self.factory.entity(entity_id=1))

        result = await self.storage.get_by_id(entity_id=1)

        assert result == self.factory.entity(entity_id=1)

    async def test_get_by_id_not_found(self) -> None:
        with pytest.raises(EntityNotFoundError):
            await self.storage.get_by_id(entity_id=999)
```

### Migration smoke test (src/tests/storages/test_database_migrations.py)

```python
from src.tests.fixtures import StorageFixture


class TestDatabaseMigrations(StorageFixture):
    async def test_upgrades_to_head_revision(self) -> None:
        version = await self.storage_helper.get_current_alembic_version()

        assert version == "0001"
```

### API test (src/tests/api/test_health.py)

```python
from httpx2 import codes

from src.tests.fixtures import APIFixture


class TestHealthAPI(APIFixture):
    def test_health(self) -> None:
        response = self.api.get_health()

        assert response.is_success
        assert response.status_code == codes.OK
```

### API endpoint test с use case mock (src/tests/api/test_entities.py)

```python
from httpx2 import codes

import pytest

from src.tests.fixtures import APIFixture, ContainerFixture, FactoryFixture
from src.core.entities.use_cases import GetEntityUseCase


class TestGetEntityAPI(APIFixture, ContainerFixture, FactoryFixture):
    @pytest.fixture(autouse=True)
    async def setup(self) -> None:
        self.use_case = await self.container.override_use_case(GetEntityUseCase)

    async def test_get_entity_success(self) -> None:
        self.use_case.execute.return_value = self.factory.entity(entity_id=1)

        response = self.api.get_entity(entity_id=1)

        assert response.status_code == codes.OK
        self.use_case.execute.assert_awaited_once_with(entity_id=1)
```

Use case инициализируется в `autouse` setup-фикстуре как `self.use_case`. Это позволяет
настраивать `return_value`/`side_effect` в каждом тесте без повторного вызова `override_use_case`.

API tests не создают `AsyncClient`, `FastAPI app`, Dishka container или mock providers локально.
Эти фикстуры берутся из `conftest.py`, HTTP-вызовы идут через `APIHelper`, use case mock — через
`ContainerHelper.override_use_case(...)`.

Запрещённые локальные замены:

```python
@pytest.fixture
def app() -> FastAPI:
    return create_app()


@pytest.fixture
async def session() -> AsyncGenerator[AsyncSession]:
    async with async_session() as db:
        yield db


class TestEntityAPI:
    async def test_success(self) -> None:
        async with AsyncClient(app=create_app(), base_url="http://test") as client:
            response = await client.get("/entities/1")

        assert response.status_code == codes.OK
```

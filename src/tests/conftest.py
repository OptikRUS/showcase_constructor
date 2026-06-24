from collections.abc import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from dishka import AsyncContainer
from dishka.integrations.fastapi import setup_dishka as setup_dishka_fastapi
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine

from src.api.app import create_app
from src.api.auth.deps import access_security
from src.config.settings import settings
from src.di.container import create_container
from src.migrations.commands import downgrade, migrate
from src.storages.database import async_session


@pytest.fixture(scope="session", autouse=True)
def setup_migrations() -> Generator[None]:
    migrate(revision="heads", db_url=settings.DATABASE.URL.get_secret_value())
    yield
    downgrade(revision="base", db_url=settings.DATABASE.URL.get_secret_value())


@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def engine() -> AsyncGenerator[AsyncEngine]:
    test_engine = create_async_engine(settings.DATABASE.URL.get_secret_value(), poolclass=NullPool)
    yield test_engine
    await test_engine.dispose()


@pytest_asyncio.fixture
async def session(engine: AsyncEngine) -> AsyncGenerator[AsyncSession]:
    async with async_session(bind=engine) as db_session:
        try:
            yield db_session
            await db_session.commit()
        except Exception:
            await db_session.rollback()
            raise


@pytest.fixture
async def container() -> AsyncGenerator[AsyncContainer]:
    container = create_container()
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

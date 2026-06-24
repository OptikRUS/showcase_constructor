from collections.abc import AsyncGenerator, Generator

import pytest
from dishka import AsyncContainer
from dishka.integrations.fastapi import setup_dishka as setup_dishka_fastapi
from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.api.app import create_app
from src.di.container import create_container


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

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.tests.helpers.api import APIHelper
from src.tests.helpers.factory import FactoryHelper
from src.tests.helpers.storage import StorageHelper


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

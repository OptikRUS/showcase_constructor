import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.tests.helpers.api import APIHelper
from src.tests.helpers.factory import FactoryHelper


class APIFixture:
    api: APIHelper

    @pytest.fixture(autouse=True)
    def _api_setup(self, app: FastAPI, no_auth_client: TestClient) -> None:
        _ = app
        self.api = APIHelper(client=no_auth_client)


class FactoryFixture:
    factory: FactoryHelper

    @pytest.fixture(autouse=True)
    def fixture_setup_factory(self) -> None:
        self.factory = FactoryHelper()

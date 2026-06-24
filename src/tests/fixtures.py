import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.tests.helpers.api import APIHelper


class APIFixture:
    api: APIHelper

    @pytest.fixture(autouse=True)
    def _api_setup(self, app: FastAPI, no_auth_client: TestClient) -> None:
        _ = app
        self.api = APIHelper(client=no_auth_client)

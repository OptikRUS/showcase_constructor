from dataclasses import dataclass

from httpx2 import Response
from starlette.testclient import TestClient


@dataclass(kw_only=True, slots=True)
class APIHelper:
    client: TestClient

    def get_health(self) -> Response:
        return self.client.get("/health")

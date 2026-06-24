from collections.abc import Mapping
from dataclasses import dataclass

from httpx2 import Response
from starlette.testclient import TestClient


@dataclass(kw_only=True, slots=True)
class APIHelper:
    client: TestClient

    def get_health(self) -> Response:
        return self.client.get("/health")

    def get_public_config(self, public_id: str) -> Response:
        return self.client.get(f"/api/v1/public/showcases/{public_id}")

    def get_admin_auth_context(self, headers: Mapping[str, str] | None = None) -> Response:
        return self.client.get("/api/v1/admin/auth/context", headers=headers)

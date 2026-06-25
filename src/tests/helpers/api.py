from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from httpx2 import Response
from starlette.testclient import TestClient


@dataclass(kw_only=True, slots=True)
class APIHelper:
    client: TestClient

    def get_health(self) -> Response:
        return self.client.get("/health")

    def get_swagger_docs(self) -> Response:
        return self.client.get("/docs")

    def get_openapi_schema(self) -> Response:
        return self.client.get("/openapi.json")

    def get_public_config(self, public_id: str) -> Response:
        return self.client.get(f"/api/v1/public/showcases/{public_id}")

    def get_admin_auth_context(self, headers: Mapping[str, str] | None = None) -> Response:
        return self.client.get("/api/v1/admin/auth/context", headers=headers)

    def patch_admin_showcase_draft_settings(
        self,
        *,
        showcase_id: str,
        json: Mapping[str, Any],
    ) -> Response:
        return self.client.patch(f"/api/v1/showcases/{showcase_id}", json=json)

    def preview_admin_showcase(
        self,
        *,
        showcase_id: str,
        json: Mapping[str, Any],
    ) -> Response:
        return self.client.post(f"/api/v1/showcases/{showcase_id}/preview", json=json)

    def publish_admin_showcase(self, *, showcase_id: str) -> Response:
        return self.client.post(f"/api/v1/showcases/{showcase_id}/publish")

    def unpublish_admin_showcase(self, *, showcase_id: str) -> Response:
        return self.client.post(f"/api/v1/showcases/{showcase_id}/unpublish")

    def list_admin_showcase_blocks(self, *, showcase_id: str) -> Response:
        return self.client.get(f"/api/v1/showcases/{showcase_id}/blocks")

    def create_admin_showcase_block(
        self,
        *,
        showcase_id: str,
        json: Mapping[str, Any],
    ) -> Response:
        return self.client.post(f"/api/v1/showcases/{showcase_id}/blocks", json=json)

    def patch_admin_showcase_block(
        self,
        *,
        showcase_id: str,
        block_id: str,
        json: Mapping[str, Any],
    ) -> Response:
        return self.client.patch(
            f"/api/v1/showcases/{showcase_id}/blocks/{block_id}",
            json=json,
        )

    def delete_admin_showcase_block(
        self,
        *,
        showcase_id: str,
        block_id: str,
    ) -> Response:
        return self.client.delete(f"/api/v1/showcases/{showcase_id}/blocks/{block_id}")

    def list_admin_showcase_offers(self, *, showcase_id: str) -> Response:
        return self.client.get(f"/api/v1/showcases/{showcase_id}/offers")

    def create_admin_showcase_offer(
        self,
        *,
        showcase_id: str,
        json: Mapping[str, Any],
    ) -> Response:
        return self.client.post(f"/api/v1/showcases/{showcase_id}/offers", json=json)

    def patch_admin_showcase_offer(
        self,
        *,
        showcase_id: str,
        offer_id: str,
        json: Mapping[str, Any],
    ) -> Response:
        return self.client.patch(
            f"/api/v1/showcases/{showcase_id}/offers/{offer_id}",
            json=json,
        )

    def delete_admin_showcase_offer(
        self,
        *,
        showcase_id: str,
        offer_id: str,
    ) -> Response:
        return self.client.delete(f"/api/v1/showcases/{showcase_id}/offers/{offer_id}")

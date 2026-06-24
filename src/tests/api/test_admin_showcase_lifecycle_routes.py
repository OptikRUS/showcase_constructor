import pytest
from httpx2 import codes

from src.tests.fixtures import APIFixture


class TestAdminShowcaseLifecycleRouteExposure(APIFixture):
    @pytest.mark.parametrize(
        ("method", "path", "json_body"),
        [
            ("POST", "/api/v1/showcases", {"title": "Draft showcase"}),
            ("GET", "/api/v1/showcases", None),
            ("GET", "/api/v1/showcases/showcase-1", None),
            ("PATCH", "/api/v1/showcases/showcase-1", {"title": "Updated draft"}),
            ("POST", "/api/v1/showcases/showcase-1/clone", None),
            ("POST", "/api/v1/showcases/showcase-1/archive", None),
            ("POST", "/api/v1/showcases/showcase-1/restore", None),
        ],
    )
    def test_admin_lifecycle_routes_are_not_registered_without_decisions(
        self,
        method: str,
        path: str,
        json_body: dict[str, str] | None,
    ) -> None:
        response = self.api.client.request(method=method, url=path, json=json_body)

        assert response.status_code == codes.NOT_FOUND

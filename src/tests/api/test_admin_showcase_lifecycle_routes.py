import pytest
from httpx2 import codes

from src.tests.fixtures import APIFixture


class TestAdminShowcaseLifecycleRouteExposure(APIFixture):
    @pytest.mark.parametrize(
        ("method", "path"),
        [
            ("HEAD", "/api/v1/showcases"),
            ("OPTIONS", "/api/v1/showcases"),
            ("HEAD", "/api/v1/showcases/showcase-1"),
            ("OPTIONS", "/api/v1/showcases/showcase-1"),
            ("POST", "/api/v1/showcases/showcase-1/unarchive"),
        ],
    )
    def test_blocked_admin_lifecycle_methods_or_aliases_are_not_exposed(
        self,
        method: str,
        path: str,
    ) -> None:
        response = self.api.client.request(method=method, url=path)

        assert response.status_code in {codes.NOT_FOUND, codes.METHOD_NOT_ALLOWED}

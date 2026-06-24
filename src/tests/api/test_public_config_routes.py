import pytest
from httpx2 import codes

from src.tests.fixtures import APIFixture


class TestPublicConfigRouteExposure(APIFixture):
    @pytest.mark.parametrize("method", ["HEAD", "OPTIONS", "POST", "PATCH", "DELETE"])
    def test_unsupported_public_showcase_methods_are_not_exposed(self, method: str) -> None:
        response = self.api.client.request(
            method=method,
            url="/api/v1/public/showcases/example",
        )

        assert response.status_code in {codes.NOT_FOUND, codes.METHOD_NOT_ALLOWED}

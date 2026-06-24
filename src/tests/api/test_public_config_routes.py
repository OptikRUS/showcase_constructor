from httpx2 import codes

from src.tests.fixtures import APIFixture


class TestPublicConfigRouteExposure(APIFixture):
    def test_public_config_route_is_not_registered_without_decision(self) -> None:
        response = self.api.get_public_config(public_id="example")

        assert response.status_code == codes.NOT_FOUND

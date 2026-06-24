from httpx2 import codes

from src.tests.fixtures import APIFixture


class TestHealthAPI(APIFixture):
    def test_health(self) -> None:
        response = self.api.get_health()

        assert response.is_success
        assert response.status_code == codes.OK

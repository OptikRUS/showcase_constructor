import pytest
from httpx2 import codes

from src.tests.fixtures import APIFixture


class TestAdminAuthContextAPI(APIFixture):
    def test_missing_context_returns_unauthorized(self) -> None:
        response = self.api.get_admin_auth_context()

        assert response.status_code == codes.UNAUTHORIZED
        assert response.json() == {"detail": "ADMIN_AUTHENTICATION_REQUIRED_ERROR"}

    @pytest.mark.parametrize(
        "headers",
        [
            {"X-Admin-User-Id": "admin-user-1"},
            {"X-Partner-Id": "partner-1"},
            {"X-Admin-User-Id": "", "X-Partner-Id": "partner-1"},
            {"X-Admin-User-Id": "admin-user-1", "X-Partner-Id": ""},
            {"X-Admin-User-Id": "   ", "X-Partner-Id": "partner-1"},
            {"X-Admin-User-Id": "admin-user-1", "X-Partner-Id": "   "},
        ],
    )
    def test_incomplete_or_blank_context_returns_unauthorized(
        self,
        headers: dict[str, str],
    ) -> None:
        response = self.api.get_admin_auth_context(headers=headers)

        assert response.status_code == codes.UNAUTHORIZED
        assert response.json() == {"detail": "ADMIN_AUTHENTICATION_REQUIRED_ERROR"}

    def test_valid_context_returns_admin_identifiers(self) -> None:
        response = self.api.get_admin_auth_context(
            headers={
                "X-Admin-User-Id": "admin-user-1",
                "X-Partner-Id": "partner-1",
            },
        )

        assert response.status_code == codes.OK
        assert response.json() == {
            "userId": "admin-user-1",
            "partnerId": "partner-1",
        }

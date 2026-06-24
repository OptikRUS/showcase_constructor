import pytest
from httpx2 import codes

from src.api.auth.deps import access_security
from src.tests.fixtures import APIFixture


class TestAdminAuthContextAPI(APIFixture):
    def _auth_headers(self, *, subject: dict[str, str]) -> dict[str, str]:
        return {"Authorization": f"Bearer {access_security.create_access_token(subject=subject)}"}

    def test_missing_context_returns_unauthorized(self) -> None:
        response = self.api.get_admin_auth_context()

        assert response.status_code == codes.UNAUTHORIZED
        assert response.json() == {"detail": "ADMIN_AUTHENTICATION_REQUIRED_ERROR"}

    @pytest.mark.parametrize(
        "headers",
        [
            {"Authorization": "Bearer"},
            {"Authorization": "Bearer invalid-token"},
        ],
    )
    def test_invalid_bearer_context_returns_unauthorized(
        self,
        headers: dict[str, str],
    ) -> None:
        response = self.api.get_admin_auth_context(headers=headers)

        assert response.status_code == codes.UNAUTHORIZED
        assert response.json() == {"detail": "ADMIN_AUTHENTICATION_REQUIRED_ERROR"}

    @pytest.mark.parametrize(
        "subject",
        [
            {"user_id": "admin-user-1"},
            {"partner_id": "partner-1"},
            {"user_id": "", "partner_id": "partner-1"},
            {"user_id": "admin-user-1", "partner_id": ""},
            {"user_id": "   ", "partner_id": "partner-1"},
            {"user_id": "admin-user-1", "partner_id": "   "},
        ],
    )
    def test_incomplete_or_blank_token_subject_returns_unauthorized(
        self,
        subject: dict[str, str],
    ) -> None:
        response = self.api.get_admin_auth_context(headers=self._auth_headers(subject=subject))

        assert response.status_code == codes.UNAUTHORIZED
        assert response.json() == {"detail": "ADMIN_AUTHENTICATION_REQUIRED_ERROR"}

    def test_temporary_request_headers_do_not_authenticate(self) -> None:
        response = self.api.get_admin_auth_context(
            headers={
                "X-Admin-User-Id": "admin-user-1",
                "X-Partner-Id": "partner-1",
            },
        )

        assert response.status_code == codes.UNAUTHORIZED
        assert response.json() == {"detail": "ADMIN_AUTHENTICATION_REQUIRED_ERROR"}

    def test_valid_context_returns_admin_identifiers(self) -> None:
        response = self.api.get_admin_auth_context(
            headers=self._auth_headers(
                subject={
                    "user_id": "admin-user-1",
                    "partner_id": "partner-1",
                },
            ),
        )

        assert response.status_code == codes.OK
        assert response.json() == {
            "userId": "admin-user-1",
            "partnerId": "partner-1",
        }

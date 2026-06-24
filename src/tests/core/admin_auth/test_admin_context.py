import pytest

from src.core.admin_auth.exceptions import (
    AdminAuthenticationRequiredError,
    AdminPermissionDeniedError,
    AdminResourceNotFoundError,
)
from src.core.admin_auth.schemas import AdminActorContext
from src.core.exceptions import BaseExceptionError


class TestAdminActorContext:
    @pytest.mark.parametrize(
        ("user_id", "partner_id"),
        [
            (None, "partner-1"),
            ("admin-user-1", None),
            ("", "partner-1"),
            ("admin-user-1", ""),
            ("   ", "partner-1"),
            ("admin-user-1", "   "),
        ],
    )
    def test_rejects_blank_required_ids(
        self,
        user_id: str | None,
        partner_id: str | None,
    ) -> None:
        with pytest.raises(AdminAuthenticationRequiredError) as error:
            AdminActorContext.from_raw(user_id=user_id, partner_id=partner_id)

        assert error.value.detail == "ADMIN_AUTHENTICATION_REQUIRED_ERROR"

    def test_creates_context_from_valid_ids(self) -> None:
        context = AdminActorContext.from_raw(
            user_id=" admin-user-1 ",
            partner_id=" partner-1 ",
        )

        assert context == AdminActorContext(
            user_id="admin-user-1",
            partner_id="partner-1",
        )

    @pytest.mark.parametrize(
        ("exception_type", "detail"),
        [
            (AdminAuthenticationRequiredError, "ADMIN_AUTHENTICATION_REQUIRED_ERROR"),
            (AdminPermissionDeniedError, "ADMIN_PERMISSION_DENIED_ERROR"),
            (AdminResourceNotFoundError, "ADMIN_RESOURCE_NOT_FOUND_ERROR"),
        ],
    )
    def test_exceptions_have_stable_details(
        self,
        exception_type: type[BaseExceptionError],
        detail: str,
    ) -> None:
        exception = exception_type()

        assert exception.detail == detail
        assert str(exception) == detail

import pytest

from src.core.admin_auth.exceptions import (
    AdminAuthenticationRequiredError,
    AdminPermissionDeniedError,
    AdminResourceNotFoundError,
)
from src.core.admin_auth.schemas import AdminActorContext
from src.core.exceptions import BaseExceptionError


class TestAdminActorContext:
    def test_preserves_already_validated_identifiers(self) -> None:
        context = AdminActorContext(
            user_id=" admin-user-1 ",
            partner_id=" partner-1 ",
        )

        assert context.user_id == " admin-user-1 "
        assert context.partner_id == " partner-1 "

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

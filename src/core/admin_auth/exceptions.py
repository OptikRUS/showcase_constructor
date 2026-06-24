from src.core.exceptions import (
    AuthenticationRequiredError,
    PermissionDeniedError,
    ResourceNotFoundError,
)


class AdminAuthenticationRequiredError(AuthenticationRequiredError):
    detail: str = "ADMIN_AUTHENTICATION_REQUIRED_ERROR"


class AdminPermissionDeniedError(PermissionDeniedError):
    detail: str = "ADMIN_PERMISSION_DENIED_ERROR"


class AdminResourceNotFoundError(ResourceNotFoundError):
    detail: str = "ADMIN_RESOURCE_NOT_FOUND_ERROR"

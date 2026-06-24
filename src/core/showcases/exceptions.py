from src.core.admin_auth.exceptions import AdminPermissionDeniedError, AdminResourceNotFoundError


class ShowcaseAccessDeniedError(AdminPermissionDeniedError):
    detail: str = "SHOWCASE_ACCESS_DENIED_ERROR"


class AdminShowcaseNotFoundError(AdminResourceNotFoundError):
    detail: str = "ADMIN_SHOWCASE_NOT_FOUND_ERROR"

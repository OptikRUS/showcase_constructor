class BaseExceptionError(Exception):
    detail: str = ""

    def __init__(self, detail: str = "") -> None:
        self.detail = detail or self.detail
        super().__init__(self.detail)


class AuthenticationRequiredError(BaseExceptionError):
    detail: str = "AUTHENTICATION_REQUIRED_ERROR"


class PermissionDeniedError(BaseExceptionError):
    detail: str = "PERMISSION_DENIED_ERROR"


class ResourceNotFoundError(BaseExceptionError):
    detail: str = "RESOURCE_NOT_FOUND_ERROR"

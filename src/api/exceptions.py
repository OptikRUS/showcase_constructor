from collections.abc import Callable, Coroutine
from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse, Response

from src.core.admin_auth.exceptions import (
    AdminAuthenticationRequiredError,
    AdminPermissionDeniedError,
    AdminResourceNotFoundError,
)
from src.core.exceptions import BaseExceptionError
from src.core.showcases.exceptions import (
    AdminShowcasePublicationValidationError,
    PublicShowcaseNotFoundError,
)

ExceptionHandler = Callable[[Request, Any], Coroutine[Any, Any, Response]]
ExceptionHandlers = dict[int | type[Exception], ExceptionHandler]


async def internal_server_error_exception_handler(_: Request, _exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "INTERNAL_SERVER_ERROR"},
    )


def handler(status_code: int, message: str | None = None) -> ExceptionHandler:
    async def error(_: Request, exc: BaseExceptionError) -> JSONResponse:
        detail = message or exc.detail
        return JSONResponse(status_code=status_code, content={"detail": detail})

    return error


exception_handlers: ExceptionHandlers = {
    status.HTTP_500_INTERNAL_SERVER_ERROR: internal_server_error_exception_handler,
    AdminAuthenticationRequiredError: handler(status_code=status.HTTP_401_UNAUTHORIZED),
    AdminPermissionDeniedError: handler(status_code=status.HTTP_403_FORBIDDEN),
    AdminResourceNotFoundError: handler(status_code=status.HTTP_404_NOT_FOUND),
    PublicShowcaseNotFoundError: handler(status_code=status.HTTP_404_NOT_FOUND),
    AdminShowcasePublicationValidationError: handler(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT
    ),
}


def setup_exception_handlers(app: FastAPI) -> None:
    for exc_type, exc_handler in exception_handlers.items():
        app.add_exception_handler(exc_type, exc_handler)

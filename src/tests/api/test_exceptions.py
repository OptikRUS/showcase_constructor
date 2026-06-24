import json
from typing import cast

import pytest
from fastapi import status
from starlette.requests import Request

from src.api.exceptions import exception_handlers
from src.core.admin_auth.exceptions import AdminPermissionDeniedError, AdminResourceNotFoundError
from src.core.exceptions import BaseExceptionError


class TestExceptionHandlers:
    @pytest.mark.parametrize(
        ("exception_type", "expected_status", "expected_detail"),
        [
            (
                AdminPermissionDeniedError,
                status.HTTP_403_FORBIDDEN,
                "ADMIN_PERMISSION_DENIED_ERROR",
            ),
            (
                AdminResourceNotFoundError,
                status.HTTP_404_NOT_FOUND,
                "ADMIN_RESOURCE_NOT_FOUND_ERROR",
            ),
        ],
    )
    async def test_maps_admin_exceptions_to_http_responses(
        self,
        exception_type: type[BaseExceptionError],
        expected_status: int,
        expected_detail: str,
    ) -> None:
        request = Request(scope={"type": "http", "method": "GET", "path": "/"})
        exception_handler = exception_handlers[exception_type]

        response = await exception_handler(request, exception_type())
        response_body = cast("bytes", response.body)

        assert response.status_code == expected_status
        assert json.loads(response_body) == {"detail": expected_detail}

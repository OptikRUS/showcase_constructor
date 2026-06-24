from collections.abc import Callable
from contextlib import AbstractAsyncContextManager

from fastapi import FastAPI

from src.api.routers import root_router

Lifespan = Callable[[FastAPI], AbstractAsyncContextManager[None]]


def create_app(
    lifespan: Lifespan | None = None,
) -> FastAPI:
    app = FastAPI(
        docs_url=None,
        lifespan=lifespan,
        openapi_url=None,
        redoc_url=None,
    )
    app.include_router(root_router)
    return app

from collections.abc import Callable
from contextlib import AbstractAsyncContextManager

from fastapi import FastAPI

from src.api.exceptions import setup_exception_handlers
from src.api.routers import root_router

Lifespan = Callable[[FastAPI], AbstractAsyncContextManager[None]]


def create_app(
    lifespan: Lifespan | None = None,
) -> FastAPI:
    app = FastAPI(lifespan=lifespan)
    app.include_router(root_router)
    setup_exception_handlers(app=app)
    return app

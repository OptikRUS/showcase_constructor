from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import uvicorn
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI

from src.api.app import create_app
from src.di.container import create_container


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    yield
    await app.state.dishka_container.close()


def start_service() -> None:
    app = create_app(lifespan=lifespan)
    setup_dishka(container=create_container(), app=app)
    uvicorn.run(app=app, host="127.0.0.1", port=8080, access_log=False)


if __name__ == "__main__":
    start_service()

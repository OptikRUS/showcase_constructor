# Reference: src/main.py

```python
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import uvicorn
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI

from src.api.app import create_app
from src.config.settings import settings
from src.di.container import create_container
from src.migrations.commands import migrate


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    yield
    await app.state.dishka_container.close()


def start_service() -> None:
    migrate(revision="heads", db_url=settings.DATABASE.URL.get_secret_value())
    app = create_app(lifespan=lifespan)
    setup_dishka(container=create_container(), app=app)
    uvicorn.run(
        app=app,
        host=settings.APP.ADDRESS,
        port=settings.APP.PORT,
        access_log=False,
    )


if __name__ == "__main__":
    start_service()
```

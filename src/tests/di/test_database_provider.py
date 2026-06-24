from dataclasses import dataclass
from types import TracebackType
from unittest.mock import AsyncMock

import pytest
from dishka.integrations.fastapi import FastapiProvider
from sqlalchemy.ext.asyncio import AsyncSession

from src.di import container as container_module
from src.di.providers import database as database_provider_module
from src.di.providers.database import DatabaseProvider


@dataclass(kw_only=True)
class SessionContext:
    session: AsyncSession

    async def __aenter__(self) -> AsyncSession:
        return self.session

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> bool:
        _ = (exc_type, exc_value, traceback)
        return False


class TestDatabaseProvider:
    async def test_commits_session_after_successful_use(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        session = AsyncMock(spec=AsyncSession)

        def create_session() -> SessionContext:
            return SessionContext(session=session)

        monkeypatch.setattr(database_provider_module, "async_session", create_session)
        session_iterator = DatabaseProvider().get_db_session()

        provided_session = await anext(session_iterator)
        with pytest.raises(StopAsyncIteration):
            await anext(session_iterator)

        assert provided_session is session
        session.commit.assert_awaited_once_with()
        session.rollback.assert_not_awaited()

    async def test_rolls_back_session_and_reraises_exception(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        session = AsyncMock(spec=AsyncSession)
        error = RuntimeError("request failed")

        def create_session() -> SessionContext:
            return SessionContext(session=session)

        monkeypatch.setattr(database_provider_module, "async_session", create_session)
        session_iterator = DatabaseProvider().get_db_session()

        provided_session = await anext(session_iterator)
        with pytest.raises(RuntimeError, match="request failed"):
            await session_iterator.athrow(error)

        assert provided_session is session
        session.rollback.assert_awaited_once_with()
        session.commit.assert_not_awaited()


class TestContainer:
    def test_create_container_registers_database_provider(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        providers: list[object] = []
        container = object()

        def make_async_container(*provider_args: object) -> object:
            providers.extend(provider_args)
            return container

        monkeypatch.setattr(container_module, "make_async_container", make_async_container)

        assert container_module.create_container() is container
        assert any(isinstance(provider, FastapiProvider) for provider in providers)
        assert any(isinstance(provider, DatabaseProvider) for provider in providers)

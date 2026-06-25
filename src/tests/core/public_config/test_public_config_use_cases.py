from unittest.mock import AsyncMock

import pytest

from src.core.public_config.use_cases import (
    GetPublishedPublicConfigUseCase,
    ResolvePublishedPublicConfigUseCase,
)
from src.core.showcases.exceptions import PublicShowcaseNotFoundError
from src.core.storages import PublicShowcaseStorage
from src.tests.fixtures import FactoryFixture


class TestGetPublishedPublicConfigUseCase(FactoryFixture):
    async def test_gets_active_published_config_by_public_id(self) -> None:
        storage = AsyncMock(spec=PublicShowcaseStorage)
        snapshot = self.factory.published_public_config_snapshot()
        storage.get_active_public_config_snapshot.return_value = snapshot
        use_case = GetPublishedPublicConfigUseCase(storage=storage)

        result = await use_case.execute(public_id="public-showcase-1")

        assert result == snapshot
        storage.get_active_public_config_snapshot.assert_awaited_once_with(
            public_id="public-showcase-1"
        )

    async def test_propagates_not_found_for_missing_public_id(self) -> None:
        storage = AsyncMock(spec=PublicShowcaseStorage)
        storage.get_active_public_config_snapshot.side_effect = PublicShowcaseNotFoundError
        use_case = GetPublishedPublicConfigUseCase(storage=storage)

        with pytest.raises(PublicShowcaseNotFoundError) as error:
            await use_case.execute(public_id="missing-public")

        assert error.value.detail == "PUBLIC_SHOWCASE_NOT_FOUND_ERROR"
        storage.get_active_public_config_snapshot.assert_awaited_once_with(
            public_id="missing-public"
        )


class TestResolvePublishedPublicConfigUseCase(FactoryFixture):
    async def test_resolves_active_published_config_by_host_and_path(self) -> None:
        storage = AsyncMock(spec=PublicShowcaseStorage)
        snapshot = self.factory.published_public_config_snapshot()
        storage.resolve_active_public_config_snapshot.return_value = snapshot
        use_case = ResolvePublishedPublicConfigUseCase(storage=storage)

        result = await use_case.execute(host="offers.example.test", path="/loans")

        assert result == snapshot
        storage.resolve_active_public_config_snapshot.assert_awaited_once_with(
            host="offers.example.test",
            path="/loans",
        )

    async def test_propagates_not_found_for_missing_route_binding(self) -> None:
        storage = AsyncMock(spec=PublicShowcaseStorage)
        storage.resolve_active_public_config_snapshot.side_effect = PublicShowcaseNotFoundError
        use_case = ResolvePublishedPublicConfigUseCase(storage=storage)

        with pytest.raises(PublicShowcaseNotFoundError) as error:
            await use_case.execute(host="missing.example.test", path="/missing")

        assert error.value.detail == "PUBLIC_SHOWCASE_NOT_FOUND_ERROR"
        storage.resolve_active_public_config_snapshot.assert_awaited_once_with(
            host="missing.example.test",
            path="/missing",
        )

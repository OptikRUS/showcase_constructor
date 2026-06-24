from unittest.mock import AsyncMock

import pytest

from src.core.admin_auth.schemas import AdminActorContext
from src.core.showcases.exceptions import AdminShowcaseNotFoundError, ShowcaseAccessDeniedError
from src.core.showcases.use_cases import UpdateAdminShowcaseUseCase
from src.core.storages import AdminShowcaseStorage
from src.tests.fixtures import FactoryFixture


class TestUpdateAdminShowcaseUseCase(FactoryFixture):
    async def test_updates_same_owner_showcase(self) -> None:
        storage = AsyncMock(spec=AdminShowcaseStorage)
        storage.get_by_id.return_value = self.factory.admin_showcase(
            id="showcase-1",
            owner_partner_id="partner-1",
            title="Original showcase",
        )
        updated_showcase = self.factory.admin_showcase(
            id="showcase-1",
            owner_partner_id="partner-1",
            title="Updated showcase",
        )
        storage.update_draft.return_value = updated_showcase
        use_case = UpdateAdminShowcaseUseCase(storage=storage)
        params = self.factory.admin_showcase_update_params(title="Updated showcase")
        context = AdminActorContext(user_id="admin-user-1", partner_id="partner-1")

        result = await use_case.execute(showcase_id="showcase-1", params=params, context=context)

        assert result == updated_showcase
        storage.get_by_id.assert_awaited_once_with(showcase_id="showcase-1")
        storage.update_draft.assert_awaited_once_with(showcase_id="showcase-1", params=params)

    async def test_forbids_updating_foreign_showcase(self) -> None:
        storage = AsyncMock(spec=AdminShowcaseStorage)
        storage.get_by_id.return_value = self.factory.admin_showcase(
            id="showcase-1",
            owner_partner_id="partner-2",
        )
        use_case = UpdateAdminShowcaseUseCase(storage=storage)
        params = self.factory.admin_showcase_update_params(title="Updated showcase")
        context = AdminActorContext(user_id="admin-user-1", partner_id="partner-1")

        with pytest.raises(ShowcaseAccessDeniedError) as error:
            await use_case.execute(showcase_id="showcase-1", params=params, context=context)

        assert error.value.detail == "SHOWCASE_ACCESS_DENIED_ERROR"
        storage.get_by_id.assert_awaited_once_with(showcase_id="showcase-1")
        storage.update_draft.assert_not_awaited()

    async def test_propagates_not_found_from_storage(self) -> None:
        storage = AsyncMock(spec=AdminShowcaseStorage)
        storage.get_by_id.side_effect = AdminShowcaseNotFoundError
        use_case = UpdateAdminShowcaseUseCase(storage=storage)
        params = self.factory.admin_showcase_update_params(title="Updated showcase")
        context = AdminActorContext(user_id="admin-user-1", partner_id="partner-1")

        with pytest.raises(AdminShowcaseNotFoundError) as error:
            await use_case.execute(showcase_id="showcase-1", params=params, context=context)

        assert error.value.detail == "ADMIN_SHOWCASE_NOT_FOUND_ERROR"
        storage.get_by_id.assert_awaited_once_with(showcase_id="showcase-1")
        storage.update_draft.assert_not_awaited()

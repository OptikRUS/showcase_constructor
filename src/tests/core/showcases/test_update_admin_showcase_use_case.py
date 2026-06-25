from unittest.mock import AsyncMock

import pytest

from src.core.admin_auth.schemas import AdminActorContext
from src.core.showcases.exceptions import AdminShowcaseNotFoundError, ShowcaseAccessDeniedError
from src.core.showcases.use_cases import (
    UpdateAdminShowcaseDraftSettingsUseCase,
    UpdateAdminShowcaseUseCase,
)
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


class TestUpdateAdminShowcaseDraftSettingsUseCase(FactoryFixture):
    async def test_updates_custom_code_and_appends_safe_audit_record(self) -> None:
        storage = AsyncMock(spec=AdminShowcaseStorage)
        storage.get_by_id.return_value = self.factory.admin_showcase(
            id="showcase-1",
            owner_partner_id="partner-1",
            title="Custom code showcase",
        )
        updated_draft = self.factory.admin_showcase_draft(
            id="showcase-1",
            owner_partner_id="partner-1",
            title="Custom code showcase",
            settings={
                "custom_head_code": "<script>window.headPixel = true</script>",
                "custom_body_code": "<noscript>body pixel</noscript>",
            },
        )
        storage.update_draft_settings.return_value = updated_draft
        use_case = UpdateAdminShowcaseDraftSettingsUseCase(storage=storage)
        params = self.factory.admin_showcase_draft_settings_patch_params(
            settings={
                "custom_head_code": "<script>window.headPixel = true</script>",
                "custom_body_code": "<noscript>body pixel</noscript>",
            }
        )
        context = AdminActorContext(user_id="admin-user-1", partner_id="partner-1")

        result = await use_case.execute(showcase_id="showcase-1", params=params, context=context)

        assert result.settings == {
            "custom_head_code": "<script>window.headPixel = true</script>",
            "custom_body_code": "<noscript>body pixel</noscript>",
        }
        assert result.custom_code_warning == (
            "Custom frontend code is stored as owner-controlled frontend data; "
            "backend execution is disabled."
        )
        storage.get_by_id.assert_awaited_once_with(showcase_id="showcase-1")
        storage.update_draft_settings.assert_awaited_once_with(
            showcase_id="showcase-1",
            params=params,
        )
        storage.append_showcase_audit_record.assert_awaited_once_with(
            showcase_id="showcase-1",
            action="custom_code_updated",
            actor_user_id="admin-user-1",
            actor_partner_id="partner-1",
            metadata={
                "changed_fields": ["customHeadCode", "customBodyCode"],
                "custom_code_locations": ["head", "body"],
            },
        )

    async def test_updates_non_custom_settings_without_audit_record(self) -> None:
        storage = AsyncMock(spec=AdminShowcaseStorage)
        storage.get_by_id.return_value = self.factory.admin_showcase(
            id="showcase-1",
            owner_partner_id="partner-1",
        )
        updated_draft = self.factory.admin_showcase_draft(
            id="showcase-1",
            owner_partner_id="partner-1",
            settings={"text_title": "Updated title"},
        )
        storage.update_draft_settings.return_value = updated_draft
        use_case = UpdateAdminShowcaseDraftSettingsUseCase(storage=storage)
        params = self.factory.admin_showcase_draft_settings_patch_params(
            settings={"text_title": "Updated title"}
        )
        context = AdminActorContext(user_id="admin-user-1", partner_id="partner-1")

        result = await use_case.execute(showcase_id="showcase-1", params=params, context=context)

        assert result == updated_draft
        assert result.custom_code_warning is None
        storage.get_by_id.assert_awaited_once_with(showcase_id="showcase-1")
        storage.update_draft_settings.assert_awaited_once_with(
            showcase_id="showcase-1",
            params=params,
        )
        storage.append_showcase_audit_record.assert_not_awaited()

    async def test_forbids_foreign_owner_custom_code_update_before_mutation(self) -> None:
        storage = AsyncMock(spec=AdminShowcaseStorage)
        storage.get_by_id.return_value = self.factory.admin_showcase(
            id="showcase-1",
            owner_partner_id="partner-2",
        )
        use_case = UpdateAdminShowcaseDraftSettingsUseCase(storage=storage)
        params = self.factory.admin_showcase_draft_settings_patch_params(
            settings={"custom_head_code": "<script>window.foreign = true</script>"}
        )
        context = AdminActorContext(user_id="admin-user-1", partner_id="partner-1")

        with pytest.raises(ShowcaseAccessDeniedError) as error:
            await use_case.execute(showcase_id="showcase-1", params=params, context=context)

        assert error.value.detail == "SHOWCASE_ACCESS_DENIED_ERROR"
        storage.get_by_id.assert_awaited_once_with(showcase_id="showcase-1")
        storage.update_draft_settings.assert_not_awaited()
        storage.append_showcase_audit_record.assert_not_awaited()

    async def test_propagates_missing_showcase_before_custom_code_mutation(self) -> None:
        storage = AsyncMock(spec=AdminShowcaseStorage)
        storage.get_by_id.side_effect = AdminShowcaseNotFoundError
        use_case = UpdateAdminShowcaseDraftSettingsUseCase(storage=storage)
        params = self.factory.admin_showcase_draft_settings_patch_params(
            settings={"custom_body_code": "<noscript>missing</noscript>"}
        )
        context = AdminActorContext(user_id="admin-user-1", partner_id="partner-1")

        with pytest.raises(AdminShowcaseNotFoundError) as error:
            await use_case.execute(showcase_id="missing-showcase", params=params, context=context)

        assert error.value.detail == "ADMIN_SHOWCASE_NOT_FOUND_ERROR"
        storage.get_by_id.assert_awaited_once_with(showcase_id="missing-showcase")
        storage.update_draft_settings.assert_not_awaited()
        storage.append_showcase_audit_record.assert_not_awaited()

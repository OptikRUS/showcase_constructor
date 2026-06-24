from unittest.mock import AsyncMock
from uuid import UUID

import pytest

from src.core.admin_auth.schemas import AdminActorContext
from src.core.showcases.exceptions import AdminShowcaseNotFoundError, ShowcaseAccessDeniedError
from src.core.showcases.use_cases import (
    CreateAdminShowcaseBlockUseCase,
    DeleteAdminShowcaseBlockUseCase,
    ListAdminShowcaseBlocksUseCase,
    PatchAdminShowcaseBlockUseCase,
)
from src.core.storages import AdminShowcaseStorage
from src.tests.fixtures import FactoryFixture


class TestListAdminShowcaseBlocksUseCase(FactoryFixture):
    async def test_lists_same_owner_draft_blocks(self) -> None:
        storage = AsyncMock(spec=AdminShowcaseStorage)
        storage.get_by_id.return_value = self.factory.admin_showcase(
            id="showcase-blocks-core-list",
            owner_partner_id="partner-1",
        )
        blocks = [
            self.factory.admin_showcase_draft_block(
                id="block-core-list-1",
                showcase_id="showcase-blocks-core-list",
                order=10,
            )
        ]
        storage.list_draft_blocks.return_value = blocks
        use_case = ListAdminShowcaseBlocksUseCase(storage=storage)
        context = AdminActorContext(user_id="admin-user-1", partner_id="partner-1")

        result = await use_case.execute(showcase_id="showcase-blocks-core-list", context=context)

        assert result == blocks
        storage.get_by_id.assert_awaited_once_with(showcase_id="showcase-blocks-core-list")
        storage.list_draft_blocks.assert_awaited_once_with(
            showcase_id="showcase-blocks-core-list"
        )

    async def test_forbids_listing_foreign_draft_blocks(self) -> None:
        storage = AsyncMock(spec=AdminShowcaseStorage)
        storage.get_by_id.return_value = self.factory.admin_showcase(
            id="showcase-blocks-core-foreign",
            owner_partner_id="partner-2",
        )
        use_case = ListAdminShowcaseBlocksUseCase(storage=storage)
        context = AdminActorContext(user_id="admin-user-1", partner_id="partner-1")

        with pytest.raises(ShowcaseAccessDeniedError) as error:
            await use_case.execute(showcase_id="showcase-blocks-core-foreign", context=context)

        assert error.value.detail == "SHOWCASE_ACCESS_DENIED_ERROR"
        storage.get_by_id.assert_awaited_once_with(showcase_id="showcase-blocks-core-foreign")
        storage.list_draft_blocks.assert_not_awaited()

    async def test_propagates_not_found_from_storage(self) -> None:
        storage = AsyncMock(spec=AdminShowcaseStorage)
        storage.get_by_id.side_effect = AdminShowcaseNotFoundError
        use_case = ListAdminShowcaseBlocksUseCase(storage=storage)
        context = AdminActorContext(user_id="admin-user-1", partner_id="partner-1")

        with pytest.raises(AdminShowcaseNotFoundError) as error:
            await use_case.execute(showcase_id="missing-showcase", context=context)

        assert error.value.detail == "ADMIN_SHOWCASE_NOT_FOUND_ERROR"
        storage.get_by_id.assert_awaited_once_with(showcase_id="missing-showcase")
        storage.list_draft_blocks.assert_not_awaited()


class TestCreateAdminShowcaseBlockUseCase(FactoryFixture):
    async def test_creates_same_owner_draft_block(self) -> None:
        storage = AsyncMock(spec=AdminShowcaseStorage)
        storage.get_by_id.return_value = self.factory.admin_showcase(
            id="showcase-blocks-core-create",
            owner_partner_id="partner-1",
        )
        params = self.factory.admin_showcase_draft_block_create_params(
            type="custom_html",
            order=5,
            title="Hero custom HTML",
            subtitle=None,
            desktop_settings={"width": "full"},
            mobile_settings={"width": "compact"},
            data={"html": "<section>Owner draft only</section>"},
        )
        block_id = UUID("00000000-0000-0000-0000-000000000005")
        created_block = self.factory.admin_showcase_draft_block(
            id=str(block_id),
            showcase_id="showcase-blocks-core-create",
            type="custom_html",
            order=5,
            title="Hero custom HTML",
            subtitle=None,
            desktop_settings={"width": "full"},
            mobile_settings={"width": "compact"},
            data={"html": "<section>Owner draft only</section>"},
        )
        storage.create_draft_block.return_value = created_block
        use_case = CreateAdminShowcaseBlockUseCase(storage=storage, block_id=block_id)
        context = AdminActorContext(user_id="admin-user-1", partner_id="partner-1")

        result = await use_case.execute(
            showcase_id="showcase-blocks-core-create",
            params=params,
            context=context,
        )

        assert result == created_block
        storage.get_by_id.assert_awaited_once_with(showcase_id="showcase-blocks-core-create")
        storage.create_draft_block.assert_awaited_once_with(
            showcase_id="showcase-blocks-core-create",
            block_id=str(block_id),
            params=params,
        )

    async def test_forbids_creating_foreign_draft_block(self) -> None:
        storage = AsyncMock(spec=AdminShowcaseStorage)
        storage.get_by_id.return_value = self.factory.admin_showcase(
            id="showcase-blocks-core-create-foreign",
            owner_partner_id="partner-2",
        )
        params = self.factory.admin_showcase_draft_block_create_params()
        block_id = UUID("00000000-0000-0000-0000-000000000006")
        use_case = CreateAdminShowcaseBlockUseCase(storage=storage, block_id=block_id)
        context = AdminActorContext(user_id="admin-user-1", partner_id="partner-1")

        with pytest.raises(ShowcaseAccessDeniedError) as error:
            await use_case.execute(
                showcase_id="showcase-blocks-core-create-foreign",
                params=params,
                context=context,
            )

        assert error.value.detail == "SHOWCASE_ACCESS_DENIED_ERROR"
        storage.get_by_id.assert_awaited_once_with(
            showcase_id="showcase-blocks-core-create-foreign"
        )
        storage.create_draft_block.assert_not_awaited()


class TestPatchAdminShowcaseBlockUseCase(FactoryFixture):
    async def test_patches_same_owner_draft_block(self) -> None:
        storage = AsyncMock(spec=AdminShowcaseStorage)
        storage.get_by_id.return_value = self.factory.admin_showcase(
            id="showcase-blocks-core-patch",
            owner_partner_id="partner-1",
        )
        params = self.factory.admin_showcase_draft_block_patch_params(
            values={
                "order": 30,
                "visible": False,
                "title": "Updated block",
                "subtitle": None,
                "desktop_settings": {"width": "full"},
                "mobile_settings": {"width": "stacked"},
                "data": {"html": "<section>Draft only</section>"},
            }
        )
        patched_block = self.factory.admin_showcase_draft_block(
            id="block-core-patch",
            showcase_id="showcase-blocks-core-patch",
            order=30,
            visible=False,
            title="Updated block",
            subtitle=None,
            desktop_settings={"width": "full"},
            mobile_settings={"width": "stacked"},
            data={"html": "<section>Draft only</section>"},
        )
        storage.patch_draft_block.return_value = patched_block
        use_case = PatchAdminShowcaseBlockUseCase(storage=storage)
        context = AdminActorContext(user_id="admin-user-1", partner_id="partner-1")

        result = await use_case.execute(
            showcase_id="showcase-blocks-core-patch",
            block_id="block-core-patch",
            params=params,
            context=context,
        )

        assert result == patched_block
        storage.get_by_id.assert_awaited_once_with(showcase_id="showcase-blocks-core-patch")
        storage.patch_draft_block.assert_awaited_once_with(
            showcase_id="showcase-blocks-core-patch",
            block_id="block-core-patch",
            params=params,
        )

    async def test_forbids_patching_foreign_draft_block(self) -> None:
        storage = AsyncMock(spec=AdminShowcaseStorage)
        storage.get_by_id.return_value = self.factory.admin_showcase(
            id="showcase-blocks-core-patch-foreign",
            owner_partner_id="partner-2",
        )
        params = self.factory.admin_showcase_draft_block_patch_params(values={"visible": False})
        use_case = PatchAdminShowcaseBlockUseCase(storage=storage)
        context = AdminActorContext(user_id="admin-user-1", partner_id="partner-1")

        with pytest.raises(ShowcaseAccessDeniedError) as error:
            await use_case.execute(
                showcase_id="showcase-blocks-core-patch-foreign",
                block_id="block-core-patch-foreign",
                params=params,
                context=context,
            )

        assert error.value.detail == "SHOWCASE_ACCESS_DENIED_ERROR"
        storage.get_by_id.assert_awaited_once_with(
            showcase_id="showcase-blocks-core-patch-foreign"
        )
        storage.patch_draft_block.assert_not_awaited()


class TestDeleteAdminShowcaseBlockUseCase(FactoryFixture):
    async def test_deletes_same_owner_draft_block(self) -> None:
        storage = AsyncMock(spec=AdminShowcaseStorage)
        storage.get_by_id.return_value = self.factory.admin_showcase(
            id="showcase-blocks-core-delete",
            owner_partner_id="partner-1",
        )
        use_case = DeleteAdminShowcaseBlockUseCase(storage=storage)
        context = AdminActorContext(user_id="admin-user-1", partner_id="partner-1")

        await use_case.execute(
            showcase_id="showcase-blocks-core-delete",
            block_id="block-core-delete",
            context=context,
        )

        storage.get_by_id.assert_awaited_once_with(showcase_id="showcase-blocks-core-delete")
        storage.delete_draft_block.assert_awaited_once_with(
            showcase_id="showcase-blocks-core-delete",
            block_id="block-core-delete",
        )

    async def test_forbids_deleting_foreign_draft_block(self) -> None:
        storage = AsyncMock(spec=AdminShowcaseStorage)
        storage.get_by_id.return_value = self.factory.admin_showcase(
            id="showcase-blocks-core-delete-foreign",
            owner_partner_id="partner-2",
        )
        use_case = DeleteAdminShowcaseBlockUseCase(storage=storage)
        context = AdminActorContext(user_id="admin-user-1", partner_id="partner-1")

        with pytest.raises(ShowcaseAccessDeniedError) as error:
            await use_case.execute(
                showcase_id="showcase-blocks-core-delete-foreign",
                block_id="block-core-delete-foreign",
                context=context,
            )

        assert error.value.detail == "SHOWCASE_ACCESS_DENIED_ERROR"
        storage.get_by_id.assert_awaited_once_with(
            showcase_id="showcase-blocks-core-delete-foreign"
        )
        storage.delete_draft_block.assert_not_awaited()

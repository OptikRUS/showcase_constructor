from __future__ import annotations

from typing import TYPE_CHECKING

from httpx2 import codes

from src.tests.fixtures import APIFixture, FactoryFixture, StorageFixture

if TYPE_CHECKING:
    from src.core.showcases.schemas import JsonObject


class TestAdminShowcaseBlocksAPI(APIFixture, FactoryFixture, StorageFixture):
    async def test_creates_and_lists_draft_blocks(self) -> None:
        published_snapshot: JsonObject = {
            "id": "public-showcase-api-blocks-1",
            "blocks": [{"type": "offers", "title": "Published offers"}],
        }
        await self.storage_helper.create_admin_showcase(
            id="showcase-api-blocks-1",
            owner_partner_id="partner-1",
            title="Blocks showcase",
            draft_settings={"design_id": "classic"},
            published_snapshot=published_snapshot,
        )
        await self.storage_helper.create_admin_showcase_draft_block(
            block=self.factory.admin_showcase_draft_block(
                id="block-api-existing",
                showcase_id="showcase-api-blocks-1",
                type="offers",
                order=20,
                visible=False,
                title="Existing offers",
                subtitle="Existing subtitle",
                desktop_settings={"columns": 3},
                mobile_settings={"columns": 1},
                data={"layout": "cards"},
            )
        )
        await self.storage_helper.commit()

        create_response = self.api.create_admin_showcase_block(
            showcase_id="showcase-api-blocks-1",
            json={
                "type": "custom_html",
                "order": 10,
                "visible": True,
                "title": "Custom hero",
                "subtitle": None,
                "desktopSettings": {"width": "full"},
                "mobileSettings": {"width": "compact"},
                "data": {"html": "<section>Owner draft only</section>"},
            },
        )

        assert create_response.status_code == codes.CREATED
        created_payload = create_response.json()
        assert created_payload == {
            "id": created_payload["id"],
            "type": "custom_html",
            "order": 10,
            "visible": True,
            "title": "Custom hero",
            "subtitle": None,
            "desktopSettings": {"width": "full"},
            "mobileSettings": {"width": "compact"},
            "data": {"html": "<section>Owner draft only</section>"},
        }
        assert isinstance(created_payload["id"], str)
        assert created_payload["id"]

        list_response = self.api.list_admin_showcase_blocks(showcase_id="showcase-api-blocks-1")

        assert list_response.status_code == codes.OK
        assert list_response.json() == [
            created_payload,
            {
                "id": "block-api-existing",
                "type": "offers",
                "order": 20,
                "visible": False,
                "title": "Existing offers",
                "subtitle": "Existing subtitle",
                "desktopSettings": {"columns": 3},
                "mobileSettings": {"columns": 1},
                "data": {"layout": "cards"},
            },
        ]

        persisted_blocks = await self.storage_helper.list_admin_showcase_draft_blocks(
            showcase_id="showcase-api-blocks-1"
        )
        assert [block.id for block in persisted_blocks] == [
            created_payload["id"],
            "block-api-existing",
        ]
        persisted = await self.storage_helper.get_admin_showcase_draft(
            showcase_id="showcase-api-blocks-1"
        )
        assert persisted.published_snapshot == published_snapshot

    async def test_forbids_foreign_owner_block_access(self) -> None:
        await self.storage_helper.create_admin_showcase(
            id="showcase-api-blocks-foreign",
            owner_partner_id="partner-2",
            title="Foreign blocks showcase",
            draft_settings={"design_id": "classic"},
            published_snapshot={"id": "public-blocks-foreign"},
        )
        await self.storage_helper.commit()

        list_response = self.api.list_admin_showcase_blocks(
            showcase_id="showcase-api-blocks-foreign"
        )
        create_response = self.api.create_admin_showcase_block(
            showcase_id="showcase-api-blocks-foreign",
            json={"type": "hero", "order": 1},
        )

        assert list_response.status_code == codes.FORBIDDEN
        assert list_response.json() == {"detail": "SHOWCASE_ACCESS_DENIED_ERROR"}
        assert create_response.status_code == codes.FORBIDDEN
        assert create_response.json() == {"detail": "SHOWCASE_ACCESS_DENIED_ERROR"}
        persisted_blocks = await self.storage_helper.list_admin_showcase_draft_blocks(
            showcase_id="showcase-api-blocks-foreign"
        )
        assert persisted_blocks == []

    async def test_patches_and_deletes_draft_block(self) -> None:
        published_snapshot: JsonObject = {
            "id": "public-showcase-api-blocks-patch",
            "blocks": [{"type": "offers", "title": "Published offers"}],
        }
        await self.storage_helper.create_admin_showcase(
            id="showcase-api-blocks-patch",
            owner_partner_id="partner-1",
            title="Patch blocks showcase",
            draft_settings={"design_id": "classic"},
            published_snapshot=published_snapshot,
        )
        await self.storage_helper.create_admin_showcase_draft_block(
            block=self.factory.admin_showcase_draft_block(
                id="block-api-patch-target",
                showcase_id="showcase-api-blocks-patch",
                type="custom_html",
                order=10,
                visible=True,
                title="Original custom block",
                subtitle="Original subtitle",
                desktop_settings={"width": "narrow"},
                mobile_settings={"width": "compact"},
                data={"html": "<section>Original</section>"},
            )
        )
        await self.storage_helper.create_admin_showcase_draft_block(
            block=self.factory.admin_showcase_draft_block(
                id="block-api-delete-target",
                showcase_id="showcase-api-blocks-patch",
                type="offers",
                order=20,
                visible=True,
                title="Delete me",
                subtitle="Delete subtitle",
                desktop_settings={"columns": 3},
                mobile_settings={"columns": 1},
                data={"layout": "cards"},
            )
        )
        await self.storage_helper.create_admin_showcase_draft_offer(
            offer=self.factory.admin_showcase_draft_offer(
                id="offer-api-preserved",
                showcase_id="showcase-api-blocks-patch",
                block_id="block-api-delete-target",
                manual_order=1,
                data={"source": "manual"},
            )
        )
        await self.storage_helper.commit()

        patch_response = self.api.patch_admin_showcase_block(
            showcase_id="showcase-api-blocks-patch",
            block_id="block-api-patch-target",
            json={
                "order": 30,
                "visible": False,
                "title": "Updated custom block",
                "subtitle": None,
                "desktopSettings": {"width": "full", "theme": "dark"},
                "mobileSettings": {"width": "stacked"},
                "data": {"html": "<script>window.ownerDraftOnly = true</script>"},
            },
        )
        delete_response = self.api.delete_admin_showcase_block(
            showcase_id="showcase-api-blocks-patch",
            block_id="block-api-delete-target",
        )

        assert patch_response.status_code == codes.OK
        assert patch_response.json() == {
            "id": "block-api-patch-target",
            "type": "custom_html",
            "order": 30,
            "visible": False,
            "title": "Updated custom block",
            "subtitle": None,
            "desktopSettings": {"width": "full", "theme": "dark"},
            "mobileSettings": {"width": "stacked"},
            "data": {"html": "<script>window.ownerDraftOnly = true</script>"},
        }
        assert delete_response.status_code == codes.NO_CONTENT
        assert delete_response.content == b""

        list_response = self.api.list_admin_showcase_blocks(
            showcase_id="showcase-api-blocks-patch"
        )
        assert list_response.status_code == codes.OK
        assert list_response.json() == [patch_response.json()]

        persisted = await self.storage_helper.get_admin_showcase_draft(
            showcase_id="showcase-api-blocks-patch"
        )
        assert persisted.published_snapshot == published_snapshot
        persisted_offers = await self.storage_helper.list_admin_showcase_draft_offers(
            showcase_id="showcase-api-blocks-patch"
        )
        assert [offer.id for offer in persisted_offers] == ["offer-api-preserved"]

    async def test_forbids_foreign_owner_block_mutation(self) -> None:
        await self.storage_helper.create_admin_showcase(
            id="showcase-api-blocks-patch-foreign",
            owner_partner_id="partner-2",
            title="Foreign block mutation showcase",
        )
        await self.storage_helper.create_admin_showcase_draft_block(
            block=self.factory.admin_showcase_draft_block(
                id="block-api-patch-foreign",
                showcase_id="showcase-api-blocks-patch-foreign",
                order=10,
                visible=True,
                title="Foreign block",
            )
        )
        await self.storage_helper.commit()

        patch_response = self.api.patch_admin_showcase_block(
            showcase_id="showcase-api-blocks-patch-foreign",
            block_id="block-api-patch-foreign",
            json={"visible": False},
        )
        delete_response = self.api.delete_admin_showcase_block(
            showcase_id="showcase-api-blocks-patch-foreign",
            block_id="block-api-patch-foreign",
        )

        assert patch_response.status_code == codes.FORBIDDEN
        assert patch_response.json() == {"detail": "SHOWCASE_ACCESS_DENIED_ERROR"}
        assert delete_response.status_code == codes.FORBIDDEN
        assert delete_response.json() == {"detail": "SHOWCASE_ACCESS_DENIED_ERROR"}
        persisted_blocks = await self.storage_helper.list_admin_showcase_draft_blocks(
            showcase_id="showcase-api-blocks-patch-foreign"
        )
        assert persisted_blocks[0].visible is True

    async def test_returns_not_found_for_missing_block(self) -> None:
        await self.storage_helper.create_admin_showcase(
            id="showcase-api-blocks-missing-block",
            owner_partner_id="partner-1",
            title="Missing block showcase",
        )
        await self.storage_helper.commit()

        patch_response = self.api.patch_admin_showcase_block(
            showcase_id="showcase-api-blocks-missing-block",
            block_id="missing-block",
            json={"visible": False},
        )
        delete_response = self.api.delete_admin_showcase_block(
            showcase_id="showcase-api-blocks-missing-block",
            block_id="missing-block",
        )

        assert patch_response.status_code == codes.NOT_FOUND
        assert patch_response.json() == {"detail": "ADMIN_SHOWCASE_DRAFT_BLOCK_NOT_FOUND_ERROR"}
        assert delete_response.status_code == codes.NOT_FOUND
        assert delete_response.json() == {"detail": "ADMIN_SHOWCASE_DRAFT_BLOCK_NOT_FOUND_ERROR"}

    def test_returns_not_found_for_missing_showcase(self) -> None:
        list_response = self.api.list_admin_showcase_blocks(showcase_id="missing-showcase")
        create_response = self.api.create_admin_showcase_block(
            showcase_id="missing-showcase",
            json={"type": "hero", "order": 1},
        )
        patch_response = self.api.patch_admin_showcase_block(
            showcase_id="missing-showcase",
            block_id="missing-block",
            json={"visible": False},
        )
        delete_response = self.api.delete_admin_showcase_block(
            showcase_id="missing-showcase",
            block_id="missing-block",
        )

        assert list_response.status_code == codes.NOT_FOUND
        assert list_response.json() == {"detail": "ADMIN_SHOWCASE_NOT_FOUND_ERROR"}
        assert create_response.status_code == codes.NOT_FOUND
        assert create_response.json() == {"detail": "ADMIN_SHOWCASE_NOT_FOUND_ERROR"}
        assert patch_response.status_code == codes.NOT_FOUND
        assert patch_response.json() == {"detail": "ADMIN_SHOWCASE_NOT_FOUND_ERROR"}
        assert delete_response.status_code == codes.NOT_FOUND
        assert delete_response.json() == {"detail": "ADMIN_SHOWCASE_NOT_FOUND_ERROR"}

    async def test_rejects_unsupported_block_type(self) -> None:
        await self.storage_helper.create_admin_showcase(
            id="showcase-api-blocks-invalid-type",
            owner_partner_id="partner-1",
            title="Invalid block type showcase",
        )
        await self.storage_helper.commit()

        response = self.api.create_admin_showcase_block(
            showcase_id="showcase-api-blocks-invalid-type",
            json={"type": "unsupported", "order": 1},
        )

        assert response.status_code == codes.UNPROCESSABLE_ENTITY
        persisted_blocks = await self.storage_helper.list_admin_showcase_draft_blocks(
            showcase_id="showcase-api-blocks-invalid-type"
        )
        assert persisted_blocks == []


class TestAdminShowcaseBlocksNoAuthAPI(APIFixture, StorageFixture):
    async def test_requires_authentication(self) -> None:
        await self.storage_helper.create_admin_showcase(
            id="showcase-api-blocks-no-auth",
            owner_partner_id="partner-1",
            title="No auth blocks showcase",
            published_snapshot={"id": "public-blocks-no-auth"},
        )
        await self.storage_helper.commit()

        list_response = self.no_auth_api.list_admin_showcase_blocks(
            showcase_id="showcase-api-blocks-no-auth"
        )
        create_response = self.no_auth_api.create_admin_showcase_block(
            showcase_id="showcase-api-blocks-no-auth",
            json={"type": "hero", "order": 1},
        )
        patch_response = self.no_auth_api.patch_admin_showcase_block(
            showcase_id="showcase-api-blocks-no-auth",
            block_id="block-no-auth",
            json={"visible": False},
        )
        delete_response = self.no_auth_api.delete_admin_showcase_block(
            showcase_id="showcase-api-blocks-no-auth",
            block_id="block-no-auth",
        )

        assert list_response.status_code == codes.UNAUTHORIZED
        assert list_response.json() == {"detail": "ADMIN_AUTHENTICATION_REQUIRED_ERROR"}
        assert create_response.status_code == codes.UNAUTHORIZED
        assert create_response.json() == {"detail": "ADMIN_AUTHENTICATION_REQUIRED_ERROR"}
        assert patch_response.status_code == codes.UNAUTHORIZED
        assert patch_response.json() == {"detail": "ADMIN_AUTHENTICATION_REQUIRED_ERROR"}
        assert delete_response.status_code == codes.UNAUTHORIZED
        assert delete_response.json() == {"detail": "ADMIN_AUTHENTICATION_REQUIRED_ERROR"}
        persisted_blocks = await self.storage_helper.list_admin_showcase_draft_blocks(
            showcase_id="showcase-api-blocks-no-auth"
        )
        assert persisted_blocks == []

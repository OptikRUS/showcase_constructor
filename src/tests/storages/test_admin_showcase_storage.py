import pytest

from src.core.showcases.exceptions import AdminShowcaseNotFoundError
from src.core.showcases.schemas import (
    AdminShowcaseDraftBlockCreateParams,
    AdminShowcaseDraftSettingsPatchParams,
    JsonObject,
)
from src.storages.showcases import DatabaseAdminShowcaseStorage
from src.tests.fixtures import FactoryFixture, StorageFixture


class TestDatabaseAdminShowcaseStorage(FactoryFixture, StorageFixture):
    async def test_updates_draft_settings_without_changing_published_snapshot(self) -> None:
        published_snapshot: JsonObject = {
            "id": "public-showcase-1",
            "settings": {"design_id": "published", "text_title": "Published title"},
        }
        await self.storage_helper.create_admin_showcase(
            id="showcase-1",
            owner_partner_id="partner-1",
            title="Original showcase",
            draft_settings={
                "design_id": "classic",
                "color_scheme": "light",
                "text_title": "Original draft title",
                "image_banner_mobile": "https://cdn.example.test/mobile.png",
            },
            published_snapshot=published_snapshot,
        )
        storage = DatabaseAdminShowcaseStorage(session=self.storage_helper.session)
        params = AdminShowcaseDraftSettingsPatchParams(
            settings={
                "design_id": "modern",
                "text_title": "Updated draft title",
                "image_banner_mobile": None,
            }
        )

        result = await storage.update_draft_settings(showcase_id="showcase-1", params=params)

        assert result.id == "showcase-1"
        assert result.owner_partner_id == "partner-1"
        assert result.title == "Original showcase"
        assert result.settings == {
            "design_id": "modern",
            "color_scheme": "light",
            "text_title": "Updated draft title",
            "image_banner_mobile": None,
        }
        assert result.published_snapshot == published_snapshot

        persisted = await storage.get_draft_by_id(showcase_id="showcase-1")
        assert persisted == result

    async def test_raises_not_found_when_updating_missing_draft_settings(self) -> None:
        storage = DatabaseAdminShowcaseStorage(session=self.storage_helper.session)
        params = AdminShowcaseDraftSettingsPatchParams(settings={"design_id": "modern"})

        with pytest.raises(AdminShowcaseNotFoundError) as error:
            await storage.update_draft_settings(showcase_id="missing-showcase", params=params)

        assert error.value.detail == "ADMIN_SHOWCASE_NOT_FOUND_ERROR"

    async def test_creates_and_lists_draft_blocks_ordered_by_draft_order(self) -> None:
        await self.storage_helper.create_admin_showcase(
            id="showcase-blocks-storage-1",
            owner_partner_id="partner-1",
            title="Block storage showcase",
            published_snapshot={"id": "public-blocks-storage-1"},
        )
        await self.storage_helper.create_admin_showcase_draft_block(
            block=self.factory.admin_showcase_draft_block(
                id="block-storage-existing",
                showcase_id="showcase-blocks-storage-1",
                type="offers",
                order=20,
                visible=True,
                title="Existing offers",
                subtitle="Existing subtitle",
                desktop_settings={"columns": 3},
                mobile_settings={"columns": 1},
                data={"layout": "cards"},
            )
        )
        storage = DatabaseAdminShowcaseStorage(session=self.storage_helper.session)
        params = AdminShowcaseDraftBlockCreateParams(
            type="custom_html",
            order=10,
            visible=False,
            title="Custom block",
            subtitle=None,
            desktop_settings={"width": "full"},
            mobile_settings={"width": "compact"},
            data={"html": "<section>Draft block</section>"},
        )

        created = await storage.create_draft_block(
            showcase_id="showcase-blocks-storage-1",
            block_id="block-storage-created",
            params=params,
        )
        blocks = await storage.list_draft_blocks(showcase_id="showcase-blocks-storage-1")

        assert created.id == "block-storage-created"
        assert created.showcase_id == "showcase-blocks-storage-1"
        assert created.type == "custom_html"
        assert created.order == 10
        assert created.visible is False
        assert created.title == "Custom block"
        assert created.subtitle is None
        assert created.desktop_settings == {"width": "full"}
        assert created.mobile_settings == {"width": "compact"}
        assert created.data == {"html": "<section>Draft block</section>"}
        assert [block.id for block in blocks] == [
            "block-storage-created",
            "block-storage-existing",
        ]

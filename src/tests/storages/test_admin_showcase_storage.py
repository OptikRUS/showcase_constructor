import pytest

from src.core.showcases.exceptions import AdminShowcaseNotFoundError
from src.core.showcases.schemas import AdminShowcaseDraftSettingsPatchParams, JsonObject
from src.storages.showcases import DatabaseAdminShowcaseStorage
from src.tests.fixtures import StorageFixture


class TestDatabaseAdminShowcaseStorage(StorageFixture):
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

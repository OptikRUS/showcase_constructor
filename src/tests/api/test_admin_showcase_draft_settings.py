from __future__ import annotations

from typing import TYPE_CHECKING

from httpx2 import codes

from src.tests.fixtures import APIFixture, StorageFixture

if TYPE_CHECKING:
    from src.core.showcases.schemas import JsonObject


class TestAdminShowcaseDraftSettingsAPI(APIFixture, StorageFixture):
    async def test_accepts_empty_patch_without_mutating_draft_settings(self) -> None:
        await self.storage_helper.create_admin_showcase(
            id="showcase-api-settings-empty-patch",
            owner_partner_id="partner-1",
            title="Empty patch showcase",
            draft_settings={
                "design_id": "classic",
                "text_title": "Original draft title",
            },
            published_snapshot={"id": "public-settings-empty-patch"},
        )
        await self.storage_helper.commit()

        response = self.api.patch_admin_showcase_draft_settings(
            showcase_id="showcase-api-settings-empty-patch",
            json={},
        )

        assert response.status_code == codes.OK
        assert response.json() == {
            "id": "showcase-api-settings-empty-patch",
            "title": "Empty patch showcase",
            "settings": {
                "designId": "classic",
                "textTitle": "Original draft title",
            },
        }
        persisted = await self.storage_helper.get_admin_showcase_draft(
            showcase_id="showcase-api-settings-empty-patch"
        )
        assert persisted.settings == {
            "design_id": "classic",
            "text_title": "Original draft title",
        }
        assert persisted.published_snapshot == {"id": "public-settings-empty-patch"}

    async def test_patches_draft_settings_only(self) -> None:
        published_snapshot: JsonObject = {
            "id": "public-showcase-api-settings-1",
            "settings": {
                "design_id": "published",
                "text_title": "Published title",
            },
        }
        await self.storage_helper.create_admin_showcase(
            id="showcase-api-settings-1",
            owner_partner_id="partner-1",
            title="Original showcase",
            draft_settings={
                "design_id": "classic",
                "color_scheme": "light",
                "font_family": "Arial",
                "text_title": "Original draft title",
                "text_subtitle": "Original subtitle",
                "text_button": "Apply",
                "meta_title": "Original meta",
                "meta_description": "Original description",
                "image_banner_desktop": "https://cdn.example.test/desktop-old.png",
                "image_banner_mobile": "https://cdn.example.test/mobile-old.png",
                "image_banner_mini": "https://cdn.example.test/mini-old.png",
                "fallback_text": "Original fallback",
            },
            published_snapshot=published_snapshot,
        )
        await self.storage_helper.commit()

        response = self.api.patch_admin_showcase_draft_settings(
            showcase_id="showcase-api-settings-1",
            json={
                "designId": "modern",
                "fontFamily": "Inter",
                "textTitle": "Updated draft title",
                "metaTitle": "Updated meta",
                "imageBannerMobile": None,
                "fallbackText": "No offers available",
            },
        )

        assert response.status_code == codes.OK
        assert response.json() == {
            "id": "showcase-api-settings-1",
            "title": "Original showcase",
            "settings": {
                "designId": "modern",
                "colorScheme": "light",
                "fontFamily": "Inter",
                "textTitle": "Updated draft title",
                "textSubtitle": "Original subtitle",
                "textButton": "Apply",
                "metaTitle": "Updated meta",
                "metaDescription": "Original description",
                "imageBannerDesktop": "https://cdn.example.test/desktop-old.png",
                "imageBannerMobile": None,
                "imageBannerMini": "https://cdn.example.test/mini-old.png",
                "fallbackText": "No offers available",
            },
        }

        persisted = await self.storage_helper.get_admin_showcase_draft(
            showcase_id="showcase-api-settings-1"
        )
        assert persisted.settings == {
            "design_id": "modern",
            "color_scheme": "light",
            "font_family": "Inter",
            "text_title": "Updated draft title",
            "text_subtitle": "Original subtitle",
            "text_button": "Apply",
            "meta_title": "Updated meta",
            "meta_description": "Original description",
            "image_banner_desktop": "https://cdn.example.test/desktop-old.png",
            "image_banner_mobile": None,
            "image_banner_mini": "https://cdn.example.test/mini-old.png",
            "fallback_text": "No offers available",
        }
        assert persisted.published_snapshot == published_snapshot

    async def test_forbids_foreign_owner_draft_settings_patch(self) -> None:
        await self.storage_helper.create_admin_showcase(
            id="showcase-api-settings-foreign",
            owner_partner_id="partner-2",
            title="Foreign showcase",
            draft_settings={"design_id": "classic"},
            published_snapshot={"id": "public-foreign"},
        )
        await self.storage_helper.commit()

        response = self.api.patch_admin_showcase_draft_settings(
            showcase_id="showcase-api-settings-foreign",
            json={"designId": "modern"},
        )

        assert response.status_code == codes.FORBIDDEN
        assert response.json() == {"detail": "SHOWCASE_ACCESS_DENIED_ERROR"}

        persisted = await self.storage_helper.get_admin_showcase_draft(
            showcase_id="showcase-api-settings-foreign"
        )
        assert persisted.settings == {"design_id": "classic"}
        assert persisted.published_snapshot == {"id": "public-foreign"}

    def test_returns_not_found_for_missing_showcase(self) -> None:
        response = self.api.patch_admin_showcase_draft_settings(
            showcase_id="missing-showcase",
            json={"designId": "modern"},
        )

        assert response.status_code == codes.NOT_FOUND
        assert response.json() == {"detail": "ADMIN_SHOWCASE_NOT_FOUND_ERROR"}


class TestAdminShowcaseDraftSettingsNoAuthAPI(APIFixture, StorageFixture):
    async def test_requires_authentication(self) -> None:
        await self.storage_helper.create_admin_showcase(
            id="showcase-api-settings-no-auth",
            owner_partner_id="partner-1",
            title="No auth showcase",
            draft_settings={"design_id": "classic"},
            published_snapshot={"id": "public-no-auth"},
        )
        await self.storage_helper.commit()

        response = self.no_auth_api.patch_admin_showcase_draft_settings(
            showcase_id="showcase-api-settings-no-auth",
            json={"designId": "modern"},
        )

        assert response.status_code == codes.UNAUTHORIZED
        assert response.json() == {"detail": "ADMIN_AUTHENTICATION_REQUIRED_ERROR"}

        persisted = await self.storage_helper.get_admin_showcase_draft(
            showcase_id="showcase-api-settings-no-auth"
        )
        assert persisted.settings == {"design_id": "classic"}
        assert persisted.published_snapshot == {"id": "public-no-auth"}

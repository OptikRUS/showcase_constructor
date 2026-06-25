from __future__ import annotations

from typing import TYPE_CHECKING

from httpx2 import codes

from src.tests.fixtures import APIFixture, FactoryFixture, StorageFixture

if TYPE_CHECKING:
    from src.core.showcases.schemas import JsonObject


class TestAdminShowcasePreviewAPI(APIFixture, FactoryFixture, StorageFixture):
    async def test_builds_mobile_preview_from_draft_without_publishing(self) -> None:
        published_snapshot: JsonObject = {
            "id": "public-preview-api",
            "settings": {"text_title": "Published title"},
            "blocks": [{"type": "offers", "title": "Published offers"}],
        }
        await self.storage_helper.create_admin_showcase(
            id="showcase-preview-api",
            owner_partner_id="partner-1",
            title="Preview showcase",
            draft_settings={
                "affiliate_id": "affiliate-preview-api",
                "type": "showcase",
                "tracking_domain": "draft-track.example.test",
                "design_id": "modern",
                "text_title": "Draft preview title",
                "text_subtitle": "Draft subtitle",
                "text_button": "Apply",
                "custom_head_code": "<script>window.previewHead = true</script>",
                "custom_body_code": "<noscript>preview body pixel</noscript>",
            },
            published_snapshot=published_snapshot,
        )
        await self.storage_helper.create_admin_showcase_draft_block(
            block=self.factory.admin_showcase_draft_block(
                id="block-preview-visible",
                showcase_id="showcase-preview-api",
                type="offers",
                order=10,
                visible=True,
                title="Draft offers",
            )
        )
        await self.storage_helper.create_admin_showcase_draft_block(
            block=self.factory.admin_showcase_draft_block(
                id="block-preview-hidden",
                showcase_id="showcase-preview-api",
                type="offers",
                order=20,
                visible=False,
                title="Hidden draft offers",
            )
        )
        await self.storage_helper.create_admin_showcase_draft_offer(
            offer=self.factory.admin_showcase_draft_offer(
                id="offer-preview-enabled",
                showcase_id="showcase-preview-api",
                block_id="block-preview-visible",
                enabled=True,
                manual_order=10,
                fields=[
                    {"key": "amount", "value": "100000", "visible": True},
                    {"key": "internal_score", "value": "A", "visible": False},
                ],
                categories=["cash", "cards"],
                display_name="Draft preview offer",
                site_name="Preview Bank",
                cpa_url="https://cpa.example.test/preview",
            )
        )
        await self.storage_helper.create_admin_showcase_draft_offer(
            offer=self.factory.admin_showcase_draft_offer(
                id="offer-preview-disabled",
                showcase_id="showcase-preview-api",
                block_id="block-preview-visible",
                enabled=False,
                manual_order=20,
                display_name="Disabled draft offer",
            )
        )
        await self.storage_helper.commit()

        response = self.api.preview_admin_showcase(
            showcase_id="showcase-preview-api",
            json={"mode": "mobile"},
        )

        assert response.status_code == codes.OK
        payload = response.json()
        assert payload["preview"] is True
        assert payload["mode"] == "mobile"
        assert payload["config"] == {
            "id": "preview-showcase-preview-api",
            "affiliateId": "affiliate-preview-api",
            "type": "showcase",
            "settings": {
                "trackingDomain": "draft-track.example.test",
                "designId": "modern",
                "colorScheme": None,
                "siteBackgroundColor": None,
                "widgetBackgroundColor": None,
                "offersBackgroundColor": None,
                "textColor": None,
                "uspTextColor": None,
                "ctaColor": None,
                "fontFamily": None,
                "textTitle": "Draft preview title",
                "textSubtitle": "Draft subtitle",
                "textButton": "Apply",
                "imageBannerDesktop": None,
                "imageBannerMobile": None,
                "imageBannerMini": None,
                "offersPlacement": None,
                "offersMobilePlacement": None,
                "uspPlacement": None,
                "alignment": None,
                "offsetHorizontal": None,
                "offsetVertical": None,
                "sortType": None,
                "sortPeriod": None,
            },
            "platform": {"id": "widgetmarket"},
            "constantUrlParamsTool": {"enabled": False, "params": []},
            "transferredUrlParamsTool": {"enabled": False, "params": []},
            "metricsTool": {"enabled": False, "metrics": []},
            "is_need_to_send_offers_display_and_positions": False,
            "blocks": [
                {
                    "type": "offers",
                    "title": "Draft offers",
                    "offers": [
                        {
                            "id": "offer-preview-enabled",
                            "offerCategories": ["cash", "cards"],
                            "logoUrl": "https://cdn.example.test/logo.png",
                            "roundedLogoUrl": "https://cdn.example.test/logo-rounded.png",
                            "name": "Draft preview offer",
                            "siteName": "Preview Bank",
                            "url": "https://cpa.example.test/preview",
                            "fields": [
                                {"key": "amount", "value": "100000", "visible": True}
                            ],
                        },
                    ],
                },
            ],
            "widgetInfo": None,
        }
        assert 'data-preview="true"' in payload["html"]
        assert 'data-preview-mode="mobile"' in payload["html"]
        assert "<script>window.previewHead = true</script>" in payload["html"]
        assert "<noscript>preview body pixel</noscript>" in payload["html"]

        persisted = await self.storage_helper.get_admin_showcase_draft(
            showcase_id="showcase-preview-api"
        )
        assert persisted.published_snapshot == published_snapshot
        audit_records = await self.storage_helper.list_showcase_audit_records(
            showcase_id="showcase-preview-api"
        )
        assert audit_records == []
        public_response = self.api.get_public_config(public_id="preview-showcase-preview-api")
        assert public_response.status_code == codes.NOT_FOUND

    async def test_rejects_unsupported_preview_mode(self) -> None:
        await self.storage_helper.create_admin_showcase(
            id="showcase-preview-api-invalid-mode",
            owner_partner_id="partner-1",
            title="Invalid mode preview showcase",
        )
        await self.storage_helper.commit()

        response = self.api.preview_admin_showcase(
            showcase_id="showcase-preview-api-invalid-mode",
            json={"mode": "tablet"},
        )

        assert response.status_code == codes.UNPROCESSABLE_ENTITY

    async def test_forbids_foreign_owner_preview_without_mutation(self) -> None:
        published_snapshot: JsonObject = {
            "id": "public-preview-foreign",
            "settings": {"text_title": "Published foreign title"},
        }
        await self.storage_helper.create_admin_showcase(
            id="showcase-preview-api-foreign",
            owner_partner_id="partner-2",
            title="Foreign preview showcase",
            draft_settings={"text_title": "Foreign draft title"},
            published_snapshot=published_snapshot,
        )
        await self.storage_helper.commit()

        response = self.api.preview_admin_showcase(
            showcase_id="showcase-preview-api-foreign",
            json={"mode": "desktop"},
        )

        assert response.status_code == codes.FORBIDDEN
        assert response.json() == {"detail": "SHOWCASE_ACCESS_DENIED_ERROR"}
        persisted = await self.storage_helper.get_admin_showcase_draft(
            showcase_id="showcase-preview-api-foreign"
        )
        assert persisted.published_snapshot == published_snapshot
        audit_records = await self.storage_helper.list_showcase_audit_records(
            showcase_id="showcase-preview-api-foreign"
        )
        assert audit_records == []

    def test_returns_not_found_for_missing_showcase(self) -> None:
        response = self.api.preview_admin_showcase(
            showcase_id="missing-showcase",
            json={"mode": "desktop"},
        )

        assert response.status_code == codes.NOT_FOUND
        assert response.json() == {"detail": "ADMIN_SHOWCASE_NOT_FOUND_ERROR"}


class TestAdminShowcasePreviewNoAuthAPI(APIFixture, StorageFixture):
    async def test_requires_authentication_without_mutation(self) -> None:
        published_snapshot: JsonObject = {
            "id": "public-preview-no-auth",
            "settings": {"text_title": "Published no-auth title"},
        }
        await self.storage_helper.create_admin_showcase(
            id="showcase-preview-api-no-auth",
            owner_partner_id="partner-1",
            title="No auth preview showcase",
            draft_settings={"text_title": "No auth draft title"},
            published_snapshot=published_snapshot,
        )
        await self.storage_helper.commit()

        response = self.no_auth_api.preview_admin_showcase(
            showcase_id="showcase-preview-api-no-auth",
            json={"mode": "mobile"},
        )

        assert response.status_code == codes.UNAUTHORIZED
        assert response.json() == {"detail": "ADMIN_AUTHENTICATION_REQUIRED_ERROR"}
        persisted = await self.storage_helper.get_admin_showcase_draft(
            showcase_id="showcase-preview-api-no-auth"
        )
        assert persisted.published_snapshot == published_snapshot
        audit_records = await self.storage_helper.list_showcase_audit_records(
            showcase_id="showcase-preview-api-no-auth"
        )
        assert audit_records == []

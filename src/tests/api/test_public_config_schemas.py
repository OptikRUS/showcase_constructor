import pytest
from pydantic import ValidationError

from src.api.public_config.schemas import PublicConfigResponse
from src.tests.fixtures import FactoryFixture


class TestPublicConfigResponseSchema(FactoryFixture):
    def test_serializes_widgetmarket_json(self) -> None:
        snapshot = self.factory.published_public_config_snapshot()

        payload = PublicConfigResponse.from_domain(snapshot=snapshot).model_dump(
            mode="json",
            by_alias=True,
        )

        assert payload == {
            "id": "public-showcase-1",
            "affiliateId": "affiliate-public-1",
            "type": "popup_offers",
            "settings": {
                "trackingDomain": "track.example.test",
                "designId": "default",
                "colorScheme": "light",
                "siteBackgroundColor": "#ffffff",
                "widgetBackgroundColor": "#f6f7f9",
                "offersBackgroundColor": "#ffffff",
                "textColor": "#101828",
                "uspTextColor": "#175cd3",
                "ctaColor": "#12b76a",
                "fontFamily": "Inter",
                "textTitle": "Best offers",
                "textSubtitle": "Choose an offer",
                "textButton": "Open",
                "imageBannerDesktop": "https://cdn.example.test/banner-desktop.png",
                "imageBannerMobile": "https://cdn.example.test/banner-mobile.png",
                "imageBannerMini": "https://cdn.example.test/banner-mini.png",
                "offersPlacement": "main",
                "offersMobilePlacement": "bottom",
                "uspPlacement": "above_offers",
                "alignment": "center",
                "offsetHorizontal": 16,
                "offsetVertical": 24,
                "sortType": "manual",
                "sortPeriod": "day",
            },
            "platform": {"id": "widgetmarket"},
            "blocks": [
                {
                    "type": "offers",
                    "title": "Offers",
                    "offers": [
                        {
                            "id": "offer-public-1",
                            "offerCategories": ["loans"],
                            "logoUrl": "https://cdn.example.test/logo.png",
                            "roundedLogoUrl": "https://cdn.example.test/logo-rounded.png",
                            "name": "Fast Loan",
                            "siteName": "Example Bank",
                            "url": "https://cpa.example.test/click",
                            "fields": [{"key": "amount", "value": "100000", "visible": True}],
                        },
                    ],
                },
            ],
            "widgetInfo": {
                "type": "popup_offers",
                "displayLimit": 3,
                "leadsIdEnabled": True,
                "offers": [
                    {
                        "id": "offer-public-1",
                        "offerCategories": ["loans"],
                        "logoUrl": "https://cdn.example.test/logo.png",
                        "roundedLogoUrl": "https://cdn.example.test/logo-rounded.png",
                        "name": "Fast Loan",
                        "siteName": "Example Bank",
                        "url": "https://cpa.example.test/click",
                        "fields": [{"key": "amount", "value": "100000", "visible": True}],
                    },
                ],
                "triggerGroups": [{"type": "page_open", "delaySecs": 2}],
            },
            "constantUrlParamsTool": {
                "enabled": True,
                "params": [{"key": "aff_sub7", "value": "showcase"}],
            },
            "transferredUrlParamsTool": {
                "enabled": True,
                "params": [{"key": "utm_source", "value": "aff_sub1"}],
            },
            "metricsTool": {"enabled": True, "metrics": ["ym:123", "pixel:abc"]},
            "is_need_to_send_offers_display_and_positions": True,
        }

    def test_serializes_widget_config_without_blocks(self) -> None:
        snapshot = self.factory.widget_public_config_snapshot()

        payload = PublicConfigResponse.from_domain(snapshot=snapshot).model_dump(
            mode="json",
            by_alias=True,
        )

        assert payload["type"] == "popup_offers"
        assert payload["blocks"] == []
        assert payload["widgetInfo"]["triggerGroups"] == [{"type": "page_open", "delaySecs": 2}]

    def test_serializes_showcase_config_without_widget_info(self) -> None:
        snapshot = self.factory.showcase_public_config_snapshot()

        payload = PublicConfigResponse.from_domain(snapshot=snapshot).model_dump(
            mode="json",
            by_alias=True,
        )

        assert payload["type"] == "showcase"
        assert payload["blocks"][0]["type"] == "offers"
        assert payload["widgetInfo"] is None

    def test_excludes_draft_and_private_fields(self) -> None:
        snapshot = self.factory.published_public_config_snapshot()

        serialized_payload = PublicConfigResponse.from_domain(snapshot=snapshot).model_dump_json(
            by_alias=True,
        )

        forbidden_field_names = (
            "ownerId",
            "tenantId",
            "draftVersion",
            "privateStats",
            "serviceSettings",
            "createdBy",
            "internalId",
        )
        for field_name in forbidden_field_names:
            assert field_name not in serialized_payload

    @pytest.mark.parametrize(
        ("field_name", "field_value"),
        [
            ("ownerId", "owner-admin-1"),
            ("tenantId", "tenant-private-1"),
            ("draftVersion", "draft-version-1"),
            ("privateStats", {"views": 42}),
            ("serviceSettings", {"token": "private-token"}),
            ("createdBy", "admin@example.test"),
        ],
    )
    def test_rejects_top_level_private_fields(
        self,
        field_name: str,
        field_value: object,
    ) -> None:
        snapshot = self.factory.published_public_config_snapshot()
        payload = PublicConfigResponse.from_domain(snapshot=snapshot).model_dump(
            mode="json",
            by_alias=True,
        )
        leaky_payload = {
            **payload,
            field_name: field_value,
        }

        with pytest.raises(ValidationError) as exc_info:
            PublicConfigResponse.model_validate(leaky_payload)

        assert (field_name,) in {tuple(error["loc"]) for error in exc_info.value.errors()}

    def test_rejects_widget_offer_private_fields(self) -> None:
        snapshot = self.factory.published_public_config_snapshot()
        payload = PublicConfigResponse.from_domain(snapshot=snapshot).model_dump(
            mode="json",
            by_alias=True,
        )
        leaky_payload = {
            **payload,
            "widgetInfo": {
                **payload["widgetInfo"],
                "offers": [
                    {
                        **payload["widgetInfo"]["offers"][0],
                        "internalId": "offer-internal-1",
                    },
                ],
            },
        }

        with pytest.raises(ValidationError) as exc_info:
            PublicConfigResponse.model_validate(leaky_payload)

        assert ("widgetInfo", "offers", 0, "internalId") in {
            tuple(error["loc"]) for error in exc_info.value.errors()
        }

    def test_rejects_block_offer_private_fields(self) -> None:
        snapshot = self.factory.published_public_config_snapshot()
        payload = PublicConfigResponse.from_domain(snapshot=snapshot).model_dump(
            mode="json",
            by_alias=True,
        )
        leaky_payload = {
            **payload,
            "blocks": [
                {
                    **payload["blocks"][0],
                    "offers": [
                        {
                            **payload["blocks"][0]["offers"][0],
                            "internalId": "block-offer-internal-1",
                        },
                    ],
                },
            ],
        }

        with pytest.raises(ValidationError) as exc_info:
            PublicConfigResponse.model_validate(leaky_payload)

        assert ("blocks", 0, "offers", 0, "internalId") in {
            tuple(error["loc"]) for error in exc_info.value.errors()
        }

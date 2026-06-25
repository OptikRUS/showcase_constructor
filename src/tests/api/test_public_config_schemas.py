from dataclasses import replace

import pytest
from pydantic import ValidationError

from src.api.public_config.schemas import PublicConfigResponse
from src.core.public_config.schemas import PublicOfferField
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
            "customHeadCode": "<script>window.publicHead = true</script>",
            "customBodyCode": "<noscript>public body pixel</noscript>",
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
        assert snapshot.widget_info is not None
        published_offer = snapshot.widget_info.offers[0]
        offer_with_hidden_field = replace(
            published_offer,
            fields=(
                *published_offer.fields,
                PublicOfferField(
                    key="draftSecret",
                    value="hidden-draft-value",
                    visible=False,
                ),
            ),
        )
        snapshot_with_hidden_field = replace(
            snapshot,
            blocks=(
                replace(
                    snapshot.blocks[0],
                    offers=(offer_with_hidden_field,),
                ),
            ),
            widget_info=replace(
                snapshot.widget_info,
                offers=(offer_with_hidden_field,),
            ),
        )

        serialized_payload = PublicConfigResponse.from_domain(
            snapshot=snapshot_with_hidden_field,
        ).model_dump_json(by_alias=True)

        forbidden_field_names = (
            "ownerId",
            "tenantId",
            "draftVersion",
            "privateStats",
            "serviceSettings",
            "createdBy",
            "internalId",
            "draftSecret",
            "hidden-draft-value",
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
            ("customCodeReviewMetadata", {"status": "private"}),
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

    @pytest.mark.parametrize(
        ("field_name", "field_value"),
        [
            ("enabled", False),
            ("manualOrder", 20),
            ("blockId", "draft-block-1"),
            ("ctaText", "Private CTA"),
            ("uspText", "Private USP"),
            ("legalEntity", "Private Entity LLC"),
            ("inn", "1234567890"),
            ("erid", "draft-erid"),
        ],
    )
    def test_rejects_widget_offer_draft_fields(
        self,
        field_name: str,
        field_value: object,
    ) -> None:
        snapshot = self.factory.published_public_config_snapshot()
        payload = PublicConfigResponse.from_domain(snapshot=snapshot).model_dump(
            mode="json",
            by_alias=True,
        )
        assert payload["widgetInfo"] is not None
        leaky_payload = {
            **payload,
            "widgetInfo": {
                **payload["widgetInfo"],
                "offers": [
                    {
                        **payload["widgetInfo"]["offers"][0],
                        field_name: field_value,
                    },
                ],
            },
        }

        with pytest.raises(ValidationError) as exc_info:
            PublicConfigResponse.model_validate(leaky_payload)

        assert ("widgetInfo", "offers", 0, field_name) in {
            tuple(error["loc"]) for error in exc_info.value.errors()
        }

    @pytest.mark.parametrize(
        ("field_name", "field_value"),
        [
            ("fallbackText", "Draft fallback"),
            ("metaTitle", "Draft meta title"),
            ("metaDescription", "Draft meta description"),
        ],
    )
    def test_rejects_draft_only_settings_fields(
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
            "settings": {
                **payload["settings"],
                field_name: field_value,
            },
        }

        with pytest.raises(ValidationError) as exc_info:
            PublicConfigResponse.model_validate(leaky_payload)

        assert ("settings", field_name) in {
            tuple(error["loc"]) for error in exc_info.value.errors()
        }

    @pytest.mark.parametrize(
        ("field_name", "field_value"),
        [
            ("id", "draft-block-1"),
            ("order", 10),
            ("visible", False),
            ("subtitle", "Draft subtitle"),
            ("desktopSettings", {"columns": 3}),
            ("mobileSettings", {"columns": 1}),
            ("data", {"html": "<section>Draft</section>"}),
        ],
    )
    def test_rejects_block_draft_fields(
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
            "blocks": [
                {
                    **payload["blocks"][0],
                    field_name: field_value,
                },
            ],
        }

        with pytest.raises(ValidationError) as exc_info:
            PublicConfigResponse.model_validate(leaky_payload)

        assert ("blocks", 0, field_name) in {
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

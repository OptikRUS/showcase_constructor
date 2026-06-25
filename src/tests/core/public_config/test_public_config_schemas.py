from dataclasses import fields, is_dataclass

from src.core.public_config.schemas import (
    PublicBlock,
    PublicConfigSettings,
    PublicMetricsTool,
    PublicOffer,
    PublicOfferField,
    PublicPlatform,
    PublicTriggerGroup,
    PublicUrlParam,
    PublicUrlParamsTool,
    PublicWidgetInfo,
    PublishedPublicConfigSnapshot,
)
from src.tests.fixtures import FactoryFixture

PRIVATE_FIELD_NAMES = {
    "created_by",
    "draft_version",
    "internal_id",
    "owner_id",
    "private_stats",
    "service_settings",
    "tenant_id",
}


class TestPublishedPublicConfigSnapshot(FactoryFixture):
    def test_public_shape_contains_widgetmarket_fields(self) -> None:
        snapshot = self.factory.published_public_config_snapshot()
        assert snapshot.widget_info is not None

        offer = snapshot.widget_info.offers[0]
        offer_field = offer.fields[0]
        trigger_group = snapshot.widget_info.trigger_groups[0]

        assert isinstance(snapshot, PublishedPublicConfigSnapshot)
        assert snapshot.id == "public-showcase-1"
        assert snapshot.affiliate_id == "affiliate-public-1"
        assert snapshot.type == "popup_offers"
        assert snapshot.settings.tracking_domain == "track.example.test"
        assert snapshot.settings.offers_mobile_placement == "bottom"
        assert snapshot.platform.id == "widgetmarket"
        assert snapshot.blocks[0].type == "offers"
        assert snapshot.blocks[0].offers == (offer,)
        assert snapshot.constant_url_params_tool.params[0].key == "aff_sub7"
        assert snapshot.transferred_url_params_tool.params[0].value == "aff_sub1"
        assert snapshot.metrics_tool.metrics == ("ym:123", "pixel:abc")
        assert snapshot.is_need_to_send_offers_display_and_positions is True
        assert snapshot.custom_head_code == "<script>window.publicHead = true</script>"
        assert snapshot.custom_body_code == "<noscript>public body pixel</noscript>"
        assert offer.id == "offer-public-1"
        assert offer.offer_categories == ("loans",)
        assert offer_field == PublicOfferField(key="amount", value="100000", visible=True)
        assert trigger_group.type == "page_open"
        assert trigger_group.delay_secs == 2

        public_schema_types = (
            PublishedPublicConfigSnapshot,
            PublicConfigSettings,
            PublicPlatform,
            PublicBlock,
            PublicWidgetInfo,
            PublicOffer,
            PublicOfferField,
            PublicTriggerGroup,
            PublicUrlParamsTool,
            PublicUrlParam,
            PublicMetricsTool,
        )
        for schema_type in public_schema_types:
            assert is_dataclass(schema_type)
            public_field_names = {field.name for field in fields(schema_type)}
            assert not public_field_names & PRIVATE_FIELD_NAMES

    def test_widget_public_shape_can_omit_blocks(self) -> None:
        snapshot = self.factory.widget_public_config_snapshot()

        assert snapshot.type == "popup_offers"
        assert snapshot.blocks == ()
        assert snapshot.widget_info is not None
        assert snapshot.widget_info.trigger_groups[0].type == "page_open"

    def test_showcase_public_shape_can_omit_widget_info(self) -> None:
        snapshot = self.factory.showcase_public_config_snapshot()

        assert snapshot.type == "showcase"
        assert snapshot.blocks[0].type == "offers"
        assert snapshot.widget_info is None

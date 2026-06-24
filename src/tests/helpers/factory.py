from typing import NotRequired, TypedDict, Unpack

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
from src.core.showcases.schemas import (
    AdminShowcase,
    AdminShowcaseDraftBlock,
    AdminShowcaseDraftBlockCreateParams,
    AdminShowcaseUpdateParams,
    JsonObject,
)


class AdminShowcaseDraftBlockFactoryKwargs(TypedDict):
    id: NotRequired[str]
    showcase_id: NotRequired[str]
    type: NotRequired[str]
    order: NotRequired[int]
    visible: NotRequired[bool]
    title: NotRequired[str | None]
    subtitle: NotRequired[str | None]
    desktop_settings: NotRequired[JsonObject]
    mobile_settings: NotRequired[JsonObject]
    data: NotRequired[JsonObject]


class AdminShowcaseDraftBlockCreateParamsFactoryKwargs(TypedDict):
    type: NotRequired[str]
    order: NotRequired[int]
    visible: NotRequired[bool]
    title: NotRequired[str | None]
    subtitle: NotRequired[str | None]
    desktop_settings: NotRequired[JsonObject]
    mobile_settings: NotRequired[JsonObject]
    data: NotRequired[JsonObject]


class FactoryHelper:
    @classmethod
    def admin_showcase(
        cls,
        *,
        id: str = "showcase-1",
        owner_partner_id: str = "partner-1",
        title: str = "Test showcase",
    ) -> AdminShowcase:
        return AdminShowcase(
            id=id,
            owner_partner_id=owner_partner_id,
            title=title,
        )

    @classmethod
    def admin_showcase_update_params(
        cls,
        *,
        title: str = "Updated showcase",
    ) -> AdminShowcaseUpdateParams:
        return AdminShowcaseUpdateParams(title=title)

    @classmethod
    def admin_showcase_draft_block(
        cls,
        **kwargs: Unpack[AdminShowcaseDraftBlockFactoryKwargs],
    ) -> AdminShowcaseDraftBlock:
        return AdminShowcaseDraftBlock(
            id=kwargs.get("id", "block-1"),
            showcase_id=kwargs.get("showcase_id", "showcase-1"),
            type=kwargs.get("type", "offers"),
            order=kwargs.get("order", 10),
            visible=kwargs.get("visible", True),
            title=kwargs.get("title", "Offers"),
            subtitle=kwargs.get("subtitle", "Choose an offer"),
            desktop_settings=kwargs.get("desktop_settings", {}),
            mobile_settings=kwargs.get("mobile_settings", {}),
            data=kwargs.get("data", {}),
        )

    @classmethod
    def admin_showcase_draft_block_create_params(
        cls,
        **kwargs: Unpack[AdminShowcaseDraftBlockCreateParamsFactoryKwargs],
    ) -> AdminShowcaseDraftBlockCreateParams:
        return AdminShowcaseDraftBlockCreateParams(
            type=kwargs.get("type", "offers"),
            order=kwargs.get("order", 10),
            visible=kwargs.get("visible", True),
            title=kwargs.get("title", "Offers"),
            subtitle=kwargs.get("subtitle", "Choose an offer"),
            desktop_settings=kwargs.get("desktop_settings", {}),
            mobile_settings=kwargs.get("mobile_settings", {}),
            data=kwargs.get("data", {}),
        )

    @classmethod
    def published_public_config_snapshot(cls) -> PublishedPublicConfigSnapshot:
        offer_field = PublicOfferField(key="amount", value="100000", visible=True)
        offer = PublicOffer(
            id="offer-public-1",
            offer_categories=("loans",),
            logo_url="https://cdn.example.test/logo.png",
            rounded_logo_url="https://cdn.example.test/logo-rounded.png",
            name="Fast Loan",
            site_name="Example Bank",
            url="https://cpa.example.test/click",
            fields=(offer_field,),
        )

        return PublishedPublicConfigSnapshot(
            id="public-showcase-1",
            affiliate_id="affiliate-public-1",
            type="popup_offers",
            settings=PublicConfigSettings(
                tracking_domain="track.example.test",
                design_id="default",
                color_scheme="light",
                site_background_color="#ffffff",
                widget_background_color="#f6f7f9",
                offers_background_color="#ffffff",
                text_color="#101828",
                usp_text_color="#175cd3",
                cta_color="#12b76a",
                font_family="Inter",
                text_title="Best offers",
                text_subtitle="Choose an offer",
                text_button="Open",
                image_banner_desktop="https://cdn.example.test/banner-desktop.png",
                image_banner_mobile="https://cdn.example.test/banner-mobile.png",
                image_banner_mini="https://cdn.example.test/banner-mini.png",
                offers_placement="main",
                offers_mobile_placement="bottom",
                usp_placement="above_offers",
                alignment="center",
                offset_horizontal=16,
                offset_vertical=24,
                sort_type="manual",
                sort_period="day",
            ),
            platform=PublicPlatform(id="widgetmarket"),
            blocks=(PublicBlock(type="offers", title="Offers", offers=(offer,)),),
            widget_info=PublicWidgetInfo(
                type="popup_offers",
                display_limit=3,
                leads_id_enabled=True,
                offers=(offer,),
                trigger_groups=(PublicTriggerGroup(type="page_open", delay_secs=2),),
            ),
            constant_url_params_tool=PublicUrlParamsTool(
                enabled=True,
                params=(PublicUrlParam(key="aff_sub7", value="showcase"),),
            ),
            transferred_url_params_tool=PublicUrlParamsTool(
                enabled=True,
                params=(PublicUrlParam(key="utm_source", value="aff_sub1"),),
            ),
            metrics_tool=PublicMetricsTool(enabled=True, metrics=("ym:123", "pixel:abc")),
            is_need_to_send_offers_display_and_positions=True,
        )

    @classmethod
    def widget_public_config_snapshot(cls) -> PublishedPublicConfigSnapshot:
        snapshot = cls.published_public_config_snapshot()
        return PublishedPublicConfigSnapshot(
            id=snapshot.id,
            affiliate_id=snapshot.affiliate_id,
            type="popup_offers",
            settings=snapshot.settings,
            platform=snapshot.platform,
            widget_info=snapshot.widget_info,
            constant_url_params_tool=snapshot.constant_url_params_tool,
            transferred_url_params_tool=snapshot.transferred_url_params_tool,
            metrics_tool=snapshot.metrics_tool,
            is_need_to_send_offers_display_and_positions=(
                snapshot.is_need_to_send_offers_display_and_positions
            ),
        )

    @classmethod
    def showcase_public_config_snapshot(cls) -> PublishedPublicConfigSnapshot:
        snapshot = cls.published_public_config_snapshot()
        return PublishedPublicConfigSnapshot(
            id=snapshot.id,
            affiliate_id=snapshot.affiliate_id,
            type="showcase",
            settings=snapshot.settings,
            platform=snapshot.platform,
            blocks=snapshot.blocks,
            widget_info=None,
            constant_url_params_tool=snapshot.constant_url_params_tool,
            transferred_url_params_tool=snapshot.transferred_url_params_tool,
            metrics_tool=snapshot.metrics_tool,
            is_need_to_send_offers_display_and_positions=(
                snapshot.is_need_to_send_offers_display_and_positions
            ),
        )

from datetime import UTC, datetime
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
    AdminShowcaseDraft,
    AdminShowcaseDraftBlock,
    AdminShowcaseDraftBlockCreateParams,
    AdminShowcaseDraftBlockPatchParams,
    AdminShowcaseDraftOffer,
    AdminShowcaseDraftOfferCreateParams,
    AdminShowcaseDraftOfferField,
    AdminShowcaseDraftOfferPatchParams,
    AdminShowcaseDraftSettingsPatchParams,
    AdminShowcasePublication,
    AdminShowcasePublicationState,
    AdminShowcaseUpdateParams,
    JsonObject,
    JsonValue,
    PublishedShowcaseSnapshot,
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


class AdminShowcaseDraftBlockPatchParamsFactoryKwargs(TypedDict):
    values: NotRequired[JsonObject]


class AdminShowcaseDraftOfferFactoryKwargs(TypedDict):
    id: NotRequired[str]
    showcase_id: NotRequired[str]
    block_id: NotRequired[str | None]
    enabled: NotRequired[bool]
    manual_order: NotRequired[int]
    cta_text: NotRequired[str | None]
    usp_text: NotRequired[str | None]
    fields: NotRequired[list[AdminShowcaseDraftOfferField]]
    categories: NotRequired[list[JsonValue]]
    logo_url: NotRequired[str | None]
    rounded_logo_url: NotRequired[str | None]
    display_name: NotRequired[str | None]
    site_name: NotRequired[str | None]
    cpa_url: NotRequired[str | None]
    legal_entity: NotRequired[str | None]
    inn: NotRequired[str | None]
    erid: NotRequired[str | None]
    data: NotRequired[JsonObject]


class AdminShowcaseDraftOfferCreateParamsFactoryKwargs(TypedDict):
    block_id: NotRequired[str | None]
    enabled: NotRequired[bool]
    manual_order: NotRequired[int]
    cta_text: NotRequired[str | None]
    usp_text: NotRequired[str | None]
    fields: NotRequired[list[AdminShowcaseDraftOfferField]]
    categories: NotRequired[list[JsonValue]]
    logo_url: NotRequired[str | None]
    rounded_logo_url: NotRequired[str | None]
    display_name: NotRequired[str | None]
    site_name: NotRequired[str | None]
    cpa_url: NotRequired[str | None]
    legal_entity: NotRequired[str | None]
    inn: NotRequired[str | None]
    erid: NotRequired[str | None]
    data: NotRequired[JsonObject]


class AdminShowcaseDraftOfferPatchParamsFactoryKwargs(TypedDict):
    values: NotRequired[JsonObject]


class AdminShowcaseDraftFactoryKwargs(TypedDict):
    id: NotRequired[str]
    owner_partner_id: NotRequired[str]
    title: NotRequired[str]
    settings: NotRequired[JsonObject]
    published_snapshot: NotRequired[JsonObject | None]
    custom_code_warning: NotRequired[str | None]


class AdminShowcaseDraftSettingsPatchParamsFactoryKwargs(TypedDict):
    settings: NotRequired[JsonObject]


class PublishedShowcaseSnapshotFactoryKwargs(TypedDict):
    showcase_id: NotRequired[str]
    public_id: NotRequired[str]
    version: NotRequired[int]
    snapshot: NotRequired[JsonObject | None]
    created_by_user_id: NotRequired[str]
    created_by_partner_id: NotRequired[str]
    created_at: NotRequired[datetime | None]


class PublishedPublicConfigSnapshotPayloadFactoryKwargs(TypedDict):
    public_id: NotRequired[str]
    affiliate_id: NotRequired[str]
    type: NotRequired[str]
    text_title: NotRequired[str]
    custom_head_code: NotRequired[str | None]
    custom_body_code: NotRequired[str | None]
    extra: NotRequired[JsonObject | None]


class FactoryHelper:
    @classmethod
    def admin_showcase(
        cls,
        *,
        id: str = "showcase-1",
        owner_partner_id: str = "partner-1",
        title: str = "Test showcase",
        public_id: str | None = None,
        publication_version: int = 0,
        published_snapshot: JsonObject | None = None,
    ) -> AdminShowcase:
        return AdminShowcase(
            id=id,
            owner_partner_id=owner_partner_id,
            title=title,
            public_id=public_id,
            publication_version=publication_version,
            published_snapshot=published_snapshot,
        )

    @classmethod
    def admin_showcase_update_params(
        cls,
        *,
        title: str = "Updated showcase",
    ) -> AdminShowcaseUpdateParams:
        return AdminShowcaseUpdateParams(title=title)

    @classmethod
    def admin_showcase_draft(
        cls,
        **kwargs: Unpack[AdminShowcaseDraftFactoryKwargs],
    ) -> AdminShowcaseDraft:
        return AdminShowcaseDraft(
            id=kwargs.get("id", "showcase-1"),
            owner_partner_id=kwargs.get("owner_partner_id", "partner-1"),
            title=kwargs.get("title", "Test showcase"),
            settings=kwargs.get("settings", {}),
            published_snapshot=kwargs.get("published_snapshot"),
            custom_code_warning=kwargs.get("custom_code_warning"),
        )

    @classmethod
    def admin_showcase_draft_settings_patch_params(
        cls,
        **kwargs: Unpack[AdminShowcaseDraftSettingsPatchParamsFactoryKwargs],
    ) -> AdminShowcaseDraftSettingsPatchParams:
        return AdminShowcaseDraftSettingsPatchParams(settings=kwargs.get("settings", {}))

    @classmethod
    def admin_showcase_publication(
        cls,
        *,
        id: str = "showcase-1",
        public_id: str = "public-showcase-1",
        version: int = 1,
        published: bool = True,
    ) -> AdminShowcasePublication:
        return AdminShowcasePublication(
            id=id,
            public_id=public_id,
            version=version,
            published=published,
        )

    @classmethod
    def admin_showcase_publication_state(
        cls,
        *,
        id: str = "showcase-1",
        public_id: str | None = "public-showcase-1",
        version: int = 1,
        active: bool = True,
        snapshot: JsonObject | None = None,
    ) -> AdminShowcasePublicationState:
        return AdminShowcasePublicationState(
            id=id,
            public_id=public_id,
            version=version,
            active=active,
            snapshot=snapshot,
        )

    @classmethod
    def published_showcase_snapshot(
        cls,
        **kwargs: Unpack[PublishedShowcaseSnapshotFactoryKwargs],
    ) -> PublishedShowcaseSnapshot:
        public_id = kwargs.get("public_id", "public-showcase-1")
        return PublishedShowcaseSnapshot(
            showcase_id=kwargs.get("showcase_id", "showcase-1"),
            public_id=public_id,
            version=kwargs.get("version", 1),
            snapshot=kwargs.get("snapshot") or {"id": public_id},
            created_by_user_id=kwargs.get("created_by_user_id", "admin-user-1"),
            created_by_partner_id=kwargs.get("created_by_partner_id", "partner-1"),
            created_at=kwargs.get("created_at") or datetime(2026, 1, 1, tzinfo=UTC),
        )

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
    def admin_showcase_draft_block_patch_params(
        cls,
        **kwargs: Unpack[AdminShowcaseDraftBlockPatchParamsFactoryKwargs],
    ) -> AdminShowcaseDraftBlockPatchParams:
        return AdminShowcaseDraftBlockPatchParams(values=kwargs.get("values", {}))

    @classmethod
    def admin_showcase_draft_offer(
        cls,
        **kwargs: Unpack[AdminShowcaseDraftOfferFactoryKwargs],
    ) -> AdminShowcaseDraftOffer:
        return AdminShowcaseDraftOffer(
            id=kwargs.get("id", "offer-1"),
            showcase_id=kwargs.get("showcase_id", "showcase-1"),
            block_id=kwargs.get("block_id", "block-1"),
            enabled=kwargs.get("enabled", True),
            manual_order=kwargs.get("manual_order", 10),
            cta_text=kwargs.get("cta_text", "Open offer"),
            usp_text=kwargs.get("usp_text", "Fast approval"),
            fields=kwargs.get("fields", []),
            categories=kwargs.get("categories", []),
            logo_url=kwargs.get("logo_url", "https://cdn.example.test/logo.png"),
            rounded_logo_url=kwargs.get(
                "rounded_logo_url",
                "https://cdn.example.test/logo-rounded.png",
            ),
            display_name=kwargs.get("display_name", "Fast Loan"),
            site_name=kwargs.get("site_name", "Example Bank"),
            cpa_url=kwargs.get("cpa_url", "https://cpa.example.test/click"),
            legal_entity=kwargs.get("legal_entity", "Example Bank LLC"),
            inn=kwargs.get("inn", "1234567890"),
            erid=kwargs.get("erid"),
            data=kwargs.get("data", {}),
        )

    @classmethod
    def admin_showcase_draft_offer_create_params(
        cls,
        **kwargs: Unpack[AdminShowcaseDraftOfferCreateParamsFactoryKwargs],
    ) -> AdminShowcaseDraftOfferCreateParams:
        return AdminShowcaseDraftOfferCreateParams(
            block_id=kwargs.get("block_id", "block-1"),
            enabled=kwargs.get("enabled", True),
            manual_order=kwargs.get("manual_order", 10),
            cta_text=kwargs.get("cta_text", "Open offer"),
            usp_text=kwargs.get("usp_text", "Fast approval"),
            fields=kwargs.get("fields", []),
            categories=kwargs.get("categories", []),
            logo_url=kwargs.get("logo_url", "https://cdn.example.test/logo.png"),
            rounded_logo_url=kwargs.get(
                "rounded_logo_url",
                "https://cdn.example.test/logo-rounded.png",
            ),
            display_name=kwargs.get("display_name", "Fast Loan"),
            site_name=kwargs.get("site_name", "Example Bank"),
            cpa_url=kwargs.get("cpa_url", "https://cpa.example.test/click"),
            legal_entity=kwargs.get("legal_entity", "Example Bank LLC"),
            inn=kwargs.get("inn", "1234567890"),
            erid=kwargs.get("erid"),
            data=kwargs.get("data", {}),
        )

    @classmethod
    def admin_showcase_draft_offer_patch_params(
        cls,
        **kwargs: Unpack[AdminShowcaseDraftOfferPatchParamsFactoryKwargs],
    ) -> AdminShowcaseDraftOfferPatchParams:
        return AdminShowcaseDraftOfferPatchParams(values=kwargs.get("values", {}))

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
            custom_head_code="<script>window.publicHead = true</script>",
            custom_body_code="<noscript>public body pixel</noscript>",
        )

    @classmethod
    def published_public_config_snapshot_payload(
        cls,
        **kwargs: Unpack[PublishedPublicConfigSnapshotPayloadFactoryKwargs],
    ) -> JsonObject:
        public_id = kwargs.get("public_id", "public-showcase-1")
        payload: JsonObject = {
            "id": public_id,
            "affiliate_id": kwargs.get("affiliate_id", "affiliate-public-1"),
            "type": kwargs.get("type", "popup_offers"),
            "settings": {
                "tracking_domain": "track.example.test",
                "design_id": "default",
                "color_scheme": "light",
                "site_background_color": "#ffffff",
                "widget_background_color": "#f6f7f9",
                "offers_background_color": "#ffffff",
                "text_color": "#101828",
                "usp_text_color": "#175cd3",
                "cta_color": "#12b76a",
                "font_family": "Inter",
                "text_title": kwargs.get("text_title", "Best offers"),
                "text_subtitle": "Choose an offer",
                "text_button": "Open",
                "image_banner_desktop": "https://cdn.example.test/banner-desktop.png",
                "image_banner_mobile": "https://cdn.example.test/banner-mobile.png",
                "image_banner_mini": "https://cdn.example.test/banner-mini.png",
                "offers_placement": "main",
                "offers_mobile_placement": "bottom",
                "usp_placement": "above_offers",
                "alignment": "center",
                "offset_horizontal": 16,
                "offset_vertical": 24,
                "sort_type": "manual",
                "sort_period": "day",
            },
            "platform": {"id": "widgetmarket"},
            "blocks": [
                {
                    "type": "offers",
                    "title": "Offers",
                    "offers": [
                        {
                            "id": "offer-public-1",
                            "offer_categories": ["loans"],
                            "logo_url": "https://cdn.example.test/logo.png",
                            "rounded_logo_url": "https://cdn.example.test/logo-rounded.png",
                            "name": "Fast Loan",
                            "site_name": "Example Bank",
                            "url": "https://cpa.example.test/click",
                            "fields": [
                                {"key": "amount", "value": "100000", "visible": True},
                                {
                                    "key": "draftSecret",
                                    "value": "hidden-draft-value",
                                    "visible": False,
                                },
                            ],
                        }
                    ],
                }
            ],
            "widget_info": {
                "type": "popup_offers",
                "display_limit": 3,
                "leads_id_enabled": True,
                "offers": [
                    {
                        "id": "offer-public-1",
                        "offer_categories": ["loans"],
                        "logo_url": "https://cdn.example.test/logo.png",
                        "rounded_logo_url": "https://cdn.example.test/logo-rounded.png",
                        "name": "Fast Loan",
                        "site_name": "Example Bank",
                        "url": "https://cpa.example.test/click",
                        "fields": [
                            {"key": "amount", "value": "100000", "visible": True},
                            {
                                "key": "draftSecret",
                                "value": "hidden-draft-value",
                                "visible": False,
                            },
                        ],
                    },
                ],
                "trigger_groups": [{"type": "page_open", "delay_secs": 2}],
            },
            "constant_url_params_tool": {
                "enabled": True,
                "params": [{"key": "aff_sub7", "value": "showcase"}],
            },
            "transferred_url_params_tool": {
                "enabled": True,
                "params": [{"key": "utm_source", "value": "aff_sub1"}],
            },
            "metrics_tool": {"enabled": True, "metrics": ["ym:123", "pixel:abc"]},
            "is_need_to_send_offers_display_and_positions": True,
        }
        custom_head_code = kwargs.get(
            "custom_head_code",
            "<script>window.publicHead = true</script>",
        )
        custom_body_code = kwargs.get(
            "custom_body_code",
            "<noscript>public body pixel</noscript>",
        )
        if custom_head_code is not None:
            payload["custom_head_code"] = custom_head_code
        if custom_body_code is not None:
            payload["custom_body_code"] = custom_body_code

        extra = kwargs.get("extra")
        if extra is not None:
            payload.update(extra)

        return payload

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
            custom_head_code=snapshot.custom_head_code,
            custom_body_code=snapshot.custom_body_code,
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
            custom_head_code=snapshot.custom_head_code,
            custom_body_code=snapshot.custom_body_code,
        )

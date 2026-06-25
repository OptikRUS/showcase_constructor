from dataclasses import dataclass


@dataclass(frozen=True, slots=True, kw_only=True)
class PublicConfigSettings:
    tracking_domain: str | None = None
    design_id: str | None = None
    color_scheme: str | None = None
    site_background_color: str | None = None
    widget_background_color: str | None = None
    offers_background_color: str | None = None
    text_color: str | None = None
    usp_text_color: str | None = None
    cta_color: str | None = None
    font_family: str | None = None
    text_title: str | None = None
    text_subtitle: str | None = None
    text_button: str | None = None
    image_banner_desktop: str | None = None
    image_banner_mobile: str | None = None
    image_banner_mini: str | None = None
    offers_placement: str | None = None
    offers_mobile_placement: str | None = None
    usp_placement: str | None = None
    alignment: str | None = None
    offset_horizontal: int | None = None
    offset_vertical: int | None = None
    sort_type: str | None = None
    sort_period: str | None = None


@dataclass(frozen=True, slots=True, kw_only=True)
class PublicPlatform:
    id: str


@dataclass(frozen=True, slots=True, kw_only=True)
class PublicOfferField:
    key: str
    value: str
    visible: bool


@dataclass(frozen=True, slots=True, kw_only=True)
class PublicOffer:
    id: str
    offer_categories: tuple[str, ...]
    logo_url: str
    rounded_logo_url: str
    name: str
    site_name: str
    url: str
    fields: tuple[PublicOfferField, ...]


@dataclass(frozen=True, slots=True, kw_only=True)
class PublicBlock:
    type: str
    title: str | None = None
    offers: tuple[PublicOffer, ...] = ()


@dataclass(frozen=True, slots=True, kw_only=True)
class PublicTriggerGroup:
    type: str
    delay_secs: int | None = None


@dataclass(frozen=True, slots=True, kw_only=True)
class PublicWidgetInfo:
    type: str
    display_limit: int
    leads_id_enabled: bool
    offers: tuple[PublicOffer, ...]
    trigger_groups: tuple[PublicTriggerGroup, ...]


@dataclass(frozen=True, slots=True, kw_only=True)
class PublicUrlParam:
    key: str
    value: str


@dataclass(frozen=True, slots=True, kw_only=True)
class PublicUrlParamsTool:
    enabled: bool
    params: tuple[PublicUrlParam, ...]


@dataclass(frozen=True, slots=True, kw_only=True)
class PublicMetricsTool:
    enabled: bool
    metrics: tuple[str, ...]


@dataclass(frozen=True, slots=True, kw_only=True)
class PublishedPublicConfigSnapshot:
    id: str
    affiliate_id: str
    type: str
    settings: PublicConfigSettings
    platform: PublicPlatform
    constant_url_params_tool: PublicUrlParamsTool
    transferred_url_params_tool: PublicUrlParamsTool
    metrics_tool: PublicMetricsTool
    is_need_to_send_offers_display_and_positions: bool
    blocks: tuple[PublicBlock, ...] = ()
    widget_info: PublicWidgetInfo | None = None
    custom_head_code: str | None = None
    custom_body_code: str | None = None

from __future__ import annotations

from html import escape
from typing import TYPE_CHECKING

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

if TYPE_CHECKING:
    from src.core.showcases.schemas import (
        AdminShowcaseDraft,
        AdminShowcaseDraftBlock,
        AdminShowcaseDraftOffer,
        AdminShowcasePreviewMode,
        JsonObject,
        JsonValue,
    )

WIDGET_CONFIG_TYPES = frozenset({"banner", "popup_offers", "widget"})


def build_preview_public_config(
    *,
    draft: AdminShowcaseDraft,
    blocks: list[AdminShowcaseDraftBlock],
    offers: list[AdminShowcaseDraftOffer],
) -> PublishedPublicConfigSnapshot:
    return _build_public_config(
        draft=draft,
        blocks=blocks,
        offers=offers,
        snapshot_id=f"preview-{draft.id}",
        affiliate_id=_str_setting(settings=draft.settings, key="affiliate_id")
        or f"preview-{draft.id}",
    )


def build_published_public_config(
    *,
    draft: AdminShowcaseDraft,
    blocks: list[AdminShowcaseDraftBlock],
    offers: list[AdminShowcaseDraftOffer],
    public_id: str,
) -> PublishedPublicConfigSnapshot:
    return _build_public_config(
        draft=draft,
        blocks=blocks,
        offers=offers,
        snapshot_id=public_id,
        affiliate_id=_str_setting(settings=draft.settings, key="affiliate_id") or public_id,
    )


def public_config_snapshot_to_json(
    *,
    snapshot: PublishedPublicConfigSnapshot,
    settings: JsonObject,
) -> JsonObject:
    data: JsonObject = {
        "id": snapshot.id,
        "affiliate_id": snapshot.affiliate_id,
        "type": snapshot.type,
        "settings": _settings_to_json(settings=snapshot.settings),
        "platform": {"id": snapshot.platform.id},
        "constant_url_params_tool": _url_params_tool_to_json(
            tool=snapshot.constant_url_params_tool
        ),
        "transferred_url_params_tool": _url_params_tool_to_json(
            tool=snapshot.transferred_url_params_tool
        ),
        "metrics_tool": {
            "enabled": snapshot.metrics_tool.enabled,
            "metrics": list(snapshot.metrics_tool.metrics),
        },
        "is_need_to_send_offers_display_and_positions": (
            snapshot.is_need_to_send_offers_display_and_positions
        ),
        "blocks": [_block_to_json(block=block) for block in snapshot.blocks],
        "widget_info": (
            _widget_info_to_json(widget_info=snapshot.widget_info)
            if snapshot.widget_info is not None
            else None
        ),
        "custom_head_code": _str_setting(settings=settings, key="custom_head_code"),
        "custom_body_code": _str_setting(settings=settings, key="custom_body_code"),
    }

    return data


def _build_public_config(
    *,
    draft: AdminShowcaseDraft,
    blocks: list[AdminShowcaseDraftBlock],
    offers: list[AdminShowcaseDraftOffer],
    snapshot_id: str,
    affiliate_id: str,
) -> PublishedPublicConfigSnapshot:
    public_offers_by_block_id = _public_offers_by_block_id(offers=offers)
    public_blocks = tuple(
        PublicBlock(
            type=block.type,
            title=block.title,
            offers=tuple(public_offers_by_block_id.get(block.id, ())),
        )
        for block in blocks
        if block.visible
    )
    config_type = _str_setting(settings=draft.settings, key="type") or "showcase"

    return PublishedPublicConfigSnapshot(
        id=snapshot_id,
        affiliate_id=affiliate_id,
        type=config_type,
        settings=_public_settings(settings=draft.settings),
        platform=PublicPlatform(
            id=_str_setting(settings=draft.settings, key="platform_id") or "widgetmarket"
        ),
        constant_url_params_tool=_url_params_tool(
            settings=draft.settings,
            key="constant_url_params_tool",
        ),
        transferred_url_params_tool=_url_params_tool(
            settings=draft.settings,
            key="transferred_url_params_tool",
        ),
        metrics_tool=_metrics_tool(settings=draft.settings),
        is_need_to_send_offers_display_and_positions=_bool_setting(
            settings=draft.settings,
            key="is_need_to_send_offers_display_and_positions",
        ),
        blocks=public_blocks,
        widget_info=_widget_info(
            config_type=config_type,
            settings=draft.settings,
            offers=offers,
        ),
    )


def render_preview_html(
    *,
    config: PublishedPublicConfigSnapshot,
    mode: AdminShowcasePreviewMode,
    settings: JsonObject,
) -> str:
    custom_head_code = _str_setting(settings=settings, key="custom_head_code") or ""
    custom_body_code = _str_setting(settings=settings, key="custom_body_code") or ""
    title = config.settings.text_title or config.id

    return (
        "<!doctype html>"
        f'<html data-preview="true" data-preview-mode="{mode}">'
        "<head>"
        '<meta name="robots" content="noindex,nofollow">'
        f"<title>{escape(title)}</title>"
        f"{custom_head_code}"
        "</head>"
        '<body data-preview="true">'
        f'<main data-preview-config-id="{escape(config.id)}"></main>'
        f"{custom_body_code}"
        "</body>"
        "</html>"
    )


def _public_settings(*, settings: JsonObject) -> PublicConfigSettings:
    return PublicConfigSettings(
        tracking_domain=_str_setting(settings=settings, key="tracking_domain"),
        design_id=_str_setting(settings=settings, key="design_id"),
        color_scheme=_str_setting(settings=settings, key="color_scheme"),
        site_background_color=_str_setting(settings=settings, key="site_background_color"),
        widget_background_color=_str_setting(settings=settings, key="widget_background_color"),
        offers_background_color=_str_setting(settings=settings, key="offers_background_color"),
        text_color=_str_setting(settings=settings, key="text_color"),
        usp_text_color=_str_setting(settings=settings, key="usp_text_color"),
        cta_color=_str_setting(settings=settings, key="cta_color"),
        font_family=_str_setting(settings=settings, key="font_family"),
        text_title=_str_setting(settings=settings, key="text_title"),
        text_subtitle=_str_setting(settings=settings, key="text_subtitle"),
        text_button=_str_setting(settings=settings, key="text_button"),
        image_banner_desktop=_str_setting(settings=settings, key="image_banner_desktop"),
        image_banner_mobile=_str_setting(settings=settings, key="image_banner_mobile"),
        image_banner_mini=_str_setting(settings=settings, key="image_banner_mini"),
        offers_placement=_str_setting(settings=settings, key="offers_placement"),
        offers_mobile_placement=_str_setting(settings=settings, key="offers_mobile_placement"),
        usp_placement=_str_setting(settings=settings, key="usp_placement"),
        alignment=_str_setting(settings=settings, key="alignment"),
        offset_horizontal=_int_setting(settings=settings, key="offset_horizontal"),
        offset_vertical=_int_setting(settings=settings, key="offset_vertical"),
        sort_type=_str_setting(settings=settings, key="sort_type"),
        sort_period=_str_setting(settings=settings, key="sort_period"),
    )


def _public_offers_by_block_id(
    *,
    offers: list[AdminShowcaseDraftOffer],
) -> dict[str, list[PublicOffer]]:
    public_offers_by_block_id: dict[str, list[PublicOffer]] = {}

    for offer in offers:
        if not offer.enabled or offer.block_id is None:
            continue

        public_offers_by_block_id.setdefault(offer.block_id, []).append(
            _public_offer(offer=offer)
        )

    return public_offers_by_block_id


def _widget_info(
    *,
    config_type: str,
    settings: JsonObject,
    offers: list[AdminShowcaseDraftOffer],
) -> PublicWidgetInfo | None:
    if config_type not in WIDGET_CONFIG_TYPES:
        return None

    enabled_offers = tuple(_public_offer(offer=offer) for offer in offers if offer.enabled)
    return PublicWidgetInfo(
        type=config_type,
        display_limit=_int_setting(settings=settings, key="display_limit") or len(enabled_offers),
        leads_id_enabled=_bool_setting(settings=settings, key="leads_id_enabled"),
        offers=enabled_offers,
        trigger_groups=_trigger_groups(settings=settings),
    )


def _public_offer(*, offer: AdminShowcaseDraftOffer) -> PublicOffer:
    return PublicOffer(
        id=offer.id,
        offer_categories=tuple(
            category for category in offer.categories if isinstance(category, str)
        ),
        logo_url=offer.logo_url or "",
        rounded_logo_url=offer.rounded_logo_url or "",
        name=offer.display_name or "",
        site_name=offer.site_name or "",
        url=offer.cpa_url or "",
        fields=tuple(
            PublicOfferField(
                key=field["key"],
                value=field["value"],
                visible=field["visible"],
            )
            for field in offer.fields
            if field["visible"]
        ),
    )


def _trigger_groups(*, settings: JsonObject) -> tuple[PublicTriggerGroup, ...]:
    raw_trigger_groups = settings.get("trigger_groups")
    if not isinstance(raw_trigger_groups, list):
        return ()

    trigger_groups: list[PublicTriggerGroup] = []
    for raw_trigger_group in raw_trigger_groups:
        if not isinstance(raw_trigger_group, dict):
            continue

        trigger_type = _str_value(raw_trigger_group.get("type"))
        if trigger_type is None:
            continue

        trigger_groups.append(
            PublicTriggerGroup(
                type=trigger_type,
                delay_secs=_int_value(raw_trigger_group.get("delay_secs")),
            )
        )

    return tuple(trigger_groups)


def _url_params_tool(*, settings: JsonObject, key: str) -> PublicUrlParamsTool:
    raw_tool = settings.get(key)
    if not isinstance(raw_tool, dict):
        return PublicUrlParamsTool(enabled=False, params=())

    return PublicUrlParamsTool(
        enabled=_bool_value(raw_tool.get("enabled")),
        params=_url_params(value=raw_tool.get("params") or raw_tool.get("url_params")),
    )


def _url_params(*, value: JsonValue) -> tuple[PublicUrlParam, ...]:
    if not isinstance(value, list):
        return ()

    params: list[PublicUrlParam] = []
    for raw_param in value:
        if not isinstance(raw_param, dict):
            continue

        param_key = _str_value(raw_param.get("key"))
        param_value = _str_value(raw_param.get("value"))
        if param_key is None or param_value is None:
            continue

        params.append(PublicUrlParam(key=param_key, value=param_value))

    return tuple(params)


def _metrics_tool(*, settings: JsonObject) -> PublicMetricsTool:
    raw_tool = settings.get("metrics_tool")
    if not isinstance(raw_tool, dict):
        return PublicMetricsTool(enabled=False, metrics=())

    raw_metrics = raw_tool.get("metrics")
    metrics = (
        tuple(metric for metric in raw_metrics if isinstance(metric, str))
        if isinstance(raw_metrics, list)
        else ()
    )

    return PublicMetricsTool(
        enabled=_bool_value(raw_tool.get("enabled")),
        metrics=metrics,
    )


def _settings_to_json(*, settings: PublicConfigSettings) -> JsonObject:
    return {
        "tracking_domain": settings.tracking_domain,
        "design_id": settings.design_id,
        "color_scheme": settings.color_scheme,
        "site_background_color": settings.site_background_color,
        "widget_background_color": settings.widget_background_color,
        "offers_background_color": settings.offers_background_color,
        "text_color": settings.text_color,
        "usp_text_color": settings.usp_text_color,
        "cta_color": settings.cta_color,
        "font_family": settings.font_family,
        "text_title": settings.text_title,
        "text_subtitle": settings.text_subtitle,
        "text_button": settings.text_button,
        "image_banner_desktop": settings.image_banner_desktop,
        "image_banner_mobile": settings.image_banner_mobile,
        "image_banner_mini": settings.image_banner_mini,
        "offers_placement": settings.offers_placement,
        "offers_mobile_placement": settings.offers_mobile_placement,
        "usp_placement": settings.usp_placement,
        "alignment": settings.alignment,
        "offset_horizontal": settings.offset_horizontal,
        "offset_vertical": settings.offset_vertical,
        "sort_type": settings.sort_type,
        "sort_period": settings.sort_period,
    }


def _block_to_json(*, block: PublicBlock) -> JsonObject:
    return {
        "type": block.type,
        "title": block.title,
        "offers": [_offer_to_json(offer=offer) for offer in block.offers],
    }


def _widget_info_to_json(*, widget_info: PublicWidgetInfo) -> JsonObject:
    return {
        "type": widget_info.type,
        "display_limit": widget_info.display_limit,
        "leads_id_enabled": widget_info.leads_id_enabled,
        "offers": [_offer_to_json(offer=offer) for offer in widget_info.offers],
        "trigger_groups": [
            {
                "type": trigger_group.type,
                "delay_secs": trigger_group.delay_secs,
            }
            for trigger_group in widget_info.trigger_groups
        ],
    }


def _offer_to_json(*, offer: PublicOffer) -> JsonObject:
    return {
        "id": offer.id,
        "offer_categories": list(offer.offer_categories),
        "logo_url": offer.logo_url,
        "rounded_logo_url": offer.rounded_logo_url,
        "name": offer.name,
        "site_name": offer.site_name,
        "url": offer.url,
        "fields": [
            {
                "key": field.key,
                "value": field.value,
                "visible": field.visible,
            }
            for field in offer.fields
        ],
    }


def _url_params_tool_to_json(*, tool: PublicUrlParamsTool) -> JsonObject:
    return {
        "enabled": tool.enabled,
        "params": [
            {
                "key": param.key,
                "value": param.value,
            }
            for param in tool.params
        ],
    }


def _str_setting(*, settings: JsonObject, key: str) -> str | None:
    return _str_value(settings.get(key))


def _int_setting(*, settings: JsonObject, key: str) -> int | None:
    return _int_value(settings.get(key))


def _bool_setting(*, settings: JsonObject, key: str) -> bool:
    return _bool_value(settings.get(key))


def _str_value(value: JsonValue) -> str | None:
    return value if isinstance(value, str) else None


def _int_value(value: JsonValue) -> int | None:
    return value if isinstance(value, int) and not isinstance(value, bool) else None


def _bool_value(value: JsonValue) -> bool:
    return value if isinstance(value, bool) else False

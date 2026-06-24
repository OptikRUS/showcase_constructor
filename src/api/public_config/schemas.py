from typing import Self

from pydantic import ConfigDict, Field, field_validator

from src.api.boundary import BoundaryModel
from src.core.public_config.schemas import (
    PublishedPublicConfigSnapshot,
)


class PublicConfigBoundaryModel(BoundaryModel):
    model_config = ConfigDict(extra="forbid")


class PublicConfigSettingsResponse(PublicConfigBoundaryModel):
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


class PublicPlatformResponse(PublicConfigBoundaryModel):
    id: str


class PublicOfferFieldResponse(PublicConfigBoundaryModel):
    key: str
    value: str
    visible: bool


class PublicOfferResponse(PublicConfigBoundaryModel):
    id: str
    offer_categories: tuple[str, ...]
    logo_url: str
    rounded_logo_url: str
    name: str
    site_name: str
    url: str
    fields: tuple[PublicOfferFieldResponse, ...]

    @field_validator("fields")
    @classmethod
    def exclude_hidden_fields(
        cls,
        fields: tuple[PublicOfferFieldResponse, ...],
    ) -> tuple[PublicOfferFieldResponse, ...]:
        return tuple(field for field in fields if field.visible)


class PublicBlockResponse(PublicConfigBoundaryModel):
    type: str
    title: str | None = None
    offers: tuple[PublicOfferResponse, ...] = ()


class PublicTriggerGroupResponse(PublicConfigBoundaryModel):
    type: str
    delay_secs: int | None = None


class PublicWidgetInfoResponse(PublicConfigBoundaryModel):
    type: str
    display_limit: int
    leads_id_enabled: bool
    offers: tuple[PublicOfferResponse, ...]
    trigger_groups: tuple[PublicTriggerGroupResponse, ...]


class PublicUrlParamResponse(PublicConfigBoundaryModel):
    key: str
    value: str


class PublicUrlParamsToolResponse(PublicConfigBoundaryModel):
    enabled: bool
    params: tuple[PublicUrlParamResponse, ...]


class PublicMetricsToolResponse(PublicConfigBoundaryModel):
    enabled: bool
    metrics: tuple[str, ...]


class PublicConfigResponse(PublicConfigBoundaryModel):
    id: str
    affiliate_id: str
    type: str
    settings: PublicConfigSettingsResponse
    platform: PublicPlatformResponse
    constant_url_params_tool: PublicUrlParamsToolResponse
    transferred_url_params_tool: PublicUrlParamsToolResponse
    metrics_tool: PublicMetricsToolResponse
    is_need_to_send_offers_display_and_positions: bool = Field(
        alias="is_need_to_send_offers_display_and_positions",
    )
    blocks: tuple[PublicBlockResponse, ...] = ()
    widget_info: PublicWidgetInfoResponse | None = None

    @classmethod
    def from_domain(cls, snapshot: PublishedPublicConfigSnapshot) -> Self:
        return cls.model_validate(snapshot)

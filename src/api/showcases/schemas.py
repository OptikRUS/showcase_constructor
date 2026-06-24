from typing import Literal, Self, cast

from pydantic import ConfigDict, Field
from pydantic.alias_generators import to_camel

from src.api.boundary import BoundaryModel
from src.core.showcases.schemas import (
    AdminShowcaseDraft,
    AdminShowcaseDraftBlock,
    AdminShowcaseDraftBlockCreateParams,
    AdminShowcaseDraftBlockPatchParams,
    AdminShowcaseDraftSettingsPatchParams,
    JsonObject,
)

AdminShowcaseDraftBlockType = Literal[
    "hero",
    "offers",
    "banner",
    "banner_card",
    "advantages",
    "legal_footer",
    "popup_offers",
    "custom_html",
    "calculator",
]


class AdminShowcaseDraftPatchRequest(BoundaryModel):
    model_config = ConfigDict(extra="forbid")

    design_id: str | None = None
    color_scheme: str | None = None
    site_background_color: str | None = None
    card_background_color: str | None = None
    widget_background_color: str | None = None
    offers_background_color: str | None = None
    text_color: str | None = None
    usp_text_color: str | None = None
    cta_color: str | None = None
    cta_hover_color: str | None = None
    cta_click_color: str | None = None
    font_family: str | None = None
    offers_placement: str | None = None
    offers_mobile_placement: str | None = None
    usp_placement: str | None = None
    alignment: str | None = None
    offset_horizontal: int | None = None
    offset_vertical: int | None = None
    tracking_domain: str | None = None
    logo_url: str | None = None
    favicon_url: str | None = None
    image_banner_desktop: str | None = None
    image_banner_mobile: str | None = None
    image_banner_mini: str | None = None
    text_title: str | None = None
    text_subtitle: str | None = None
    text_button: str | None = None
    meta_title: str | None = None
    meta_description: str | None = None
    fallback_text: str | None = None

    def to_domain(self) -> AdminShowcaseDraftSettingsPatchParams:
        settings = self.model_dump(
            mode="json",
            include=self.model_fields_set,
            by_alias=False,
        )

        return AdminShowcaseDraftSettingsPatchParams(settings=cast("JsonObject", settings))


class AdminShowcaseDraftResponse(BoundaryModel):
    id: str
    title: str
    settings: JsonObject

    @classmethod
    def from_domain(cls, showcase: AdminShowcaseDraft) -> Self:
        return cls(
            id=showcase.id,
            title=showcase.title,
            settings=_camelize_keys(showcase.settings),
        )


def _camelize_keys(data: JsonObject) -> JsonObject:
    return {to_camel(key): value for key, value in data.items()}


class AdminShowcaseDraftBlockCreateRequest(BoundaryModel):
    model_config = ConfigDict(extra="forbid")

    type: AdminShowcaseDraftBlockType
    order: int
    visible: bool = True
    title: str | None = None
    subtitle: str | None = None
    desktop_settings: JsonObject = Field(default_factory=dict)
    mobile_settings: JsonObject = Field(default_factory=dict)
    data: JsonObject = Field(default_factory=dict)

    def to_domain(self) -> AdminShowcaseDraftBlockCreateParams:
        return AdminShowcaseDraftBlockCreateParams(
            type=self.type,
            order=self.order,
            visible=self.visible,
            title=self.title,
            subtitle=self.subtitle,
            desktop_settings=self.desktop_settings,
            mobile_settings=self.mobile_settings,
            data=self.data,
        )


class AdminShowcaseDraftBlockPatchRequest(BoundaryModel):
    model_config = ConfigDict(extra="forbid")

    order: int = 0
    visible: bool = True
    title: str | None = None
    subtitle: str | None = None
    desktop_settings: JsonObject = Field(default_factory=dict)
    mobile_settings: JsonObject = Field(default_factory=dict)
    data: JsonObject = Field(default_factory=dict)

    def to_domain(self) -> AdminShowcaseDraftBlockPatchParams:
        values = self.model_dump(
            mode="json",
            include=self.model_fields_set,
            by_alias=False,
        )

        return AdminShowcaseDraftBlockPatchParams(values=cast("JsonObject", values))


class AdminShowcaseDraftBlockResponse(BoundaryModel):
    id: str
    type: str
    order: int
    visible: bool
    title: str | None
    subtitle: str | None
    desktop_settings: JsonObject
    mobile_settings: JsonObject
    data: JsonObject

    @classmethod
    def from_domain(cls, block: AdminShowcaseDraftBlock) -> Self:
        return cls(
            id=block.id,
            type=block.type,
            order=block.order,
            visible=block.visible,
            title=block.title,
            subtitle=block.subtitle,
            desktop_settings=block.desktop_settings,
            mobile_settings=block.mobile_settings,
            data=block.data,
        )

from typing import Self, cast

from pydantic import ConfigDict
from pydantic.alias_generators import to_camel

from src.api.boundary import BoundaryModel
from src.core.showcases.schemas import (
    AdminShowcaseDraft,
    AdminShowcaseDraftSettingsPatchParams,
    JsonObject,
)


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

from typing import Literal, Self, cast

from pydantic import ConfigDict, Field
from pydantic.alias_generators import to_camel

from src.api.boundary import BoundaryModel
from src.api.public_config.schemas import PublicConfigResponse
from src.core.showcases.schemas import (
    AdminShowcaseDraft,
    AdminShowcaseDraftBlock,
    AdminShowcaseDraftBlockCreateParams,
    AdminShowcaseDraftBlockPatchParams,
    AdminShowcaseDraftOffer,
    AdminShowcaseDraftOfferCreateParams,
    AdminShowcaseDraftOfferField,
    AdminShowcaseDraftOfferPatchParams,
    AdminShowcaseDraftSettingsPatchParams,
    AdminShowcasePreview,
    AdminShowcasePreviewMode,
    JsonObject,
    JsonValue,
)

BLOCK_TITLE_MAX_LENGTH = 255
OFFER_DISPLAY_NAME_MAX_LENGTH = 255
OFFER_SITE_NAME_MAX_LENGTH = 255
OFFER_LEGAL_ENTITY_MAX_LENGTH = 255
OFFER_INN_MAX_LENGTH = 32
OFFER_ERID_MAX_LENGTH = 128

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
    custom_head_code: str | None = None
    custom_body_code: str | None = None

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
    custom_code_warning: str | None = None

    @classmethod
    def from_domain(cls, showcase: AdminShowcaseDraft) -> Self:
        return cls(
            id=showcase.id,
            title=showcase.title,
            settings=_camelize_keys(showcase.settings),
            custom_code_warning=showcase.custom_code_warning,
        )


class AdminShowcasePreviewRequest(BoundaryModel):
    model_config = ConfigDict(extra="forbid")

    mode: AdminShowcasePreviewMode = "desktop"


class AdminShowcasePreviewResponse(BoundaryModel):
    preview: bool
    mode: AdminShowcasePreviewMode
    config: PublicConfigResponse
    html: str | None = None

    @classmethod
    def from_domain(cls, result: AdminShowcasePreview) -> Self:
        return cls(
            preview=result.preview,
            mode=result.mode,
            config=PublicConfigResponse.from_domain(snapshot=result.config),
            html=result.html,
        )


def _camelize_keys(data: JsonObject) -> JsonObject:
    return {to_camel(key): value for key, value in data.items()}


class AdminShowcaseDraftBlockCreateRequest(BoundaryModel):
    model_config = ConfigDict(extra="forbid")

    type: AdminShowcaseDraftBlockType
    order: int
    visible: bool = True
    title: str | None = Field(default=None, max_length=BLOCK_TITLE_MAX_LENGTH)
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
    title: str | None = Field(default=None, max_length=BLOCK_TITLE_MAX_LENGTH)
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


class AdminShowcaseDraftOfferFieldRequest(BoundaryModel):
    model_config = ConfigDict(extra="forbid")

    key: str
    value: str
    visible: bool

    def to_domain(self) -> AdminShowcaseDraftOfferField:
        return {
            "key": self.key,
            "value": self.value,
            "visible": self.visible,
        }


class AdminShowcaseDraftOfferFieldResponse(BoundaryModel):
    key: str
    value: str
    visible: bool

    @classmethod
    def from_domain(cls, field: AdminShowcaseDraftOfferField) -> Self:
        return cls(
            key=field["key"],
            value=field["value"],
            visible=field["visible"],
        )


class AdminShowcaseDraftOfferCreateRequest(BoundaryModel):
    model_config = ConfigDict(extra="forbid")

    block_id: str | None = None
    enabled: bool = True
    manual_order: int
    cta_text: str | None = None
    usp_text: str | None = None
    fields: list[AdminShowcaseDraftOfferFieldRequest] = Field(default_factory=list)
    categories: list[JsonValue] = Field(default_factory=list)
    logo_url: str | None = None
    rounded_logo_url: str | None = None
    display_name: str | None = Field(default=None, max_length=OFFER_DISPLAY_NAME_MAX_LENGTH)
    site_name: str | None = Field(default=None, max_length=OFFER_SITE_NAME_MAX_LENGTH)
    cpa_url: str | None = None
    legal_entity: str | None = Field(default=None, max_length=OFFER_LEGAL_ENTITY_MAX_LENGTH)
    inn: str | None = Field(default=None, max_length=OFFER_INN_MAX_LENGTH)
    erid: str | None = Field(default=None, max_length=OFFER_ERID_MAX_LENGTH)
    data: JsonObject = Field(default_factory=dict)

    def to_domain(self) -> AdminShowcaseDraftOfferCreateParams:
        return AdminShowcaseDraftOfferCreateParams(
            block_id=self.block_id,
            enabled=self.enabled,
            manual_order=self.manual_order,
            cta_text=self.cta_text,
            usp_text=self.usp_text,
            fields=[field.to_domain() for field in self.fields],
            categories=self.categories,
            logo_url=self.logo_url,
            rounded_logo_url=self.rounded_logo_url,
            display_name=self.display_name,
            site_name=self.site_name,
            cpa_url=self.cpa_url,
            legal_entity=self.legal_entity,
            inn=self.inn,
            erid=self.erid,
            data=self.data,
        )


class AdminShowcaseDraftOfferPatchRequest(BoundaryModel):
    model_config = ConfigDict(extra="forbid")

    block_id: str | None = None
    enabled: bool = True
    manual_order: int = 0
    cta_text: str | None = None
    usp_text: str | None = None
    fields: list[AdminShowcaseDraftOfferFieldRequest] = Field(default_factory=list)
    categories: list[JsonValue] = Field(default_factory=list)
    logo_url: str | None = None
    rounded_logo_url: str | None = None
    display_name: str | None = Field(default=None, max_length=OFFER_DISPLAY_NAME_MAX_LENGTH)
    site_name: str | None = Field(default=None, max_length=OFFER_SITE_NAME_MAX_LENGTH)
    cpa_url: str | None = None
    legal_entity: str | None = Field(default=None, max_length=OFFER_LEGAL_ENTITY_MAX_LENGTH)
    inn: str | None = Field(default=None, max_length=OFFER_INN_MAX_LENGTH)
    erid: str | None = Field(default=None, max_length=OFFER_ERID_MAX_LENGTH)
    data: JsonObject = Field(default_factory=dict)

    def to_domain(self) -> AdminShowcaseDraftOfferPatchParams:
        values = self.model_dump(
            mode="json",
            include=self.model_fields_set,
            by_alias=False,
        )
        if "fields" in values:
            values["fields"] = [field.to_domain() for field in self.fields]

        return AdminShowcaseDraftOfferPatchParams(values=cast("JsonObject", values))


class AdminShowcaseDraftOfferResponse(BoundaryModel):
    id: str
    block_id: str | None
    enabled: bool
    manual_order: int
    cta_text: str | None
    usp_text: str | None
    fields: list[AdminShowcaseDraftOfferFieldResponse]
    categories: list[JsonValue]
    logo_url: str | None
    rounded_logo_url: str | None
    display_name: str | None
    site_name: str | None
    cpa_url: str | None
    legal_entity: str | None
    inn: str | None
    erid: str | None
    data: JsonObject

    @classmethod
    def from_domain(cls, offer: AdminShowcaseDraftOffer) -> Self:
        return cls(
            id=offer.id,
            block_id=offer.block_id,
            enabled=offer.enabled,
            manual_order=offer.manual_order,
            cta_text=offer.cta_text,
            usp_text=offer.usp_text,
            fields=[
                AdminShowcaseDraftOfferFieldResponse.from_domain(field=field)
                for field in offer.fields
            ],
            categories=offer.categories,
            logo_url=offer.logo_url,
            rounded_logo_url=offer.rounded_logo_url,
            display_name=offer.display_name,
            site_name=offer.site_name,
            cpa_url=offer.cpa_url,
            legal_entity=offer.legal_entity,
            inn=offer.inn,
            erid=offer.erid,
            data=offer.data,
        )

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal, TypedDict

if TYPE_CHECKING:
    from datetime import datetime

    from src.core.public_config.schemas import PublishedPublicConfigSnapshot

type JsonPrimitive = str | int | float | bool | None
type JsonValue = JsonPrimitive | list[JsonValue] | dict[str, JsonValue]
type JsonObject = dict[str, JsonValue]
type AdminShowcasePreviewMode = Literal["desktop", "mobile"]


@dataclass(frozen=True, slots=True, kw_only=True)
class AdminShowcase:
    id: str
    owner_partner_id: str
    title: str
    public_id: str | None = None
    publication_version: int = 0
    published_snapshot: JsonObject | None = None


@dataclass(frozen=True, slots=True, kw_only=True)
class AdminShowcaseUpdateParams:
    title: str


@dataclass(frozen=True, slots=True, kw_only=True)
class AdminShowcaseDraft:
    id: str
    owner_partner_id: str
    title: str
    settings: JsonObject
    published_snapshot: JsonObject | None
    custom_code_warning: str | None = None


@dataclass(frozen=True, slots=True, kw_only=True)
class AdminShowcaseDraftSettingsPatchParams:
    settings: JsonObject


@dataclass(frozen=True, slots=True, kw_only=True)
class AdminShowcasePreview:
    preview: bool
    mode: AdminShowcasePreviewMode
    config: PublishedPublicConfigSnapshot
    html: str | None


@dataclass(frozen=True, slots=True, kw_only=True)
class AdminShowcasePublication:
    id: str
    public_id: str
    version: int
    published: bool


@dataclass(frozen=True, slots=True, kw_only=True)
class AdminShowcasePublicationState:
    id: str
    public_id: str | None
    version: int
    active: bool
    snapshot: JsonObject | None


@dataclass(frozen=True, slots=True, kw_only=True)
class AdminShowcaseDraftBlock:
    id: str
    showcase_id: str
    type: str
    order: int
    visible: bool
    title: str | None
    subtitle: str | None
    desktop_settings: JsonObject
    mobile_settings: JsonObject
    data: JsonObject


@dataclass(frozen=True, slots=True, kw_only=True)
class AdminShowcaseDraftBlockCreateParams:
    type: str
    order: int
    visible: bool
    title: str | None
    subtitle: str | None
    desktop_settings: JsonObject
    mobile_settings: JsonObject
    data: JsonObject


@dataclass(frozen=True, slots=True, kw_only=True)
class AdminShowcaseDraftBlockPatchParams:
    values: JsonObject


class AdminShowcaseDraftOfferField(TypedDict):
    key: str
    value: str
    visible: bool


@dataclass(frozen=True, slots=True, kw_only=True)
class AdminShowcaseDraftOffer:
    id: str
    showcase_id: str
    block_id: str | None
    enabled: bool
    manual_order: int
    cta_text: str | None
    usp_text: str | None
    fields: list[AdminShowcaseDraftOfferField]
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


@dataclass(frozen=True, slots=True, kw_only=True)
class AdminShowcaseDraftOfferCreateParams:
    block_id: str | None
    enabled: bool
    manual_order: int
    cta_text: str | None
    usp_text: str | None
    fields: list[AdminShowcaseDraftOfferField]
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


@dataclass(frozen=True, slots=True, kw_only=True)
class AdminShowcaseDraftOfferPatchParams:
    values: JsonObject


@dataclass(frozen=True, slots=True, kw_only=True)
class PublishedShowcaseSnapshot:
    showcase_id: str
    public_id: str
    version: int
    snapshot: JsonObject
    created_by_user_id: str
    created_by_partner_id: str
    created_at: datetime


@dataclass(frozen=True, slots=True, kw_only=True)
class PublishedRouteBinding:
    showcase_id: str
    public_id: str
    host: str
    path: str
    active: bool
    created_at: datetime


@dataclass(frozen=True, slots=True, kw_only=True)
class ShowcaseAuditRecord:
    showcase_id: str
    action: str
    actor_user_id: str
    actor_partner_id: str
    metadata: JsonObject
    created_at: datetime

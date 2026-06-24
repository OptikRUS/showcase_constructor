from __future__ import annotations

from dataclasses import dataclass

type JsonPrimitive = str | int | float | bool | None
type JsonValue = JsonPrimitive | list[JsonValue] | dict[str, JsonValue]
type JsonObject = dict[str, JsonValue]


@dataclass(frozen=True, slots=True, kw_only=True)
class AdminShowcase:
    id: str
    owner_partner_id: str
    title: str


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


@dataclass(frozen=True, slots=True, kw_only=True)
class AdminShowcaseDraftSettingsPatchParams:
    settings: JsonObject


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
class AdminShowcaseDraftOffer:
    id: str
    showcase_id: str
    block_id: str | None
    enabled: bool
    manual_order: int
    cta_text: str | None
    usp_text: str | None
    fields: list[JsonValue]
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

from dataclasses import dataclass


@dataclass(frozen=True, slots=True, kw_only=True)
class AdminShowcase:
    id: str
    owner_partner_id: str
    title: str

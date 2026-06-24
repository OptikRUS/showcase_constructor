from dataclasses import dataclass


@dataclass(frozen=True, slots=True, kw_only=True)
class AdminActorContext:
    user_id: str
    partner_id: str

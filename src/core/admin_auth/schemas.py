from dataclasses import dataclass

from src.core.admin_auth.exceptions import AdminAuthenticationRequiredError


@dataclass(frozen=True, slots=True, kw_only=True)
class AdminActorContext:
    user_id: str
    partner_id: str

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "user_id",
            self._normalize_required_id(value=self.user_id),
        )
        object.__setattr__(
            self,
            "partner_id",
            self._normalize_required_id(value=self.partner_id),
        )

    @classmethod
    def from_raw(cls, *, user_id: str | None, partner_id: str | None) -> "AdminActorContext":
        return cls(
            user_id=cls._normalize_required_id(value=user_id),
            partner_id=cls._normalize_required_id(value=partner_id),
        )

    @staticmethod
    def _normalize_required_id(*, value: str | None) -> str:
        if value is None:
            raise AdminAuthenticationRequiredError

        normalized_value = value.strip()
        if not normalized_value:
            raise AdminAuthenticationRequiredError

        return normalized_value

from pydantic import ValidationError, field_validator

from src.api.boundary import SnakeBoundaryModel
from src.core.admin_auth.exceptions import AdminAuthenticationRequiredError


class JwtUser(SnakeBoundaryModel):
    user_id: str
    partner_id: str

    @field_validator("user_id", "partner_id")
    @classmethod
    def validate_required_identifier(cls, value: str) -> str:
        if not value.strip():
            message = "Auth identifier is required"
            raise ValueError(message)

        return value

    @classmethod
    def from_credentials(cls, payload: object) -> "JwtUser":
        try:
            return cls.model_validate(payload)
        except ValidationError as exc:
            raise AdminAuthenticationRequiredError from exc

from src.api.boundary import SnakeBoundaryModel
from src.core.admin_auth.exceptions import AdminAuthenticationRequiredError


class JwtUser(SnakeBoundaryModel):
    user_id: str
    partner_id: str

    @classmethod
    def from_credentials(cls, payload: object) -> "JwtUser":
        try:
            return cls.model_validate(payload)
        except Exception as exc:
            raise AdminAuthenticationRequiredError from exc

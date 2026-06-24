from src.api.boundary import BoundaryModel
from src.core.admin_auth.schemas import AdminActorContext


class AdminContextResponse(BoundaryModel):
    user_id: str
    partner_id: str

    @classmethod
    def from_domain(cls, context: AdminActorContext) -> "AdminContextResponse":
        return cls(user_id=context.user_id, partner_id=context.partner_id)

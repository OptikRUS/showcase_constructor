from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, status

from src.api.admin_auth.schemas import AdminContextResponse
from src.api.auth.deps import JwtUserDeps
from src.core.admin_auth.schemas import AdminActorContext

router = APIRouter(prefix="/api/v1/admin/auth", tags=["admin-auth"], route_class=DishkaRoute)


@router.get(path="/context", status_code=status.HTTP_200_OK)
async def get_current_context(
    user: JwtUserDeps,
) -> AdminContextResponse:
    context = AdminActorContext(user_id=user.user_id, partner_id=user.partner_id)
    return AdminContextResponse.from_domain(context=context)

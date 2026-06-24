from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, status

from src.api.admin_auth.schemas import AdminContextResponse
from src.core.admin_auth.schemas import AdminActorContext

router = APIRouter(prefix="/api/v1/admin/auth", tags=["admin-auth"], route_class=DishkaRoute)


@router.get(path="/context", status_code=status.HTTP_200_OK)
async def get_current_context(
    context: FromDishka[AdminActorContext],
) -> AdminContextResponse:
    return AdminContextResponse.from_domain(context=context)

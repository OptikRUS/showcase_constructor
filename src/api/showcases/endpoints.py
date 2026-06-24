from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, status

from src.api.auth.deps import JwtUserDeps
from src.api.showcases.schemas import AdminShowcaseDraftPatchRequest, AdminShowcaseDraftResponse
from src.core.admin_auth.schemas import AdminActorContext
from src.core.showcases.use_cases import UpdateAdminShowcaseDraftSettingsUseCase

router = APIRouter(prefix="/api/v1/showcases", tags=["showcases"], route_class=DishkaRoute)


@router.patch(path="/{showcase_id}", status_code=status.HTTP_200_OK)
async def patch_showcase_draft_settings(
    showcase_id: str,
    body: AdminShowcaseDraftPatchRequest,
    user: JwtUserDeps,
    use_case: FromDishka[UpdateAdminShowcaseDraftSettingsUseCase],
) -> AdminShowcaseDraftResponse:
    context = AdminActorContext(user_id=user.user_id, partner_id=user.partner_id)
    showcase = await use_case.execute(
        showcase_id=showcase_id,
        params=body.to_domain(),
        context=context,
    )

    return AdminShowcaseDraftResponse.from_domain(showcase=showcase)

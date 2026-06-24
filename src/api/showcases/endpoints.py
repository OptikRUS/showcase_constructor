from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, status

from src.api.auth.deps import JwtUserDeps
from src.api.showcases.schemas import (
    AdminShowcaseDraftBlockCreateRequest,
    AdminShowcaseDraftBlockPatchRequest,
    AdminShowcaseDraftBlockResponse,
    AdminShowcaseDraftPatchRequest,
    AdminShowcaseDraftResponse,
)
from src.core.admin_auth.schemas import AdminActorContext
from src.core.showcases.use_cases import (
    CreateAdminShowcaseBlockUseCase,
    DeleteAdminShowcaseBlockUseCase,
    ListAdminShowcaseBlocksUseCase,
    PatchAdminShowcaseBlockUseCase,
    UpdateAdminShowcaseDraftSettingsUseCase,
)

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


@router.get(path="/{showcase_id}/blocks", status_code=status.HTTP_200_OK)
async def list_showcase_draft_blocks(
    showcase_id: str,
    user: JwtUserDeps,
    use_case: FromDishka[ListAdminShowcaseBlocksUseCase],
) -> list[AdminShowcaseDraftBlockResponse]:
    context = AdminActorContext(user_id=user.user_id, partner_id=user.partner_id)
    blocks = await use_case.execute(showcase_id=showcase_id, context=context)

    return [AdminShowcaseDraftBlockResponse.from_domain(block=block) for block in blocks]


@router.post(path="/{showcase_id}/blocks", status_code=status.HTTP_201_CREATED)
async def create_showcase_draft_block(
    showcase_id: str,
    body: AdminShowcaseDraftBlockCreateRequest,
    user: JwtUserDeps,
    use_case: FromDishka[CreateAdminShowcaseBlockUseCase],
) -> AdminShowcaseDraftBlockResponse:
    context = AdminActorContext(user_id=user.user_id, partner_id=user.partner_id)
    block = await use_case.execute(
        showcase_id=showcase_id,
        params=body.to_domain(),
        context=context,
    )

    return AdminShowcaseDraftBlockResponse.from_domain(block=block)


@router.patch(path="/{showcase_id}/blocks/{block_id}", status_code=status.HTTP_200_OK)
async def patch_showcase_draft_block(
    showcase_id: str,
    block_id: str,
    body: AdminShowcaseDraftBlockPatchRequest,
    user: JwtUserDeps,
    use_case: FromDishka[PatchAdminShowcaseBlockUseCase],
) -> AdminShowcaseDraftBlockResponse:
    context = AdminActorContext(user_id=user.user_id, partner_id=user.partner_id)
    block = await use_case.execute(
        showcase_id=showcase_id,
        block_id=block_id,
        params=body.to_domain(),
        context=context,
    )

    return AdminShowcaseDraftBlockResponse.from_domain(block=block)


@router.delete(path="/{showcase_id}/blocks/{block_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_showcase_draft_block(
    showcase_id: str,
    block_id: str,
    user: JwtUserDeps,
    use_case: FromDishka[DeleteAdminShowcaseBlockUseCase],
) -> None:
    context = AdminActorContext(user_id=user.user_id, partner_id=user.partner_id)
    await use_case.execute(showcase_id=showcase_id, block_id=block_id, context=context)

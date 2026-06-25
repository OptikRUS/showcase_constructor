from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, status

from src.api.auth.deps import JwtUserDeps
from src.api.showcases.schemas import (
    AdminShowcaseDraftBlockCreateRequest,
    AdminShowcaseDraftBlockPatchRequest,
    AdminShowcaseDraftBlockResponse,
    AdminShowcaseDraftOfferCreateRequest,
    AdminShowcaseDraftOfferPatchRequest,
    AdminShowcaseDraftOfferResponse,
    AdminShowcaseDraftPatchRequest,
    AdminShowcaseDraftResponse,
    AdminShowcasePreviewRequest,
    AdminShowcasePreviewResponse,
    AdminShowcasePublicationResponse,
)
from src.core.admin_auth.schemas import AdminActorContext
from src.core.showcases.use_cases import (
    BuildAdminShowcasePreviewUseCase,
    CreateAdminShowcaseBlockUseCase,
    CreateAdminShowcaseOfferUseCase,
    DeleteAdminShowcaseBlockUseCase,
    DeleteAdminShowcaseOfferUseCase,
    ListAdminShowcaseBlocksUseCase,
    ListAdminShowcaseOffersUseCase,
    PatchAdminShowcaseBlockUseCase,
    PatchAdminShowcaseOfferUseCase,
    PublishAdminShowcaseUseCase,
    UnpublishAdminShowcaseUseCase,
    UpdateAdminShowcaseDraftSettingsUseCase,
)

router = APIRouter(prefix="/api/v1/showcases", tags=["showcases"], route_class=DishkaRoute)


@router.patch(
    path="/{showcase_id}",
    status_code=status.HTTP_200_OK,
    response_model_exclude_none=True,
)
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


@router.post(path="/{showcase_id}/preview", status_code=status.HTTP_200_OK)
async def preview_showcase(
    showcase_id: str,
    body: AdminShowcasePreviewRequest,
    user: JwtUserDeps,
    use_case: FromDishka[BuildAdminShowcasePreviewUseCase],
) -> AdminShowcasePreviewResponse:
    context = AdminActorContext(user_id=user.user_id, partner_id=user.partner_id)
    result = await use_case.execute(
        showcase_id=showcase_id,
        mode=body.mode,
        context=context,
    )

    return AdminShowcasePreviewResponse.from_domain(result=result)


@router.post(path="/{showcase_id}/publish", status_code=status.HTTP_200_OK)
async def publish_showcase(
    showcase_id: str,
    user: JwtUserDeps,
    use_case: FromDishka[PublishAdminShowcaseUseCase],
) -> AdminShowcasePublicationResponse:
    context = AdminActorContext(user_id=user.user_id, partner_id=user.partner_id)
    result = await use_case.execute(showcase_id=showcase_id, context=context)

    return AdminShowcasePublicationResponse.from_domain(result=result)


@router.post(path="/{showcase_id}/unpublish", status_code=status.HTTP_200_OK)
async def unpublish_showcase(
    showcase_id: str,
    user: JwtUserDeps,
    use_case: FromDishka[UnpublishAdminShowcaseUseCase],
) -> AdminShowcasePublicationResponse:
    context = AdminActorContext(user_id=user.user_id, partner_id=user.partner_id)
    result = await use_case.execute(showcase_id=showcase_id, context=context)

    return AdminShowcasePublicationResponse.from_domain(result=result)


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


@router.get(path="/{showcase_id}/offers", status_code=status.HTTP_200_OK)
async def list_showcase_draft_offers(
    showcase_id: str,
    user: JwtUserDeps,
    use_case: FromDishka[ListAdminShowcaseOffersUseCase],
) -> list[AdminShowcaseDraftOfferResponse]:
    context = AdminActorContext(user_id=user.user_id, partner_id=user.partner_id)
    offers = await use_case.execute(showcase_id=showcase_id, context=context)

    return [AdminShowcaseDraftOfferResponse.from_domain(offer=offer) for offer in offers]


@router.post(path="/{showcase_id}/offers", status_code=status.HTTP_201_CREATED)
async def create_showcase_draft_offer(
    showcase_id: str,
    body: AdminShowcaseDraftOfferCreateRequest,
    user: JwtUserDeps,
    use_case: FromDishka[CreateAdminShowcaseOfferUseCase],
) -> AdminShowcaseDraftOfferResponse:
    context = AdminActorContext(user_id=user.user_id, partner_id=user.partner_id)
    offer = await use_case.execute(
        showcase_id=showcase_id,
        params=body.to_domain(),
        context=context,
    )

    return AdminShowcaseDraftOfferResponse.from_domain(offer=offer)


@router.patch(path="/{showcase_id}/offers/{offer_id}", status_code=status.HTTP_200_OK)
async def patch_showcase_draft_offer(
    showcase_id: str,
    offer_id: str,
    body: AdminShowcaseDraftOfferPatchRequest,
    user: JwtUserDeps,
    use_case: FromDishka[PatchAdminShowcaseOfferUseCase],
) -> AdminShowcaseDraftOfferResponse:
    context = AdminActorContext(user_id=user.user_id, partner_id=user.partner_id)
    offer = await use_case.execute(
        showcase_id=showcase_id,
        offer_id=offer_id,
        params=body.to_domain(),
        context=context,
    )

    return AdminShowcaseDraftOfferResponse.from_domain(offer=offer)


@router.delete(path="/{showcase_id}/offers/{offer_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_showcase_draft_offer(
    showcase_id: str,
    offer_id: str,
    user: JwtUserDeps,
    use_case: FromDishka[DeleteAdminShowcaseOfferUseCase],
) -> None:
    context = AdminActorContext(user_id=user.user_id, partner_id=user.partner_id)
    await use_case.execute(showcase_id=showcase_id, offer_id=offer_id, context=context)

from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, status

from src.api.public_config.schemas import PublicConfigResponse
from src.core.public_config.use_cases import (
    GetPublishedPublicConfigUseCase,
    ResolvePublishedPublicConfigUseCase,
)

router = APIRouter(
    prefix="/api/v1/public/showcases",
    tags=["public-config"],
    route_class=DishkaRoute,
)


@router.get(
    path="/resolve",
    status_code=status.HTTP_200_OK,
    response_model_exclude_none=True,
)
async def resolve_public_showcase(
    host: str,
    path: str,
    use_case: FromDishka[ResolvePublishedPublicConfigUseCase],
) -> PublicConfigResponse:
    snapshot = await use_case.execute(host=host, path=path)

    return PublicConfigResponse.from_domain(snapshot=snapshot)


@router.get(
    path="/{public_id}",
    status_code=status.HTTP_200_OK,
    response_model_exclude_none=True,
)
async def get_public_showcase(
    public_id: str,
    use_case: FromDishka[GetPublishedPublicConfigUseCase],
) -> PublicConfigResponse:
    snapshot = await use_case.execute(public_id=public_id)

    return PublicConfigResponse.from_domain(snapshot=snapshot)

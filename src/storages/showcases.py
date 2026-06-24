from dataclasses import dataclass

from sqlalchemy import insert, literal, select, update
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.showcases.exceptions import AdminShowcaseNotFoundError
from src.core.showcases.schemas import (
    AdminShowcase,
    AdminShowcaseDraft,
    AdminShowcaseDraftBlock,
    AdminShowcaseDraftBlockCreateParams,
    AdminShowcaseDraftSettingsPatchParams,
    AdminShowcaseUpdateParams,
)
from src.core.storages import AdminShowcaseStorage
from src.storages.models import AdminShowcaseDraftBlockModel, AdminShowcaseModel


@dataclass(frozen=True, slots=True, kw_only=True)
class DatabaseAdminShowcaseStorage(AdminShowcaseStorage):
    session: AsyncSession

    async def get_by_id(self, *, showcase_id: str) -> AdminShowcase:
        model = await self.session.scalar(
            select(AdminShowcaseModel).where(AdminShowcaseModel.id == showcase_id)
        )

        if model is None:
            raise AdminShowcaseNotFoundError

        return model.to_domain()

    async def get_draft_by_id(self, *, showcase_id: str) -> AdminShowcaseDraft:
        model = await self.session.scalar(
            select(AdminShowcaseModel).where(AdminShowcaseModel.id == showcase_id)
        )

        if model is None:
            raise AdminShowcaseNotFoundError

        return model.to_draft_domain()

    async def list_draft_blocks(self, *, showcase_id: str) -> list[AdminShowcaseDraftBlock]:
        result = await self.session.scalars(
            select(AdminShowcaseDraftBlockModel)
            .where(AdminShowcaseDraftBlockModel.showcase_id == showcase_id)
            .order_by(
                AdminShowcaseDraftBlockModel.draft_order,
                AdminShowcaseDraftBlockModel.block_id,
            )
        )

        return [model.to_domain() for model in result.all()]

    async def create_draft_block(
        self,
        *,
        showcase_id: str,
        block_id: str,
        params: AdminShowcaseDraftBlockCreateParams,
    ) -> AdminShowcaseDraftBlock:
        model = await self.session.scalar(
            insert(AdminShowcaseDraftBlockModel)
            .from_select(
                [
                    "showcase_internal_id",
                    "showcase_id",
                    "block_id",
                    "type",
                    "draft_order",
                    "visible",
                    "title",
                    "subtitle",
                    "desktop_settings",
                    "mobile_settings",
                    "data",
                ],
                select(
                    AdminShowcaseModel.internal_id,
                    AdminShowcaseModel.id,
                    literal(block_id),
                    literal(params.type),
                    literal(params.order),
                    literal(params.visible),
                    literal(params.title),
                    literal(params.subtitle),
                    literal(params.desktop_settings, type_=JSONB),
                    literal(params.mobile_settings, type_=JSONB),
                    literal(params.data, type_=JSONB),
                ).where(AdminShowcaseModel.id == showcase_id),
            )
            .returning(AdminShowcaseDraftBlockModel)
        )

        if model is None:
            raise AdminShowcaseNotFoundError

        return model.to_domain()

    async def update_draft(
        self,
        *,
        showcase_id: str,
        params: AdminShowcaseUpdateParams,
    ) -> AdminShowcase:
        model = await self.session.scalar(
            update(AdminShowcaseModel)
            .where(AdminShowcaseModel.id == showcase_id)
            .values(title=params.title)
            .returning(AdminShowcaseModel)
        )

        if model is None:
            raise AdminShowcaseNotFoundError

        return model.to_domain()

    async def update_draft_settings(
        self,
        *,
        showcase_id: str,
        params: AdminShowcaseDraftSettingsPatchParams,
    ) -> AdminShowcaseDraft:
        model = await self.session.scalar(
            update(AdminShowcaseModel)
            .where(AdminShowcaseModel.id == showcase_id)
            .values(
                draft_settings=AdminShowcaseModel.draft_settings.op("||")(
                    literal(params.settings, type_=JSONB)
                )
            )
            .returning(AdminShowcaseModel)
        )

        if model is None:
            raise AdminShowcaseNotFoundError

        return model.to_draft_domain()

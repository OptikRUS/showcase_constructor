from dataclasses import dataclass

from sqlalchemy import delete, insert, literal, select, update
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.showcases.exceptions import (
    AdminShowcaseDraftBlockNotFoundError,
    AdminShowcaseNotFoundError,
)
from src.core.showcases.schemas import (
    AdminShowcase,
    AdminShowcaseDraft,
    AdminShowcaseDraftBlock,
    AdminShowcaseDraftBlockCreateParams,
    AdminShowcaseDraftBlockPatchParams,
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

    async def patch_draft_block(
        self,
        *,
        showcase_id: str,
        block_id: str,
        params: AdminShowcaseDraftBlockPatchParams,
    ) -> AdminShowcaseDraftBlock:
        if not params.values:
            return await self._get_draft_block_by_id(showcase_id=showcase_id, block_id=block_id)

        model = await self.session.scalar(
            update(AdminShowcaseDraftBlockModel)
            .where(
                AdminShowcaseDraftBlockModel.showcase_id == showcase_id,
                AdminShowcaseDraftBlockModel.block_id == block_id,
            )
            .values(_draft_block_update_values(params=params))
            .returning(AdminShowcaseDraftBlockModel)
        )

        if model is None:
            raise AdminShowcaseDraftBlockNotFoundError

        return model.to_domain()

    async def delete_draft_block(self, *, showcase_id: str, block_id: str) -> None:
        deleted_block_id = await self.session.scalar(
            delete(AdminShowcaseDraftBlockModel)
            .where(
                AdminShowcaseDraftBlockModel.showcase_id == showcase_id,
                AdminShowcaseDraftBlockModel.block_id == block_id,
            )
            .returning(AdminShowcaseDraftBlockModel.block_id)
        )

        if deleted_block_id is None:
            raise AdminShowcaseDraftBlockNotFoundError

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

    async def _get_draft_block_by_id(
        self,
        *,
        showcase_id: str,
        block_id: str,
    ) -> AdminShowcaseDraftBlock:
        model = await self.session.scalar(
            select(AdminShowcaseDraftBlockModel).where(
                AdminShowcaseDraftBlockModel.showcase_id == showcase_id,
                AdminShowcaseDraftBlockModel.block_id == block_id,
            )
        )

        if model is None:
            raise AdminShowcaseDraftBlockNotFoundError

        return model.to_domain()


def _draft_block_update_values(
    *,
    params: AdminShowcaseDraftBlockPatchParams,
) -> dict[str, object]:
    values: dict[str, object] = {}
    if "order" in params.values:
        values["draft_order"] = params.values["order"]
    if "visible" in params.values:
        values["visible"] = params.values["visible"]
    if "title" in params.values:
        values["title"] = params.values["title"]
    if "subtitle" in params.values:
        values["subtitle"] = params.values["subtitle"]
    if "desktop_settings" in params.values:
        values["desktop_settings"] = params.values["desktop_settings"]
    if "mobile_settings" in params.values:
        values["mobile_settings"] = params.values["mobile_settings"]
    if "data" in params.values:
        values["data"] = params.values["data"]

    return values

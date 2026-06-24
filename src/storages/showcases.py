from dataclasses import dataclass

from sqlalchemy import literal, select, update
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.showcases.exceptions import AdminShowcaseNotFoundError
from src.core.showcases.schemas import (
    AdminShowcase,
    AdminShowcaseDraft,
    AdminShowcaseDraftSettingsPatchParams,
    AdminShowcaseUpdateParams,
)
from src.core.storages import AdminShowcaseStorage
from src.storages.models import AdminShowcaseModel


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

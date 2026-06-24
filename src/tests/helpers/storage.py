from dataclasses import dataclass

from sqlalchemy import insert, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.showcases.schemas import AdminShowcaseDraft, AdminShowcaseDraftBlock, JsonObject
from src.storages.models import AdminShowcaseDraftBlockModel, AdminShowcaseModel


@dataclass(kw_only=True, slots=True)
class StorageHelper:
    session: AsyncSession

    async def create_admin_showcase(
        self,
        *,
        id: str = "showcase-1",
        owner_partner_id: str = "partner-1",
        title: str = "Test showcase",
        draft_settings: JsonObject | None = None,
        published_snapshot: JsonObject | None = None,
    ) -> None:
        await self.session.execute(
            insert(AdminShowcaseModel).values(
                id=id,
                owner_partner_id=owner_partner_id,
                title=title,
                draft_settings=draft_settings or {},
                published_snapshot=published_snapshot,
            )
        )

    async def get_admin_showcase_draft(self, *, showcase_id: str) -> AdminShowcaseDraft:
        model = await self.session.scalar(
            select(AdminShowcaseModel).where(AdminShowcaseModel.id == showcase_id)
        )

        if model is None:
            message = f"Admin showcase {showcase_id!r} was not found"
            raise RuntimeError(message)

        return model.to_draft_domain()

    async def create_admin_showcase_draft_block(
        self,
        *,
        block: AdminShowcaseDraftBlock,
    ) -> None:
        showcase_internal_id = (
            select(AdminShowcaseModel.internal_id)
            .where(AdminShowcaseModel.id == block.showcase_id)
            .scalar_subquery()
        )
        await self.session.execute(
            insert(AdminShowcaseDraftBlockModel).values(
                showcase_internal_id=showcase_internal_id,
                showcase_id=block.showcase_id,
                block_id=block.id,
                type=block.type,
                draft_order=block.order,
                visible=block.visible,
                title=block.title,
                subtitle=block.subtitle,
                desktop_settings=block.desktop_settings,
                mobile_settings=block.mobile_settings,
                data=block.data,
            )
        )

    async def list_admin_showcase_draft_blocks(
        self,
        *,
        showcase_id: str,
    ) -> list[AdminShowcaseDraftBlock]:
        result = await self.session.scalars(
            select(AdminShowcaseDraftBlockModel)
            .where(AdminShowcaseDraftBlockModel.showcase_id == showcase_id)
            .order_by(
                AdminShowcaseDraftBlockModel.draft_order,
                AdminShowcaseDraftBlockModel.block_id,
            )
        )

        return [model.to_domain() for model in result.all()]

    async def commit(self) -> None:
        await self.session.commit()

    async def get_current_alembic_version(self) -> str:
        result = await self.session.execute(text("select version_num from alembic_version"))

        return str(result.scalar_one())

    async def get_public_table_names(self) -> set[str]:
        result = await self.session.execute(
            text(
                "select table_name "
                "from information_schema.tables "
                "where table_schema = 'public'"
            )
        )

        return {str(table_name) for table_name in result.scalars().all()}

    async def get_table_column_names(self, *, table_name: str) -> set[str]:
        result = await self.session.execute(
            text(
                "select column_name "
                "from information_schema.columns "
                "where table_schema = 'public' and table_name = :table_name"
            ),
            {"table_name": table_name},
        )

        return {str(column_name) for column_name in result.scalars().all()}

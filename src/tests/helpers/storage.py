from dataclasses import dataclass

from sqlalchemy import insert, select, text, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.showcases.schemas import (
    AdminShowcaseDraft,
    AdminShowcaseDraftBlock,
    AdminShowcaseDraftOffer,
    AdminShowcasePublicationState,
    JsonObject,
    PublishedRouteBinding,
    PublishedShowcaseSnapshot,
    ShowcaseAuditRecord,
)
from src.storages.models import (
    AdminShowcaseDraftBlockModel,
    AdminShowcaseDraftOfferModel,
    AdminShowcaseModel,
    PublishedRouteBindingModel,
    PublishedShowcaseSnapshotModel,
    ShowcaseAuditRecordModel,
)


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
        public_id: str | None = None,
    ) -> None:
        await self.session.execute(
            insert(AdminShowcaseModel).values(
                id=id,
                owner_partner_id=owner_partner_id,
                title=title,
                draft_settings=draft_settings or {},
                published_snapshot=published_snapshot,
                public_id=public_id,
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

    async def create_admin_showcase_draft_offer(
        self,
        *,
        offer: AdminShowcaseDraftOffer,
    ) -> None:
        showcase_internal_id = (
            select(AdminShowcaseModel.internal_id)
            .where(AdminShowcaseModel.id == offer.showcase_id)
            .scalar_subquery()
        )
        await self.session.execute(
            insert(AdminShowcaseDraftOfferModel).values(
                showcase_internal_id=showcase_internal_id,
                showcase_id=offer.showcase_id,
                offer_id=offer.id,
                block_id=offer.block_id,
                enabled=offer.enabled,
                manual_order=offer.manual_order,
                cta_text=offer.cta_text,
                usp_text=offer.usp_text,
                fields=offer.fields,
                categories=offer.categories,
                logo_url=offer.logo_url,
                rounded_logo_url=offer.rounded_logo_url,
                display_name=offer.display_name,
                site_name=offer.site_name,
                cpa_url=offer.cpa_url,
                legal_entity=offer.legal_entity,
                inn=offer.inn,
                erid=offer.erid,
                data=offer.data,
            )
        )

    async def list_admin_showcase_draft_offers(
        self,
        *,
        showcase_id: str,
    ) -> list[AdminShowcaseDraftOffer]:
        result = await self.session.scalars(
            select(AdminShowcaseDraftOfferModel)
            .where(AdminShowcaseDraftOfferModel.showcase_id == showcase_id)
            .order_by(
                AdminShowcaseDraftOfferModel.block_id,
                AdminShowcaseDraftOfferModel.manual_order,
                AdminShowcaseDraftOfferModel.offer_id,
            )
        )

        return [model.to_domain() for model in result.all()]

    async def list_published_showcase_snapshots(
        self,
        *,
        showcase_id: str,
    ) -> list[PublishedShowcaseSnapshot]:
        result = await self.session.scalars(
            select(PublishedShowcaseSnapshotModel)
            .where(PublishedShowcaseSnapshotModel.showcase_id == showcase_id)
            .order_by(PublishedShowcaseSnapshotModel.version)
        )

        return [model.to_domain() for model in result.all()]

    async def create_active_published_showcase_snapshot(
        self,
        *,
        showcase_id: str,
        public_id: str,
        version: int,
        snapshot: JsonObject,
        created_by_user_id: str = "admin-user-1",
        created_by_partner_id: str = "partner-1",
    ) -> PublishedShowcaseSnapshot:
        showcase_internal_id = (
            select(AdminShowcaseModel.internal_id)
            .where(AdminShowcaseModel.id == showcase_id)
            .scalar_subquery()
        )
        snapshot_model = await self.session.scalar(
            insert(PublishedShowcaseSnapshotModel)
            .values(
                showcase_internal_id=showcase_internal_id,
                showcase_id=showcase_id,
                public_id=public_id,
                version=version,
                snapshot=snapshot,
                created_by_user_id=created_by_user_id,
                created_by_partner_id=created_by_partner_id,
            )
            .returning(PublishedShowcaseSnapshotModel)
        )

        if snapshot_model is None:
            message = f"Published snapshot for {showcase_id!r} was not created"
            raise RuntimeError(message)

        await self.session.execute(
            update(AdminShowcaseModel)
            .where(AdminShowcaseModel.id == showcase_id)
            .values(
                public_id=public_id,
                publication_version=version,
                active_published_snapshot_internal_id=snapshot_model.internal_id,
                published_snapshot=snapshot,
            )
        )

        return snapshot_model.to_domain()

    async def get_admin_showcase_publication_state(
        self,
        *,
        showcase_id: str,
    ) -> AdminShowcasePublicationState:
        model = await self.session.scalar(
            select(AdminShowcaseModel).where(AdminShowcaseModel.id == showcase_id)
        )

        if model is None:
            message = f"Admin showcase {showcase_id!r} was not found"
            raise RuntimeError(message)

        return model.to_publication_state_domain()

    async def deactivate_admin_showcase_publication(
        self,
        *,
        showcase_id: str,
        public_id: str,
        version: int,
    ) -> None:
        await self.session.execute(
            update(AdminShowcaseModel)
            .where(AdminShowcaseModel.id == showcase_id)
            .values(
                publication_version=version,
                active_published_snapshot_internal_id=None,
                published_snapshot=None,
            )
        )
        await self.deactivate_published_route_bindings(
            showcase_id=showcase_id,
            public_id=public_id,
        )

    async def create_published_route_binding(
        self,
        *,
        showcase_id: str,
        public_id: str,
        host: str,
        path: str,
    ) -> PublishedRouteBinding:
        showcase_internal_id = (
            select(AdminShowcaseModel.internal_id)
            .where(AdminShowcaseModel.id == showcase_id)
            .scalar_subquery()
        )
        model = await self.session.scalar(
            insert(PublishedRouteBindingModel)
            .values(
                showcase_internal_id=showcase_internal_id,
                showcase_id=showcase_id,
                public_id=public_id,
                host=host,
                path=path,
            )
            .returning(PublishedRouteBindingModel)
        )

        if model is None:
            message = f"Published route binding for {showcase_id!r} was not created"
            raise RuntimeError(message)

        return model.to_domain()

    async def list_published_route_bindings(
        self,
        *,
        showcase_id: str,
    ) -> list[PublishedRouteBinding]:
        result = await self.session.scalars(
            select(PublishedRouteBindingModel)
            .where(PublishedRouteBindingModel.showcase_id == showcase_id)
            .order_by(PublishedRouteBindingModel.host, PublishedRouteBindingModel.path)
        )

        return [model.to_domain() for model in result.all()]

    async def deactivate_published_route_bindings(
        self,
        *,
        showcase_id: str,
        public_id: str,
    ) -> None:
        await self.session.execute(
            update(PublishedRouteBindingModel)
            .where(
                PublishedRouteBindingModel.showcase_id == showcase_id,
                PublishedRouteBindingModel.public_id == public_id,
                PublishedRouteBindingModel.active.is_(True),
            )
            .values(active=False)
        )

    async def list_showcase_audit_records(
        self,
        *,
        showcase_id: str,
    ) -> list[ShowcaseAuditRecord]:
        result = await self.session.scalars(
            select(ShowcaseAuditRecordModel)
            .where(ShowcaseAuditRecordModel.showcase_id == showcase_id)
            .order_by(ShowcaseAuditRecordModel.created_at, ShowcaseAuditRecordModel.internal_id)
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

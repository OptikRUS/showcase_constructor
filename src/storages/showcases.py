from dataclasses import dataclass

from sqlalchemy import and_, delete, insert, literal, select, update
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.public_config.projections import public_config_snapshot_from_json
from src.core.public_config.schemas import PublishedPublicConfigSnapshot
from src.core.showcases.exceptions import (
    AdminShowcaseDraftBlockNotFoundError,
    AdminShowcaseDraftOfferNotFoundError,
    AdminShowcaseNotFoundError,
    AdminShowcasePublicIdCollisionError,
    PublicShowcaseNotFoundError,
)
from src.core.showcases.schemas import (
    AdminShowcase,
    AdminShowcaseDraft,
    AdminShowcaseDraftBlock,
    AdminShowcaseDraftBlockCreateParams,
    AdminShowcaseDraftBlockPatchParams,
    AdminShowcaseDraftOffer,
    AdminShowcaseDraftOfferCreateParams,
    AdminShowcaseDraftOfferPatchParams,
    AdminShowcaseDraftSettingsPatchParams,
    AdminShowcasePublicationState,
    AdminShowcaseUpdateParams,
    JsonObject,
    JsonValue,
    PublishedRouteBinding,
    PublishedShowcaseSnapshot,
    ShowcaseAuditRecord,
)
from src.core.storages import AdminShowcaseStorage, PublicShowcaseStorage
from src.storages.models import (
    AdminShowcaseDraftBlockModel,
    AdminShowcaseDraftOfferModel,
    AdminShowcaseModel,
    PublishedRouteBindingModel,
    PublishedShowcaseSnapshotModel,
    ShowcaseAuditRecordModel,
)

DRAFT_OFFER_UPDATE_FIELD_NAMES = (
    "block_id",
    "enabled",
    "manual_order",
    "cta_text",
    "usp_text",
    "fields",
    "categories",
    "logo_url",
    "rounded_logo_url",
    "display_name",
    "site_name",
    "cpa_url",
    "legal_entity",
    "inn",
    "erid",
    "data",
)

UNSAFE_AUDIT_METADATA_KEY_PARTS = (
    "accesskey",
    "accesstoken",
    "custombodycode",
    "customheadcode",
    "draftsettings",
    "password",
    "publishedsnapshot",
    "rawpii",
    "refreshtoken",
    "secret",
    "serversecret",
    "snapshot",
    "token",
)
UNSAFE_AUDIT_METADATA_KEYS = frozenset(
    {
        "body",
        "custombody",
        "customcode",
        "customhead",
        "draft",
        "email",
        "head",
        "phone",
        "pii",
    }
)


@dataclass(frozen=True, slots=True, kw_only=True)
class DatabaseAdminShowcaseStorage(AdminShowcaseStorage, PublicShowcaseStorage):
    session: AsyncSession

    async def get_active_public_config_snapshot(
        self,
        *,
        public_id: str,
    ) -> PublishedPublicConfigSnapshot:
        snapshot = await self.session.scalar(
            select(PublishedShowcaseSnapshotModel.snapshot)
            .join(
                AdminShowcaseModel,
                AdminShowcaseModel.active_published_snapshot_internal_id
                == PublishedShowcaseSnapshotModel.internal_id,
            )
            .where(
                AdminShowcaseModel.public_id == public_id,
                PublishedShowcaseSnapshotModel.public_id == public_id,
            )
        )

        if snapshot is None:
            raise PublicShowcaseNotFoundError

        return public_config_snapshot_from_json(snapshot=snapshot)

    async def resolve_active_public_config_snapshot(
        self,
        *,
        host: str,
        path: str,
    ) -> PublishedPublicConfigSnapshot:
        snapshot = await self.session.scalar(
            select(PublishedShowcaseSnapshotModel.snapshot)
            .join(
                AdminShowcaseModel,
                AdminShowcaseModel.active_published_snapshot_internal_id
                == PublishedShowcaseSnapshotModel.internal_id,
            )
            .join(
                PublishedRouteBindingModel,
                and_(
                    PublishedRouteBindingModel.showcase_id == AdminShowcaseModel.id,
                    PublishedRouteBindingModel.public_id
                    == PublishedShowcaseSnapshotModel.public_id,
                ),
            )
            .where(
                PublishedRouteBindingModel.host == host,
                PublishedRouteBindingModel.path == path,
                PublishedRouteBindingModel.active.is_(True),
            )
        )

        if snapshot is None:
            raise PublicShowcaseNotFoundError

        return public_config_snapshot_from_json(snapshot=snapshot)

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

    async def list_draft_offers(self, *, showcase_id: str) -> list[AdminShowcaseDraftOffer]:
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

    async def create_draft_offer(
        self,
        *,
        showcase_id: str,
        offer_id: str,
        params: AdminShowcaseDraftOfferCreateParams,
    ) -> AdminShowcaseDraftOffer:
        model = await self.session.scalar(
            insert(AdminShowcaseDraftOfferModel)
            .from_select(
                [
                    "showcase_internal_id",
                    "showcase_id",
                    "offer_id",
                    "block_id",
                    "enabled",
                    "manual_order",
                    "cta_text",
                    "usp_text",
                    "fields",
                    "categories",
                    "logo_url",
                    "rounded_logo_url",
                    "display_name",
                    "site_name",
                    "cpa_url",
                    "legal_entity",
                    "inn",
                    "erid",
                    "data",
                ],
                select(
                    AdminShowcaseModel.internal_id,
                    AdminShowcaseModel.id,
                    literal(offer_id),
                    literal(params.block_id),
                    literal(params.enabled),
                    literal(params.manual_order),
                    literal(params.cta_text),
                    literal(params.usp_text),
                    literal(params.fields, type_=JSONB),
                    literal(params.categories, type_=JSONB),
                    literal(params.logo_url),
                    literal(params.rounded_logo_url),
                    literal(params.display_name),
                    literal(params.site_name),
                    literal(params.cpa_url),
                    literal(params.legal_entity),
                    literal(params.inn),
                    literal(params.erid),
                    literal(params.data, type_=JSONB),
                ).where(AdminShowcaseModel.id == showcase_id),
            )
            .returning(AdminShowcaseDraftOfferModel)
        )

        if model is None:
            raise AdminShowcaseNotFoundError

        return model.to_domain()

    async def patch_draft_offer(
        self,
        *,
        showcase_id: str,
        offer_id: str,
        params: AdminShowcaseDraftOfferPatchParams,
    ) -> AdminShowcaseDraftOffer:
        if not params.values:
            return await self._get_draft_offer_by_id(showcase_id=showcase_id, offer_id=offer_id)

        model = await self.session.scalar(
            update(AdminShowcaseDraftOfferModel)
            .where(
                AdminShowcaseDraftOfferModel.showcase_id == showcase_id,
                AdminShowcaseDraftOfferModel.offer_id == offer_id,
            )
            .values(_draft_offer_update_values(params=params))
            .returning(AdminShowcaseDraftOfferModel)
        )

        if model is None:
            raise AdminShowcaseDraftOfferNotFoundError

        return model.to_domain()

    async def delete_draft_offer(self, *, showcase_id: str, offer_id: str) -> None:
        deleted_offer_id = await self.session.scalar(
            delete(AdminShowcaseDraftOfferModel)
            .where(
                AdminShowcaseDraftOfferModel.showcase_id == showcase_id,
                AdminShowcaseDraftOfferModel.offer_id == offer_id,
            )
            .returning(AdminShowcaseDraftOfferModel.offer_id)
        )

        if deleted_offer_id is None:
            raise AdminShowcaseDraftOfferNotFoundError

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

    async def create_published_snapshot(
        self,
        *,
        showcase_id: str,
        public_id: str,
        version: int,
        snapshot: JsonObject,
        created_by_user_id: str,
        created_by_partner_id: str,
    ) -> PublishedShowcaseSnapshot:
        model = await self.session.scalar(
            insert(PublishedShowcaseSnapshotModel)
            .from_select(
                [
                    "showcase_internal_id",
                    "showcase_id",
                    "public_id",
                    "version",
                    "snapshot",
                    "created_by_user_id",
                    "created_by_partner_id",
                ],
                select(
                    AdminShowcaseModel.internal_id,
                    AdminShowcaseModel.id,
                    literal(public_id),
                    literal(version),
                    literal(snapshot, type_=JSONB),
                    literal(created_by_user_id),
                    literal(created_by_partner_id),
                ).where(AdminShowcaseModel.id == showcase_id),
            )
            .returning(PublishedShowcaseSnapshotModel)
        )

        if model is None:
            raise AdminShowcaseNotFoundError

        return model.to_domain()

    async def ensure_showcase_public_id(
        self,
        *,
        showcase_id: str,
        public_id_candidate: str,
    ) -> str:
        current_public_id = await self.session.scalar(
            select(AdminShowcaseModel.public_id).where(AdminShowcaseModel.id == showcase_id)
        )

        if current_public_id is not None:
            return current_public_id

        candidate_exists = (
            select(AdminShowcaseModel.internal_id)
            .where(AdminShowcaseModel.public_id == public_id_candidate)
            .exists()
        )
        public_id = await self.session.scalar(
            update(AdminShowcaseModel)
            .where(
                AdminShowcaseModel.id == showcase_id,
                AdminShowcaseModel.public_id.is_(None),
                ~candidate_exists,
            )
            .values(public_id=literal(public_id_candidate))
            .returning(AdminShowcaseModel.public_id)
        )

        if public_id is not None:
            return public_id

        showcase_exists = await self.session.scalar(
            select(AdminShowcaseModel.id).where(AdminShowcaseModel.id == showcase_id)
        )
        if showcase_exists is None:
            raise AdminShowcaseNotFoundError

        raise AdminShowcasePublicIdCollisionError

    async def public_id_exists(self, *, public_id: str) -> bool:
        existing_public_id = await self.session.scalar(
            select(AdminShowcaseModel.public_id).where(
                AdminShowcaseModel.public_id == public_id
            )
        )

        return existing_public_id is not None

    async def activate_published_snapshot(
        self,
        *,
        showcase_id: str,
        public_id: str,
        version: int,
        snapshot: JsonObject,
    ) -> AdminShowcasePublicationState:
        snapshot_internal_id = (
            select(PublishedShowcaseSnapshotModel.internal_id)
            .where(
                PublishedShowcaseSnapshotModel.showcase_id == showcase_id,
                PublishedShowcaseSnapshotModel.public_id == public_id,
                PublishedShowcaseSnapshotModel.version == version,
            )
            .scalar_subquery()
        )
        model = await self.session.scalar(
            update(AdminShowcaseModel)
            .where(AdminShowcaseModel.id == showcase_id)
            .values(
                public_id=public_id,
                publication_version=version,
                active_published_snapshot_internal_id=snapshot_internal_id,
                published_snapshot=snapshot,
            )
            .returning(AdminShowcaseModel)
        )

        if model is None:
            raise AdminShowcaseNotFoundError

        return model.to_publication_state_domain()

    async def deactivate_published_showcase(
        self,
        *,
        showcase_id: str,
        version: int,
    ) -> AdminShowcasePublicationState:
        model = await self.session.scalar(
            update(AdminShowcaseModel)
            .where(AdminShowcaseModel.id == showcase_id)
            .values(
                publication_version=version,
                active_published_snapshot_internal_id=None,
                published_snapshot=None,
            )
            .returning(AdminShowcaseModel)
        )

        if model is None:
            raise AdminShowcaseNotFoundError

        return model.to_publication_state_domain()

    async def list_published_snapshots(
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

    async def create_published_route_binding(
        self,
        *,
        showcase_id: str,
        public_id: str,
        host: str,
        path: str,
    ) -> PublishedRouteBinding:
        reactivated_model = await self.session.scalar(
            update(PublishedRouteBindingModel)
            .where(
                PublishedRouteBindingModel.showcase_id == showcase_id,
                PublishedRouteBindingModel.public_id == public_id,
                PublishedRouteBindingModel.host == host,
                PublishedRouteBindingModel.path == path,
                PublishedRouteBindingModel.active.is_(False),
            )
            .values(active=True)
            .returning(PublishedRouteBindingModel)
        )

        if reactivated_model is not None:
            return reactivated_model.to_domain()

        model = await self.session.scalar(
            insert(PublishedRouteBindingModel)
            .from_select(
                [
                    "showcase_internal_id",
                    "showcase_id",
                    "public_id",
                    "host",
                    "path",
                ],
                select(
                    AdminShowcaseModel.internal_id,
                    AdminShowcaseModel.id,
                    literal(public_id),
                    literal(host),
                    literal(path),
                ).where(AdminShowcaseModel.id == showcase_id),
            )
            .returning(PublishedRouteBindingModel)
        )

        if model is None:
            raise AdminShowcaseNotFoundError

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

    async def append_showcase_audit_record(
        self,
        *,
        showcase_id: str,
        action: str,
        actor_user_id: str,
        actor_partner_id: str,
        metadata: JsonObject,
    ) -> ShowcaseAuditRecord:
        model = await self.session.scalar(
            insert(ShowcaseAuditRecordModel)
            .from_select(
                [
                    "showcase_internal_id",
                    "showcase_id",
                    "action",
                    "actor_user_id",
                    "actor_partner_id",
                    "metadata",
                ],
                select(
                    AdminShowcaseModel.internal_id,
                    AdminShowcaseModel.id,
                    literal(action),
                    literal(actor_user_id),
                    literal(actor_partner_id),
                    literal(_safe_audit_metadata(metadata=metadata), type_=JSONB),
                ).where(AdminShowcaseModel.id == showcase_id),
            )
            .returning(ShowcaseAuditRecordModel)
        )

        if model is None:
            raise AdminShowcaseNotFoundError

        return model.to_domain()

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

    async def _get_draft_offer_by_id(
        self,
        *,
        showcase_id: str,
        offer_id: str,
    ) -> AdminShowcaseDraftOffer:
        model = await self.session.scalar(
            select(AdminShowcaseDraftOfferModel).where(
                AdminShowcaseDraftOfferModel.showcase_id == showcase_id,
                AdminShowcaseDraftOfferModel.offer_id == offer_id,
            )
        )

        if model is None:
            raise AdminShowcaseDraftOfferNotFoundError

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


def _draft_offer_update_values(
    *,
    params: AdminShowcaseDraftOfferPatchParams,
) -> dict[str, object]:
    values: dict[str, object] = {}
    for field_name in DRAFT_OFFER_UPDATE_FIELD_NAMES:
        if field_name in params.values:
            values[field_name] = params.values[field_name]

    return values


def _safe_audit_metadata(*, metadata: JsonObject) -> JsonObject:
    safe_metadata: JsonObject = {}

    for key, value in metadata.items():
        if _is_unsafe_audit_metadata_key(key=key):
            continue
        safe_metadata[key] = _safe_audit_metadata_value(value=value)

    return safe_metadata


def _safe_audit_metadata_value(*, value: JsonValue) -> JsonValue:
    if isinstance(value, dict):
        return _safe_audit_metadata(metadata=value)
    if isinstance(value, list):
        return [_safe_audit_metadata_value(value=item) for item in value]

    return value


def _is_unsafe_audit_metadata_key(*, key: str) -> bool:
    normalized_key = key.replace("-", "").replace("_", "").lower()

    if normalized_key in UNSAFE_AUDIT_METADATA_KEYS:
        return True

    return any(part in normalized_key for part in UNSAFE_AUDIT_METADATA_KEY_PARTS)

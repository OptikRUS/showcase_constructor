from dataclasses import dataclass, replace
from secrets import token_urlsafe
from uuid import UUID

from src.core.admin_auth.schemas import AdminActorContext
from src.core.public_config.projections import (
    build_preview_public_config,
    build_published_public_config,
    public_config_snapshot_to_json,
    render_preview_html,
)
from src.core.showcases.cache import PublicShowcaseCacheInvalidator
from src.core.showcases.exceptions import (
    AdminShowcaseDraftBlockNotFoundError,
    AdminShowcasePublicationValidationError,
    ShowcaseAccessDeniedError,
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
    AdminShowcasePreview,
    AdminShowcasePreviewMode,
    AdminShowcasePublication,
    AdminShowcaseUpdateParams,
    JsonObject,
)
from src.core.storages import AdminShowcaseStorage

CUSTOM_CODE_WARNING = (
    "Custom frontend code is stored as owner-controlled frontend data; "
    "backend execution is disabled."
)
CUSTOM_CODE_AUDIT_FIELDS = {
    "custom_head_code": "customHeadCode",
    "custom_body_code": "customBodyCode",
}
CUSTOM_CODE_AUDIT_LOCATIONS = {
    "custom_head_code": "head",
    "custom_body_code": "body",
}
PUBLIC_ID_GENERATION_ATTEMPTS = 5


@dataclass(frozen=True, slots=True, kw_only=True)
class GetAdminShowcaseUseCase:
    storage: AdminShowcaseStorage

    async def execute(self, *, showcase_id: str, context: AdminActorContext) -> AdminShowcase:
        showcase = await self.storage.get_by_id(showcase_id=showcase_id)

        if showcase.owner_partner_id != context.partner_id:
            raise ShowcaseAccessDeniedError

        return showcase


@dataclass(frozen=True, slots=True, kw_only=True)
class UpdateAdminShowcaseUseCase:
    storage: AdminShowcaseStorage

    async def execute(
        self,
        *,
        showcase_id: str,
        params: AdminShowcaseUpdateParams,
        context: AdminActorContext,
    ) -> AdminShowcase:
        showcase = await self.storage.get_by_id(showcase_id=showcase_id)

        if showcase.owner_partner_id != context.partner_id:
            raise ShowcaseAccessDeniedError

        return await self.storage.update_draft(showcase_id=showcase_id, params=params)


@dataclass(frozen=True, slots=True, kw_only=True)
class UpdateAdminShowcaseDraftSettingsUseCase:
    storage: AdminShowcaseStorage

    async def execute(
        self,
        *,
        showcase_id: str,
        params: AdminShowcaseDraftSettingsPatchParams,
        context: AdminActorContext,
    ) -> AdminShowcaseDraft:
        showcase = await self.storage.get_by_id(showcase_id=showcase_id)

        if showcase.owner_partner_id != context.partner_id:
            raise ShowcaseAccessDeniedError

        updated_draft = await self.storage.update_draft_settings(
            showcase_id=showcase_id,
            params=params,
        )
        custom_code_fields = _custom_code_fields(params=params)
        if not custom_code_fields:
            return updated_draft

        await self.storage.append_showcase_audit_record(
            showcase_id=showcase_id,
            action="custom_code_updated",
            actor_user_id=context.user_id,
            actor_partner_id=context.partner_id,
            metadata={
                "changed_fields": [
                    CUSTOM_CODE_AUDIT_FIELDS[field_name] for field_name in custom_code_fields
                ],
                "custom_code_locations": [
                    CUSTOM_CODE_AUDIT_LOCATIONS[field_name] for field_name in custom_code_fields
                ],
            },
        )

        return replace(updated_draft, custom_code_warning=CUSTOM_CODE_WARNING)


@dataclass(frozen=True, slots=True, kw_only=True)
class BuildAdminShowcasePreviewUseCase:
    storage: AdminShowcaseStorage

    async def execute(
        self,
        *,
        showcase_id: str,
        mode: AdminShowcasePreviewMode,
        context: AdminActorContext,
    ) -> AdminShowcasePreview:
        showcase = await self.storage.get_by_id(showcase_id=showcase_id)

        if showcase.owner_partner_id != context.partner_id:
            raise ShowcaseAccessDeniedError

        draft = await self.storage.get_draft_by_id(showcase_id=showcase_id)
        blocks = await self.storage.list_draft_blocks(showcase_id=showcase_id)
        offers = await self.storage.list_draft_offers(showcase_id=showcase_id)
        config = build_preview_public_config(draft=draft, blocks=blocks, offers=offers)

        return AdminShowcasePreview(
            preview=True,
            mode=mode,
            config=config,
            html=render_preview_html(
                config=config,
                mode=mode,
                settings=draft.settings,
            ),
        )


@dataclass(frozen=True, slots=True, kw_only=True)
class PublishAdminShowcaseUseCase:
    storage: AdminShowcaseStorage
    cache_invalidator: PublicShowcaseCacheInvalidator

    async def execute(
        self,
        *,
        showcase_id: str,
        context: AdminActorContext,
    ) -> AdminShowcasePublication:
        showcase = await self.storage.get_by_id(showcase_id=showcase_id)

        if showcase.owner_partner_id != context.partner_id:
            raise ShowcaseAccessDeniedError

        draft = await self.storage.get_draft_by_id(showcase_id=showcase_id)
        blocks = await self.storage.list_draft_blocks(showcase_id=showcase_id)
        offers = await self.storage.list_draft_offers(showcase_id=showcase_id)
        _validate_publishable_draft(draft=draft, offers=offers)

        public_id = showcase.public_id or await _new_showcase_public_id(storage=self.storage)
        version = showcase.publication_version + 1
        config = build_published_public_config(
            draft=draft,
            blocks=blocks,
            offers=offers,
            public_id=public_id,
        )
        snapshot = public_config_snapshot_to_json(snapshot=config)
        await self.storage.append_showcase_audit_record(
            showcase_id=showcase_id,
            action="showcase_published",
            actor_user_id=context.user_id,
            actor_partner_id=context.partner_id,
            metadata={"public_id": public_id, "version": version},
        )
        created_snapshot = await self.storage.create_published_snapshot(
            showcase_id=showcase_id,
            public_id=public_id,
            version=version,
            snapshot=snapshot,
            created_by_user_id=context.user_id,
            created_by_partner_id=context.partner_id,
        )
        state = await self.storage.activate_published_snapshot(
            showcase_id=showcase_id,
            public_id=public_id,
            version=version,
            snapshot=created_snapshot.snapshot,
        )
        await self.cache_invalidator.invalidate_public_showcase(public_id=public_id)

        return AdminShowcasePublication(
            id=state.id,
            public_id=public_id,
            version=state.version,
            published=True,
        )


@dataclass(frozen=True, slots=True, kw_only=True)
class UnpublishAdminShowcaseUseCase:
    storage: AdminShowcaseStorage
    cache_invalidator: PublicShowcaseCacheInvalidator

    async def execute(
        self,
        *,
        showcase_id: str,
        context: AdminActorContext,
    ) -> AdminShowcasePublication:
        showcase = await self.storage.get_by_id(showcase_id=showcase_id)

        if showcase.owner_partner_id != context.partner_id:
            raise ShowcaseAccessDeniedError

        if showcase.public_id is None or showcase.published_snapshot is None:
            raise AdminShowcasePublicationValidationError(
                detail="ADMIN_SHOWCASE_PUBLICATION_NOT_ACTIVE"
            )

        version = showcase.publication_version + 1
        await self.storage.append_showcase_audit_record(
            showcase_id=showcase_id,
            action="showcase_unpublished",
            actor_user_id=context.user_id,
            actor_partner_id=context.partner_id,
            metadata={"public_id": showcase.public_id, "version": version},
        )
        state = await self.storage.deactivate_published_showcase(
            showcase_id=showcase_id,
            version=version,
        )
        await self.storage.deactivate_published_route_bindings(
            showcase_id=showcase_id,
            public_id=showcase.public_id,
        )
        await self.cache_invalidator.invalidate_public_showcase(public_id=showcase.public_id)

        return AdminShowcasePublication(
            id=state.id,
            public_id=showcase.public_id,
            version=state.version,
            published=False,
        )


def _custom_code_fields(*, params: AdminShowcaseDraftSettingsPatchParams) -> list[str]:
    return [
        field_name
        for field_name in CUSTOM_CODE_AUDIT_FIELDS
        if field_name in params.settings
    ]


async def _new_showcase_public_id(
    *,
    storage: AdminShowcaseStorage,
) -> str:
    for _ in range(PUBLIC_ID_GENERATION_ATTEMPTS):
        public_id_candidate = _new_public_id_candidate()
        if not await storage.public_id_exists(public_id=public_id_candidate):
            return public_id_candidate

    raise AdminShowcasePublicationValidationError(
        detail="ADMIN_SHOWCASE_PUBLIC_ID_COLLISION"
    )


def _validate_publishable_draft(
    *,
    draft: AdminShowcaseDraft,
    offers: list[AdminShowcaseDraftOffer],
) -> None:
    if _str_setting(settings=draft.settings, key="affiliate_id") is None:
        raise AdminShowcasePublicationValidationError(
            detail="ADMIN_SHOWCASE_PUBLICATION_REQUIRES_AFFILIATE_ID"
        )
    if _str_setting(settings=draft.settings, key="type") is None:
        raise AdminShowcasePublicationValidationError(
            detail="ADMIN_SHOWCASE_PUBLICATION_REQUIRES_TYPE"
        )
    if not any(offer.enabled for offer in offers) and _configured_fallback(draft=draft) is None:
        raise AdminShowcasePublicationValidationError(
            detail="ADMIN_SHOWCASE_PUBLICATION_REQUIRES_AVAILABLE_OFFER_OR_FALLBACK"
        )


def _configured_fallback(*, draft: AdminShowcaseDraft) -> str | None:
    fallback_text = _str_setting(settings=draft.settings, key="fallback_text")
    if fallback_text is None or not fallback_text.strip():
        return None

    return fallback_text


def _str_setting(*, settings: JsonObject, key: str) -> str | None:
    value = settings.get(key)
    return value if isinstance(value, str) and value.strip() else None


def _new_public_id_candidate() -> str:
    return token_urlsafe(24)


@dataclass(frozen=True, slots=True, kw_only=True)
class ListAdminShowcaseBlocksUseCase:
    storage: AdminShowcaseStorage

    async def execute(
        self,
        *,
        showcase_id: str,
        context: AdminActorContext,
    ) -> list[AdminShowcaseDraftBlock]:
        showcase = await self.storage.get_by_id(showcase_id=showcase_id)

        if showcase.owner_partner_id != context.partner_id:
            raise ShowcaseAccessDeniedError

        return await self.storage.list_draft_blocks(showcase_id=showcase_id)


@dataclass(frozen=True, slots=True, kw_only=True)
class CreateAdminShowcaseBlockUseCase:
    storage: AdminShowcaseStorage
    block_id: UUID

    async def execute(
        self,
        *,
        showcase_id: str,
        params: AdminShowcaseDraftBlockCreateParams,
        context: AdminActorContext,
    ) -> AdminShowcaseDraftBlock:
        showcase = await self.storage.get_by_id(showcase_id=showcase_id)

        if showcase.owner_partner_id != context.partner_id:
            raise ShowcaseAccessDeniedError

        return await self.storage.create_draft_block(
            showcase_id=showcase_id,
            block_id=str(self.block_id),
            params=params,
        )


@dataclass(frozen=True, slots=True, kw_only=True)
class PatchAdminShowcaseBlockUseCase:
    storage: AdminShowcaseStorage

    async def execute(
        self,
        *,
        showcase_id: str,
        block_id: str,
        params: AdminShowcaseDraftBlockPatchParams,
        context: AdminActorContext,
    ) -> AdminShowcaseDraftBlock:
        showcase = await self.storage.get_by_id(showcase_id=showcase_id)

        if showcase.owner_partner_id != context.partner_id:
            raise ShowcaseAccessDeniedError

        return await self.storage.patch_draft_block(
            showcase_id=showcase_id,
            block_id=block_id,
            params=params,
        )


@dataclass(frozen=True, slots=True, kw_only=True)
class DeleteAdminShowcaseBlockUseCase:
    storage: AdminShowcaseStorage

    async def execute(
        self,
        *,
        showcase_id: str,
        block_id: str,
        context: AdminActorContext,
    ) -> None:
        showcase = await self.storage.get_by_id(showcase_id=showcase_id)

        if showcase.owner_partner_id != context.partner_id:
            raise ShowcaseAccessDeniedError

        await self.storage.delete_draft_block(showcase_id=showcase_id, block_id=block_id)


@dataclass(frozen=True, slots=True, kw_only=True)
class ListAdminShowcaseOffersUseCase:
    storage: AdminShowcaseStorage

    async def execute(
        self,
        *,
        showcase_id: str,
        context: AdminActorContext,
    ) -> list[AdminShowcaseDraftOffer]:
        showcase = await self.storage.get_by_id(showcase_id=showcase_id)

        if showcase.owner_partner_id != context.partner_id:
            raise ShowcaseAccessDeniedError

        return await self.storage.list_draft_offers(showcase_id=showcase_id)


@dataclass(frozen=True, slots=True, kw_only=True)
class CreateAdminShowcaseOfferUseCase:
    storage: AdminShowcaseStorage
    offer_id: UUID

    async def execute(
        self,
        *,
        showcase_id: str,
        params: AdminShowcaseDraftOfferCreateParams,
        context: AdminActorContext,
    ) -> AdminShowcaseDraftOffer:
        showcase = await self.storage.get_by_id(showcase_id=showcase_id)

        if showcase.owner_partner_id != context.partner_id:
            raise ShowcaseAccessDeniedError

        if params.block_id is not None:
            blocks = await self.storage.list_draft_blocks(showcase_id=showcase_id)
            if params.block_id not in {block.id for block in blocks}:
                raise AdminShowcaseDraftBlockNotFoundError

        return await self.storage.create_draft_offer(
            showcase_id=showcase_id,
            offer_id=str(self.offer_id),
            params=params,
        )


@dataclass(frozen=True, slots=True, kw_only=True)
class PatchAdminShowcaseOfferUseCase:
    storage: AdminShowcaseStorage

    async def execute(
        self,
        *,
        showcase_id: str,
        offer_id: str,
        params: AdminShowcaseDraftOfferPatchParams,
        context: AdminActorContext,
    ) -> AdminShowcaseDraftOffer:
        showcase = await self.storage.get_by_id(showcase_id=showcase_id)

        if showcase.owner_partner_id != context.partner_id:
            raise ShowcaseAccessDeniedError

        requested_block_id = params.values.get("block_id")
        if requested_block_id is not None:
            if not isinstance(requested_block_id, str):
                raise AdminShowcaseDraftBlockNotFoundError

            blocks = await self.storage.list_draft_blocks(showcase_id=showcase_id)
            if requested_block_id not in {block.id for block in blocks}:
                raise AdminShowcaseDraftBlockNotFoundError

        return await self.storage.patch_draft_offer(
            showcase_id=showcase_id,
            offer_id=offer_id,
            params=params,
        )


@dataclass(frozen=True, slots=True, kw_only=True)
class DeleteAdminShowcaseOfferUseCase:
    storage: AdminShowcaseStorage

    async def execute(
        self,
        *,
        showcase_id: str,
        offer_id: str,
        context: AdminActorContext,
    ) -> None:
        showcase = await self.storage.get_by_id(showcase_id=showcase_id)

        if showcase.owner_partner_id != context.partner_id:
            raise ShowcaseAccessDeniedError

        await self.storage.delete_draft_offer(showcase_id=showcase_id, offer_id=offer_id)

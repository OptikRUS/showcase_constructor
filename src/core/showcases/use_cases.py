from dataclasses import dataclass, replace
from uuid import UUID

from src.core.admin_auth.schemas import AdminActorContext
from src.core.showcases.exceptions import (
    AdminShowcaseDraftBlockNotFoundError,
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
    AdminShowcaseUpdateParams,
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


def _custom_code_fields(*, params: AdminShowcaseDraftSettingsPatchParams) -> list[str]:
    return [
        field_name
        for field_name in CUSTOM_CODE_AUDIT_FIELDS
        if field_name in params.settings
    ]


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

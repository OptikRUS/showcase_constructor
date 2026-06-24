from dataclasses import dataclass
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
    AdminShowcaseDraftSettingsPatchParams,
    AdminShowcaseUpdateParams,
)
from src.core.storages import AdminShowcaseStorage


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

        return await self.storage.update_draft_settings(showcase_id=showcase_id, params=params)


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

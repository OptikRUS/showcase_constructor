from abc import ABCMeta, abstractmethod

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


class AdminShowcaseStorage(metaclass=ABCMeta):
    @abstractmethod
    async def get_by_id(self, *, showcase_id: str) -> AdminShowcase: ...

    @abstractmethod
    async def get_draft_by_id(self, *, showcase_id: str) -> AdminShowcaseDraft: ...

    @abstractmethod
    async def update_draft(
        self,
        *,
        showcase_id: str,
        params: AdminShowcaseUpdateParams,
    ) -> AdminShowcase: ...

    @abstractmethod
    async def update_draft_settings(
        self,
        *,
        showcase_id: str,
        params: AdminShowcaseDraftSettingsPatchParams,
    ) -> AdminShowcaseDraft: ...

    @abstractmethod
    async def list_draft_blocks(self, *, showcase_id: str) -> list[AdminShowcaseDraftBlock]: ...

    @abstractmethod
    async def create_draft_block(
        self,
        *,
        showcase_id: str,
        block_id: str,
        params: AdminShowcaseDraftBlockCreateParams,
    ) -> AdminShowcaseDraftBlock: ...

    @abstractmethod
    async def patch_draft_block(
        self,
        *,
        showcase_id: str,
        block_id: str,
        params: AdminShowcaseDraftBlockPatchParams,
    ) -> AdminShowcaseDraftBlock: ...

    @abstractmethod
    async def delete_draft_block(self, *, showcase_id: str, block_id: str) -> None: ...

    @abstractmethod
    async def list_draft_offers(self, *, showcase_id: str) -> list[AdminShowcaseDraftOffer]: ...

    @abstractmethod
    async def create_draft_offer(
        self,
        *,
        showcase_id: str,
        offer_id: str,
        params: AdminShowcaseDraftOfferCreateParams,
    ) -> AdminShowcaseDraftOffer: ...

    @abstractmethod
    async def patch_draft_offer(
        self,
        *,
        showcase_id: str,
        offer_id: str,
        params: AdminShowcaseDraftOfferPatchParams,
    ) -> AdminShowcaseDraftOffer: ...

    @abstractmethod
    async def delete_draft_offer(self, *, showcase_id: str, offer_id: str) -> None: ...

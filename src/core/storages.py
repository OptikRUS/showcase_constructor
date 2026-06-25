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
    JsonObject,
    PublishedRouteBinding,
    PublishedShowcaseSnapshot,
    ShowcaseAuditRecord,
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

    @abstractmethod
    async def create_published_snapshot(
        self,
        *,
        showcase_id: str,
        public_id: str,
        version: int,
        snapshot: JsonObject,
        created_by_user_id: str,
        created_by_partner_id: str,
    ) -> PublishedShowcaseSnapshot: ...

    @abstractmethod
    async def list_published_snapshots(
        self,
        *,
        showcase_id: str,
    ) -> list[PublishedShowcaseSnapshot]: ...

    @abstractmethod
    async def create_published_route_binding(
        self,
        *,
        showcase_id: str,
        public_id: str,
        host: str,
        path: str,
    ) -> PublishedRouteBinding: ...

    @abstractmethod
    async def list_published_route_bindings(
        self,
        *,
        showcase_id: str,
    ) -> list[PublishedRouteBinding]: ...

    @abstractmethod
    async def append_showcase_audit_record(
        self,
        *,
        showcase_id: str,
        action: str,
        actor_user_id: str,
        actor_partner_id: str,
        metadata: JsonObject,
    ) -> ShowcaseAuditRecord: ...

    @abstractmethod
    async def list_showcase_audit_records(
        self,
        *,
        showcase_id: str,
    ) -> list[ShowcaseAuditRecord]: ...

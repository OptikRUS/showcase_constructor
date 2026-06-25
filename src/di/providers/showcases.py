from uuid import UUID

from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.showcases.cache import PublicShowcaseCacheInvalidator
from src.core.showcases.use_cases import (
    BuildAdminShowcasePreviewUseCase,
    CreateAdminShowcaseBlockUseCase,
    CreateAdminShowcaseOfferUseCase,
    DeleteAdminShowcaseBlockUseCase,
    DeleteAdminShowcaseOfferUseCase,
    ListAdminShowcaseBlocksUseCase,
    ListAdminShowcaseOffersUseCase,
    PatchAdminShowcaseBlockUseCase,
    PatchAdminShowcaseOfferUseCase,
    PublishAdminShowcaseUseCase,
    UnpublishAdminShowcaseUseCase,
    UpdateAdminShowcaseDraftSettingsUseCase,
)
from src.core.storages import AdminShowcaseStorage
from src.services.showcases import NoopPublicShowcaseCacheInvalidator
from src.storages.showcases import DatabaseAdminShowcaseStorage


class ShowcaseProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def get_admin_showcase_storage(self, session: AsyncSession) -> AdminShowcaseStorage:
        return DatabaseAdminShowcaseStorage(session=session)

    @provide(scope=Scope.REQUEST)
    def get_public_showcase_cache_invalidator(self) -> PublicShowcaseCacheInvalidator:
        return NoopPublicShowcaseCacheInvalidator()

    @provide(scope=Scope.REQUEST)
    def get_update_admin_showcase_draft_settings_use_case(
        self,
        storage: AdminShowcaseStorage,
    ) -> UpdateAdminShowcaseDraftSettingsUseCase:
        return UpdateAdminShowcaseDraftSettingsUseCase(storage=storage)

    @provide(scope=Scope.REQUEST)
    def get_build_admin_showcase_preview_use_case(
        self,
        storage: AdminShowcaseStorage,
    ) -> BuildAdminShowcasePreviewUseCase:
        return BuildAdminShowcasePreviewUseCase(storage=storage)

    @provide(scope=Scope.REQUEST)
    def get_publish_admin_showcase_use_case(
        self,
        storage: AdminShowcaseStorage,
        cache_invalidator: PublicShowcaseCacheInvalidator,
    ) -> PublishAdminShowcaseUseCase:
        return PublishAdminShowcaseUseCase(
            storage=storage,
            cache_invalidator=cache_invalidator,
        )

    @provide(scope=Scope.REQUEST)
    def get_unpublish_admin_showcase_use_case(
        self,
        storage: AdminShowcaseStorage,
        cache_invalidator: PublicShowcaseCacheInvalidator,
    ) -> UnpublishAdminShowcaseUseCase:
        return UnpublishAdminShowcaseUseCase(
            storage=storage,
            cache_invalidator=cache_invalidator,
        )

    @provide(scope=Scope.REQUEST)
    def get_list_admin_showcase_blocks_use_case(
        self,
        storage: AdminShowcaseStorage,
    ) -> ListAdminShowcaseBlocksUseCase:
        return ListAdminShowcaseBlocksUseCase(storage=storage)

    @provide(scope=Scope.REQUEST)
    def get_create_admin_showcase_block_use_case(
        self,
        storage: AdminShowcaseStorage,
        block_id: UUID,
    ) -> CreateAdminShowcaseBlockUseCase:
        return CreateAdminShowcaseBlockUseCase(storage=storage, block_id=block_id)

    @provide(scope=Scope.REQUEST)
    def get_patch_admin_showcase_block_use_case(
        self,
        storage: AdminShowcaseStorage,
    ) -> PatchAdminShowcaseBlockUseCase:
        return PatchAdminShowcaseBlockUseCase(storage=storage)

    @provide(scope=Scope.REQUEST)
    def get_delete_admin_showcase_block_use_case(
        self,
        storage: AdminShowcaseStorage,
    ) -> DeleteAdminShowcaseBlockUseCase:
        return DeleteAdminShowcaseBlockUseCase(storage=storage)

    @provide(scope=Scope.REQUEST)
    def get_list_admin_showcase_offers_use_case(
        self,
        storage: AdminShowcaseStorage,
    ) -> ListAdminShowcaseOffersUseCase:
        return ListAdminShowcaseOffersUseCase(storage=storage)

    @provide(scope=Scope.REQUEST)
    def get_create_admin_showcase_offer_use_case(
        self,
        storage: AdminShowcaseStorage,
        offer_id: UUID,
    ) -> CreateAdminShowcaseOfferUseCase:
        return CreateAdminShowcaseOfferUseCase(storage=storage, offer_id=offer_id)

    @provide(scope=Scope.REQUEST)
    def get_patch_admin_showcase_offer_use_case(
        self,
        storage: AdminShowcaseStorage,
    ) -> PatchAdminShowcaseOfferUseCase:
        return PatchAdminShowcaseOfferUseCase(storage=storage)

    @provide(scope=Scope.REQUEST)
    def get_delete_admin_showcase_offer_use_case(
        self,
        storage: AdminShowcaseStorage,
    ) -> DeleteAdminShowcaseOfferUseCase:
        return DeleteAdminShowcaseOfferUseCase(storage=storage)

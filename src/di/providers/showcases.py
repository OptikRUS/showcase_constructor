from uuid import UUID

from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.showcases.use_cases import (
    CreateAdminShowcaseBlockUseCase,
    CreateAdminShowcaseOfferUseCase,
    DeleteAdminShowcaseBlockUseCase,
    ListAdminShowcaseBlocksUseCase,
    ListAdminShowcaseOffersUseCase,
    PatchAdminShowcaseBlockUseCase,
    UpdateAdminShowcaseDraftSettingsUseCase,
)
from src.core.storages import AdminShowcaseStorage
from src.storages.showcases import DatabaseAdminShowcaseStorage


class ShowcaseProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def get_admin_showcase_storage(self, session: AsyncSession) -> AdminShowcaseStorage:
        return DatabaseAdminShowcaseStorage(session=session)

    @provide(scope=Scope.REQUEST)
    def get_update_admin_showcase_draft_settings_use_case(
        self,
        storage: AdminShowcaseStorage,
    ) -> UpdateAdminShowcaseDraftSettingsUseCase:
        return UpdateAdminShowcaseDraftSettingsUseCase(storage=storage)

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

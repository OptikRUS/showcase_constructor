from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.showcases.use_cases import UpdateAdminShowcaseDraftSettingsUseCase
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

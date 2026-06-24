from abc import ABCMeta, abstractmethod

from src.core.showcases.schemas import (
    AdminShowcase,
    AdminShowcaseDraft,
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

from dataclasses import dataclass

from src.core.admin_auth.schemas import AdminActorContext
from src.core.showcases.exceptions import ShowcaseAccessDeniedError
from src.core.showcases.schemas import AdminShowcase, AdminShowcaseUpdateParams
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

from dataclasses import dataclass

from src.core.public_config.schemas import PublishedPublicConfigSnapshot
from src.core.storages import PublicShowcaseStorage


@dataclass(frozen=True, slots=True, kw_only=True)
class GetPublishedPublicConfigUseCase:
    storage: PublicShowcaseStorage

    async def execute(self, *, public_id: str) -> PublishedPublicConfigSnapshot:
        return await self.storage.get_active_public_config_snapshot(public_id=public_id)


@dataclass(frozen=True, slots=True, kw_only=True)
class ResolvePublishedPublicConfigUseCase:
    storage: PublicShowcaseStorage

    async def execute(self, *, host: str, path: str) -> PublishedPublicConfigSnapshot:
        return await self.storage.resolve_active_public_config_snapshot(
            host=host,
            path=path,
        )

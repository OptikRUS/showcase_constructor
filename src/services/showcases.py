from dataclasses import dataclass

from src.core.showcases.cache import PublicShowcaseCacheInvalidator


@dataclass(frozen=True, slots=True)
class NoopPublicShowcaseCacheInvalidator(PublicShowcaseCacheInvalidator):
    async def invalidate_public_showcase(self, *, public_id: str) -> None:
        _ = public_id

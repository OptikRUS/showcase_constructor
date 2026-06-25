from abc import ABCMeta, abstractmethod


class PublicShowcaseCacheInvalidator(metaclass=ABCMeta):
    @abstractmethod
    async def invalidate_public_showcase(self, *, public_id: str) -> None: ...

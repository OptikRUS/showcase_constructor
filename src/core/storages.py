from abc import ABCMeta, abstractmethod

from src.core.showcases.schemas import AdminShowcase


class AdminShowcaseStorage(metaclass=ABCMeta):
    @abstractmethod
    async def get_by_id(self, *, showcase_id: str) -> AdminShowcase: ...

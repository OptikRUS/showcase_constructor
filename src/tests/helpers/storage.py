from dataclasses import dataclass

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


@dataclass(kw_only=True, slots=True)
class StorageHelper:
    session: AsyncSession

    async def get_current_alembic_version(self) -> str:
        result = await self.session.execute(text("select version_num from alembic_version"))

        return str(result.scalar_one())

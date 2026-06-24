from dataclasses import dataclass

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


@dataclass(kw_only=True, slots=True)
class StorageHelper:
    session: AsyncSession

    async def get_current_alembic_version(self) -> str:
        result = await self.session.execute(text("select version_num from alembic_version"))

        return str(result.scalar_one())

    async def get_public_table_names(self) -> set[str]:
        result = await self.session.execute(
            text(
                "select table_name "
                "from information_schema.tables "
                "where table_schema = 'public'"
            )
        )

        return {str(table_name) for table_name in result.scalars().all()}

    async def get_table_column_names(self, *, table_name: str) -> set[str]:
        result = await self.session.execute(
            text(
                "select column_name "
                "from information_schema.columns "
                "where table_schema = 'public' and table_name = :table_name"
            ),
            {"table_name": table_name},
        )

        return {str(column_name) for column_name in result.scalars().all()}

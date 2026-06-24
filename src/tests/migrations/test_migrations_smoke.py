from src.tests.fixtures import StorageFixture


class TestMigrationsSmoke(StorageFixture):
    async def test_upgrades_to_head_revision(self) -> None:
        version = await self.storage_helper.get_current_alembic_version()

        assert version == "0001"

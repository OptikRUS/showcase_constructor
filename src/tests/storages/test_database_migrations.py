from src.tests.fixtures import StorageFixture


class TestDatabaseMigrations(StorageFixture):
    async def test_upgrades_to_head_revision(self) -> None:
        version = await self.storage_helper.get_current_alembic_version()
        table_names = await self.storage_helper.get_public_table_names()
        showcase_columns = await self.storage_helper.get_table_column_names(table_name="showcases")
        block_columns = await self.storage_helper.get_table_column_names(table_name="draft_blocks")
        offer_columns = await self.storage_helper.get_table_column_names(table_name="draft_offers")

        assert version == "0002"
        assert {"showcases", "draft_blocks", "draft_offers"}.issubset(table_names)
        assert {
            "internal_id",
            "id",
            "owner_partner_id",
            "title",
            "draft_settings",
            "published_snapshot",
        }.issubset(showcase_columns)
        assert {
            "internal_id",
            "showcase_internal_id",
            "block_id",
            "type",
            "draft_order",
            "visible",
            "desktop_settings",
            "mobile_settings",
            "data",
        }.issubset(block_columns)
        assert {
            "internal_id",
            "showcase_internal_id",
            "offer_id",
            "enabled",
            "manual_order",
            "block_id",
            "fields",
            "categories",
            "cpa_url",
        }.issubset(offer_columns)

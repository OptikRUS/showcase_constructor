from src.tests.fixtures import StorageFixture


class TestDatabaseMigrations(StorageFixture):
    async def test_upgrades_to_head_revision(self) -> None:
        version = await self.storage_helper.get_current_alembic_version()
        table_names = await self.storage_helper.get_public_table_names()
        showcase_columns = await self.storage_helper.get_table_column_names(table_name="showcases")
        block_columns = await self.storage_helper.get_table_column_names(table_name="draft_blocks")
        offer_columns = await self.storage_helper.get_table_column_names(table_name="draft_offers")

        snapshot_columns = await self.storage_helper.get_table_column_names(
            table_name="published_showcase_snapshots"
        )
        route_binding_columns = await self.storage_helper.get_table_column_names(
            table_name="published_route_bindings"
        )
        audit_columns = await self.storage_helper.get_table_column_names(
            table_name="showcase_audit_records"
        )

        assert version == "0003"
        assert {
            "showcases",
            "draft_blocks",
            "draft_offers",
            "published_showcase_snapshots",
            "published_route_bindings",
            "showcase_audit_records",
        }.issubset(table_names)
        assert {
            "internal_id",
            "id",
            "owner_partner_id",
            "title",
            "draft_settings",
            "published_snapshot",
            "public_id",
            "publication_version",
            "active_published_snapshot_internal_id",
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
        assert {
            "internal_id",
            "showcase_internal_id",
            "showcase_id",
            "public_id",
            "version",
            "snapshot",
            "created_by_user_id",
            "created_by_partner_id",
            "created_at",
        }.issubset(snapshot_columns)
        assert {
            "internal_id",
            "showcase_internal_id",
            "showcase_id",
            "public_id",
            "host",
            "path",
            "active",
            "created_at",
        }.issubset(route_binding_columns)
        assert {
            "internal_id",
            "showcase_internal_id",
            "showcase_id",
            "action",
            "actor_user_id",
            "actor_partner_id",
            "metadata",
            "created_at",
        }.issubset(audit_columns)

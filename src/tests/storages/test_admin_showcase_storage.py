import pytest

from src.core.showcases.exceptions import (
    AdminShowcaseDraftBlockNotFoundError,
    AdminShowcaseDraftOfferNotFoundError,
    AdminShowcaseNotFoundError,
    PublicShowcaseNotFoundError,
)
from src.core.showcases.schemas import (
    AdminShowcaseDraftBlockCreateParams,
    AdminShowcaseDraftBlockPatchParams,
    AdminShowcaseDraftOfferCreateParams,
    AdminShowcaseDraftOfferPatchParams,
    AdminShowcaseDraftSettingsPatchParams,
    JsonObject,
)
from src.storages.showcases import DatabaseAdminShowcaseStorage
from src.tests.fixtures import FactoryFixture, StorageFixture


class TestDatabaseAdminShowcaseStorage(FactoryFixture, StorageFixture):
    async def test_creates_immutable_published_snapshots_with_public_metadata(self) -> None:
        await self.storage_helper.create_admin_showcase(
            id="showcase-publication-storage-1",
            owner_partner_id="partner-1",
            title="Publication storage showcase",
        )
        storage = DatabaseAdminShowcaseStorage(session=self.storage_helper.session)
        first_snapshot: JsonObject = {
            "id": "public-publication-storage-1",
            "settings": {"text_title": "First published title"},
            "blocks": [{"type": "offers", "title": "First offers"}],
        }
        second_snapshot: JsonObject = {
            "id": "public-publication-storage-1",
            "settings": {"text_title": "Second published title"},
            "blocks": [{"type": "offers", "title": "Second offers"}],
        }

        first = await storage.create_published_snapshot(
            showcase_id="showcase-publication-storage-1",
            public_id="public-publication-storage-1",
            version=1,
            snapshot=first_snapshot,
            created_by_user_id="admin-user-1",
            created_by_partner_id="partner-1",
        )
        second = await storage.create_published_snapshot(
            showcase_id="showcase-publication-storage-1",
            public_id="public-publication-storage-1",
            version=2,
            snapshot=second_snapshot,
            created_by_user_id="admin-user-2",
            created_by_partner_id="partner-1",
        )
        persisted = await self.storage_helper.list_published_showcase_snapshots(
            showcase_id="showcase-publication-storage-1"
        )

        assert first.showcase_id == "showcase-publication-storage-1"
        assert first.public_id == "public-publication-storage-1"
        assert first.version == 1
        assert first.snapshot == first_snapshot
        assert first.created_by_user_id == "admin-user-1"
        assert first.created_by_partner_id == "partner-1"
        assert first.created_at is not None
        assert not hasattr(first, "internal_id")
        assert second.version == 2
        assert [snapshot.version for snapshot in persisted] == [1, 2]
        assert [snapshot.snapshot for snapshot in persisted] == [
            first_snapshot,
            second_snapshot,
        ]

    async def test_creates_active_public_route_binding(self) -> None:
        await self.storage_helper.create_admin_showcase(
            id="showcase-route-binding-storage-1",
            owner_partner_id="partner-1",
            title="Route binding storage showcase",
        )
        storage = DatabaseAdminShowcaseStorage(session=self.storage_helper.session)

        created = await storage.create_published_route_binding(
            showcase_id="showcase-route-binding-storage-1",
            public_id="public-route-binding-storage-1",
            host="offers.example.test",
            path="/loans",
        )
        persisted = await self.storage_helper.list_published_route_bindings(
            showcase_id="showcase-route-binding-storage-1"
        )

        assert created.showcase_id == "showcase-route-binding-storage-1"
        assert created.public_id == "public-route-binding-storage-1"
        assert created.host == "offers.example.test"
        assert created.path == "/loans"
        assert created.active is True
        assert created.created_at is not None
        assert not hasattr(created, "internal_id")
        assert persisted == [created]

    async def test_assigns_stable_public_id_and_switches_active_published_snapshot(
        self,
    ) -> None:
        await self.storage_helper.create_admin_showcase(
            id="showcase-active-publication-storage",
            owner_partner_id="partner-1",
            title="Active publication storage showcase",
        )
        storage = DatabaseAdminShowcaseStorage(session=self.storage_helper.session)
        first_snapshot: JsonObject = {
            "id": "public-active-publication-storage",
            "settings": {"text_title": "First active title"},
        }
        second_snapshot: JsonObject = {
            "id": "public-active-publication-storage",
            "settings": {"text_title": "Second active title"},
        }

        public_id = await storage.ensure_showcase_public_id(
            showcase_id="showcase-active-publication-storage",
            public_id_candidate="public-active-publication-storage",
        )
        stable_public_id = await storage.ensure_showcase_public_id(
            showcase_id="showcase-active-publication-storage",
            public_id_candidate="ignored-public-id",
        )
        await storage.create_published_snapshot(
            showcase_id="showcase-active-publication-storage",
            public_id=public_id,
            version=1,
            snapshot=first_snapshot,
            created_by_user_id="admin-user-1",
            created_by_partner_id="partner-1",
        )
        first_state = await storage.activate_published_snapshot(
            showcase_id="showcase-active-publication-storage",
            public_id=public_id,
            version=1,
            snapshot=first_snapshot,
        )
        await storage.create_published_snapshot(
            showcase_id="showcase-active-publication-storage",
            public_id=public_id,
            version=2,
            snapshot=second_snapshot,
            created_by_user_id="admin-user-2",
            created_by_partner_id="partner-1",
        )
        second_state = await storage.activate_published_snapshot(
            showcase_id="showcase-active-publication-storage",
            public_id=public_id,
            version=2,
            snapshot=second_snapshot,
        )
        snapshots = await storage.list_published_snapshots(
            showcase_id="showcase-active-publication-storage"
        )

        assert public_id == "public-active-publication-storage"
        assert stable_public_id == public_id
        assert first_state.public_id == public_id
        assert first_state.version == 1
        assert first_state.active is True
        assert first_state.snapshot == first_snapshot
        assert second_state.public_id == public_id
        assert second_state.version == 2
        assert second_state.active is True
        assert second_state.snapshot == second_snapshot
        assert [snapshot.version for snapshot in snapshots] == [1, 2]
        assert [snapshot.snapshot for snapshot in snapshots] == [
            first_snapshot,
            second_snapshot,
        ]

    async def test_deactivates_public_visibility_without_deleting_snapshot_history(
        self,
    ) -> None:
        await self.storage_helper.create_admin_showcase(
            id="showcase-unpublish-storage",
            owner_partner_id="partner-1",
            title="Unpublish storage showcase",
        )
        storage = DatabaseAdminShowcaseStorage(session=self.storage_helper.session)
        snapshot: JsonObject = {
            "id": "public-unpublish-storage",
            "settings": {"text_title": "Active title"},
        }
        public_id = await storage.ensure_showcase_public_id(
            showcase_id="showcase-unpublish-storage",
            public_id_candidate="public-unpublish-storage",
        )
        await storage.create_published_snapshot(
            showcase_id="showcase-unpublish-storage",
            public_id=public_id,
            version=1,
            snapshot=snapshot,
            created_by_user_id="admin-user-1",
            created_by_partner_id="partner-1",
        )
        await storage.activate_published_snapshot(
            showcase_id="showcase-unpublish-storage",
            public_id=public_id,
            version=1,
            snapshot=snapshot,
        )
        route_binding = await storage.create_published_route_binding(
            showcase_id="showcase-unpublish-storage",
            public_id=public_id,
            host="unpublish-storage.example.test",
            path="/offers",
        )

        state = await storage.deactivate_published_showcase(
            showcase_id="showcase-unpublish-storage",
            version=2,
        )
        await storage.deactivate_published_route_bindings(
            showcase_id="showcase-unpublish-storage",
            public_id=public_id,
        )
        snapshots = await storage.list_published_snapshots(
            showcase_id="showcase-unpublish-storage"
        )
        route_bindings = await storage.list_published_route_bindings(
            showcase_id="showcase-unpublish-storage"
        )

        assert route_binding.active is True
        assert state.public_id == public_id
        assert state.version == 2
        assert state.active is False
        assert state.snapshot is None
        assert len(snapshots) == 1
        assert snapshots[0].snapshot == snapshot
        assert route_bindings[0].active is False

    async def test_gets_active_public_config_snapshot_by_public_id_only(self) -> None:
        await self.storage_helper.create_admin_showcase(
            id="showcase-active-public-read-storage",
            owner_partner_id="partner-1",
            title="Active public read storage showcase",
        )
        storage = DatabaseAdminShowcaseStorage(session=self.storage_helper.session)
        old_snapshot = self.factory.published_public_config_snapshot_payload(
            public_id="public-active-read-storage",
            text_title="Old inactive title",
        )
        active_snapshot = self.factory.published_public_config_snapshot_payload(
            public_id="public-active-read-storage",
            affiliate_id="affiliate-active-read-storage",
            text_title="Active public title",
            custom_head_code="<script>window.activeStorageHead = true</script>",
            custom_body_code="<noscript>active storage body</noscript>",
        )
        await storage.create_published_snapshot(
            showcase_id="showcase-active-public-read-storage",
            public_id="public-active-read-storage",
            version=1,
            snapshot=old_snapshot,
            created_by_user_id="admin-user-1",
            created_by_partner_id="partner-1",
        )
        await storage.create_published_snapshot(
            showcase_id="showcase-active-public-read-storage",
            public_id="public-active-read-storage",
            version=2,
            snapshot=active_snapshot,
            created_by_user_id="admin-user-1",
            created_by_partner_id="partner-1",
        )
        await storage.activate_published_snapshot(
            showcase_id="showcase-active-public-read-storage",
            public_id="public-active-read-storage",
            version=2,
            snapshot=active_snapshot,
        )

        result = await storage.get_active_public_config_snapshot(
            public_id="public-active-read-storage"
        )

        assert result.id == "public-active-read-storage"
        assert result.affiliate_id == "affiliate-active-read-storage"
        assert result.settings.text_title == "Active public title"
        assert result.custom_head_code == "<script>window.activeStorageHead = true</script>"
        assert result.custom_body_code == "<noscript>active storage body</noscript>"
        assert result.blocks[0].offers[0].fields == (
            self.factory.published_public_config_snapshot().blocks[0].offers[0].fields[0],
        )
        assert not hasattr(result, "internal_id")

    async def test_get_active_public_config_snapshot_raises_for_unpublished_public_id(
        self,
    ) -> None:
        await self.storage_helper.create_admin_showcase(
            id="showcase-inactive-public-read-storage",
            owner_partner_id="partner-1",
            title="Inactive public read storage showcase",
            public_id="public-inactive-read-storage",
        )
        storage = DatabaseAdminShowcaseStorage(session=self.storage_helper.session)
        await storage.create_published_snapshot(
            showcase_id="showcase-inactive-public-read-storage",
            public_id="public-inactive-read-storage",
            version=1,
            snapshot=self.factory.published_public_config_snapshot_payload(
                public_id="public-inactive-read-storage",
            ),
            created_by_user_id="admin-user-1",
            created_by_partner_id="partner-1",
        )

        with pytest.raises(PublicShowcaseNotFoundError) as error:
            await storage.get_active_public_config_snapshot(
                public_id="public-inactive-read-storage"
            )

        assert error.value.detail == "PUBLIC_SHOWCASE_NOT_FOUND_ERROR"

    async def test_resolves_active_public_config_snapshot_from_route_binding(self) -> None:
        await self.storage_helper.create_admin_showcase(
            id="showcase-resolve-public-read-storage",
            owner_partner_id="partner-1",
            title="Resolve public read storage showcase",
        )
        storage = DatabaseAdminShowcaseStorage(session=self.storage_helper.session)
        snapshot = self.factory.published_public_config_snapshot_payload(
            public_id="public-resolve-read-storage",
            affiliate_id="affiliate-resolve-read-storage",
            text_title="Resolved storage title",
        )
        await storage.create_published_snapshot(
            showcase_id="showcase-resolve-public-read-storage",
            public_id="public-resolve-read-storage",
            version=1,
            snapshot=snapshot,
            created_by_user_id="admin-user-1",
            created_by_partner_id="partner-1",
        )
        await storage.activate_published_snapshot(
            showcase_id="showcase-resolve-public-read-storage",
            public_id="public-resolve-read-storage",
            version=1,
            snapshot=snapshot,
        )
        await storage.create_published_route_binding(
            showcase_id="showcase-resolve-public-read-storage",
            public_id="public-resolve-read-storage",
            host="resolve-storage.example.test",
            path="/loans",
        )

        result = await storage.resolve_active_public_config_snapshot(
            host="resolve-storage.example.test",
            path="/loans",
        )

        assert result.id == "public-resolve-read-storage"
        assert result.affiliate_id == "affiliate-resolve-read-storage"
        assert result.settings.text_title == "Resolved storage title"

    async def test_resolve_active_public_config_snapshot_ignores_inactive_binding(
        self,
    ) -> None:
        await self.storage_helper.create_admin_showcase(
            id="showcase-inactive-resolve-storage",
            owner_partner_id="partner-1",
            title="Inactive resolve storage showcase",
        )
        storage = DatabaseAdminShowcaseStorage(session=self.storage_helper.session)
        snapshot = self.factory.published_public_config_snapshot_payload(
            public_id="public-inactive-resolve-storage",
        )
        await storage.create_published_snapshot(
            showcase_id="showcase-inactive-resolve-storage",
            public_id="public-inactive-resolve-storage",
            version=1,
            snapshot=snapshot,
            created_by_user_id="admin-user-1",
            created_by_partner_id="partner-1",
        )
        await storage.activate_published_snapshot(
            showcase_id="showcase-inactive-resolve-storage",
            public_id="public-inactive-resolve-storage",
            version=1,
            snapshot=snapshot,
        )
        await storage.create_published_route_binding(
            showcase_id="showcase-inactive-resolve-storage",
            public_id="public-inactive-resolve-storage",
            host="inactive-resolve-storage.example.test",
            path="/loans",
        )
        await storage.deactivate_published_route_bindings(
            showcase_id="showcase-inactive-resolve-storage",
            public_id="public-inactive-resolve-storage",
        )

        with pytest.raises(PublicShowcaseNotFoundError) as error:
            await storage.resolve_active_public_config_snapshot(
                host="inactive-resolve-storage.example.test",
                path="/loans",
            )

        assert error.value.detail == "PUBLIC_SHOWCASE_NOT_FOUND_ERROR"

    async def test_reuses_inactive_route_binding_for_same_public_route(self) -> None:
        await self.storage_helper.create_admin_showcase(
            id="showcase-route-binding-reuse-storage",
            owner_partner_id="partner-1",
            title="Route binding reuse storage showcase",
        )
        storage = DatabaseAdminShowcaseStorage(session=self.storage_helper.session)
        created = await storage.create_published_route_binding(
            showcase_id="showcase-route-binding-reuse-storage",
            public_id="public-route-binding-reuse-storage",
            host="reuse-storage.example.test",
            path="/offers",
        )
        await storage.deactivate_published_route_bindings(
            showcase_id="showcase-route-binding-reuse-storage",
            public_id="public-route-binding-reuse-storage",
        )

        reused = await storage.create_published_route_binding(
            showcase_id="showcase-route-binding-reuse-storage",
            public_id="public-route-binding-reuse-storage",
            host="reuse-storage.example.test",
            path="/offers",
        )
        route_bindings = await storage.list_published_route_bindings(
            showcase_id="showcase-route-binding-reuse-storage"
        )

        assert created.active is True
        assert reused.active is True
        assert len(route_bindings) == 1
        assert route_bindings[0].active is True
        assert route_bindings[0].host == "reuse-storage.example.test"
        assert route_bindings[0].path == "/offers"

    async def test_appends_safe_audit_record_without_raw_sensitive_metadata(self) -> None:
        await self.storage_helper.create_admin_showcase(
            id="showcase-audit-storage-1",
            owner_partner_id="partner-1",
            title="Audit storage showcase",
        )
        storage = DatabaseAdminShowcaseStorage(session=self.storage_helper.session)
        metadata: JsonObject = {
            "changed_fields": ["customHeadCode", "customBodyCode"],
            "customHeadCode": "<script>window.rawHead = true</script>",
            "custom_body_code": "<script>window.rawBody = true</script>",
            "published_snapshot": {"id": "public-audit-storage-1"},
            "secret": "secret-value",
            "email": "owner@example.test",
            "nested": {
                "kept": "safe",
                "token": "token-value",
                "password": "password-value",
            },
            "items": [
                {"field": "title", "phone": "+100000000"},
                "safe-list-value",
            ],
        }

        created = await storage.append_showcase_audit_record(
            showcase_id="showcase-audit-storage-1",
            action="custom_code_updated",
            actor_user_id="admin-user-1",
            actor_partner_id="partner-1",
            metadata=metadata,
        )
        persisted = await self.storage_helper.list_showcase_audit_records(
            showcase_id="showcase-audit-storage-1"
        )

        assert created.showcase_id == "showcase-audit-storage-1"
        assert created.action == "custom_code_updated"
        assert created.actor_user_id == "admin-user-1"
        assert created.actor_partner_id == "partner-1"
        assert created.created_at is not None
        assert not hasattr(created, "internal_id")
        assert persisted == [created]
        assert created.metadata == {
            "changed_fields": ["customHeadCode", "customBodyCode"],
            "nested": {"kept": "safe"},
            "items": [
                {"field": "title"},
                "safe-list-value",
            ],
        }
        assert "<script>" not in str(created.metadata)
        assert "secret-value" not in str(created.metadata)
        assert "owner@example.test" not in str(created.metadata)

    async def test_updates_draft_settings_without_changing_published_snapshot(self) -> None:
        published_snapshot: JsonObject = {
            "id": "public-showcase-1",
            "settings": {"design_id": "published", "text_title": "Published title"},
        }
        await self.storage_helper.create_admin_showcase(
            id="showcase-1",
            owner_partner_id="partner-1",
            title="Original showcase",
            draft_settings={
                "design_id": "classic",
                "color_scheme": "light",
                "text_title": "Original draft title",
                "image_banner_mobile": "https://cdn.example.test/mobile.png",
            },
            published_snapshot=published_snapshot,
        )
        storage = DatabaseAdminShowcaseStorage(session=self.storage_helper.session)
        params = AdminShowcaseDraftSettingsPatchParams(
            settings={
                "design_id": "modern",
                "text_title": "Updated draft title",
                "image_banner_mobile": None,
            }
        )

        result = await storage.update_draft_settings(showcase_id="showcase-1", params=params)

        assert result.id == "showcase-1"
        assert result.owner_partner_id == "partner-1"
        assert result.title == "Original showcase"
        assert result.settings == {
            "design_id": "modern",
            "color_scheme": "light",
            "text_title": "Updated draft title",
            "image_banner_mobile": None,
        }
        assert result.published_snapshot == published_snapshot

        persisted = await storage.get_draft_by_id(showcase_id="showcase-1")
        assert persisted == result

    async def test_updates_custom_code_draft_settings_without_changing_publication_rows(
        self,
    ) -> None:
        await self.storage_helper.create_admin_showcase(
            id="showcase-custom-code-storage",
            owner_partner_id="partner-1",
            title="Custom code storage showcase",
            draft_settings={"text_title": "Draft title"},
            published_snapshot={
                "id": "public-custom-code-storage",
                "settings": {"text_title": "Published title"},
            },
        )
        storage = DatabaseAdminShowcaseStorage(session=self.storage_helper.session)
        snapshot = await storage.create_published_snapshot(
            showcase_id="showcase-custom-code-storage",
            public_id="public-custom-code-storage",
            version=1,
            snapshot={
                "id": "public-custom-code-storage",
                "settings": {
                    "text_title": "Published title",
                    "custom_head_code": "<script>window.published = true</script>",
                },
            },
            created_by_user_id="admin-user-1",
            created_by_partner_id="partner-1",
        )
        route_binding = await storage.create_published_route_binding(
            showcase_id="showcase-custom-code-storage",
            public_id="public-custom-code-storage",
            host="offers.example.test",
            path="/custom-code",
        )
        params = AdminShowcaseDraftSettingsPatchParams(
            settings={
                "custom_head_code": "<script>window.draftHead = true</script>",
                "custom_body_code": "<noscript>draft body</noscript>",
            }
        )

        result = await storage.update_draft_settings(
            showcase_id="showcase-custom-code-storage",
            params=params,
        )

        assert result.settings == {
            "text_title": "Draft title",
            "custom_head_code": "<script>window.draftHead = true</script>",
            "custom_body_code": "<noscript>draft body</noscript>",
        }
        assert result.published_snapshot == {
            "id": "public-custom-code-storage",
            "settings": {"text_title": "Published title"},
        }
        snapshots = await storage.list_published_snapshots(
            showcase_id="showcase-custom-code-storage"
        )
        route_bindings = await storage.list_published_route_bindings(
            showcase_id="showcase-custom-code-storage"
        )
        assert snapshots == [snapshot]
        assert route_bindings == [route_binding]

    async def test_empty_draft_settings_patch_returns_unchanged_draft(self) -> None:
        await self.storage_helper.create_admin_showcase(
            id="showcase-settings-storage-empty-patch",
            owner_partner_id="partner-1",
            title="Empty settings patch showcase",
            draft_settings={
                "design_id": "classic",
                "text_title": "Original draft title",
            },
            published_snapshot={"id": "public-settings-storage-empty-patch"},
        )
        storage = DatabaseAdminShowcaseStorage(session=self.storage_helper.session)
        params = AdminShowcaseDraftSettingsPatchParams(settings={})

        result = await storage.update_draft_settings(
            showcase_id="showcase-settings-storage-empty-patch",
            params=params,
        )

        assert result.settings == {
            "design_id": "classic",
            "text_title": "Original draft title",
        }
        assert result.published_snapshot == {"id": "public-settings-storage-empty-patch"}
        persisted = await storage.get_draft_by_id(
            showcase_id="showcase-settings-storage-empty-patch"
        )
        assert persisted == result

    async def test_raises_not_found_when_updating_missing_draft_settings(self) -> None:
        storage = DatabaseAdminShowcaseStorage(session=self.storage_helper.session)
        params = AdminShowcaseDraftSettingsPatchParams(settings={"design_id": "modern"})

        with pytest.raises(AdminShowcaseNotFoundError) as error:
            await storage.update_draft_settings(showcase_id="missing-showcase", params=params)

        assert error.value.detail == "ADMIN_SHOWCASE_NOT_FOUND_ERROR"

    async def test_empty_draft_block_patch_returns_unchanged_block(self) -> None:
        await self.storage_helper.create_admin_showcase(
            id="showcase-blocks-storage-empty-patch",
            owner_partner_id="partner-1",
            title="Empty block patch showcase",
        )
        block = self.factory.admin_showcase_draft_block(
            id="block-storage-empty-patch",
            showcase_id="showcase-blocks-storage-empty-patch",
            type="offers",
            order=10,
            visible=True,
            title="Original block",
            subtitle="Original subtitle",
            desktop_settings={"columns": 3},
            mobile_settings={"columns": 1},
            data={"layout": "cards"},
        )
        await self.storage_helper.create_admin_showcase_draft_block(block=block)
        storage = DatabaseAdminShowcaseStorage(session=self.storage_helper.session)

        result = await storage.patch_draft_block(
            showcase_id="showcase-blocks-storage-empty-patch",
            block_id="block-storage-empty-patch",
            params=AdminShowcaseDraftBlockPatchParams(values={}),
        )

        assert result == block
        persisted_blocks = await storage.list_draft_blocks(
            showcase_id="showcase-blocks-storage-empty-patch"
        )
        assert persisted_blocks == [block]

    async def test_creates_and_lists_draft_blocks_ordered_by_draft_order(self) -> None:
        await self.storage_helper.create_admin_showcase(
            id="showcase-blocks-storage-1",
            owner_partner_id="partner-1",
            title="Block storage showcase",
            published_snapshot={"id": "public-blocks-storage-1"},
        )
        await self.storage_helper.create_admin_showcase_draft_block(
            block=self.factory.admin_showcase_draft_block(
                id="block-storage-existing",
                showcase_id="showcase-blocks-storage-1",
                type="offers",
                order=20,
                visible=True,
                title="Existing offers",
                subtitle="Existing subtitle",
                desktop_settings={"columns": 3},
                mobile_settings={"columns": 1},
                data={"layout": "cards"},
            )
        )
        storage = DatabaseAdminShowcaseStorage(session=self.storage_helper.session)
        params = AdminShowcaseDraftBlockCreateParams(
            type="custom_html",
            order=10,
            visible=False,
            title="Custom block",
            subtitle=None,
            desktop_settings={"width": "full"},
            mobile_settings={"width": "compact"},
            data={"html": "<section>Draft block</section>"},
        )

        created = await storage.create_draft_block(
            showcase_id="showcase-blocks-storage-1",
            block_id="block-storage-created",
            params=params,
        )
        blocks = await storage.list_draft_blocks(showcase_id="showcase-blocks-storage-1")

        assert created.id == "block-storage-created"
        assert created.showcase_id == "showcase-blocks-storage-1"
        assert created.type == "custom_html"
        assert created.order == 10
        assert created.visible is False
        assert created.title == "Custom block"
        assert created.subtitle is None
        assert created.desktop_settings == {"width": "full"}
        assert created.mobile_settings == {"width": "compact"}
        assert created.data == {"html": "<section>Draft block</section>"}
        assert [block.id for block in blocks] == [
            "block-storage-created",
            "block-storage-existing",
        ]

    async def test_patches_and_deletes_draft_block_without_changing_related_state(self) -> None:
        published_snapshot: JsonObject = {
            "id": "public-blocks-storage-patch",
            "blocks": [{"type": "offers", "title": "Published offers"}],
        }
        await self.storage_helper.create_admin_showcase(
            id="showcase-blocks-storage-patch",
            owner_partner_id="partner-1",
            title="Block patch showcase",
            published_snapshot=published_snapshot,
        )
        await self.storage_helper.create_admin_showcase_draft_block(
            block=self.factory.admin_showcase_draft_block(
                id="block-storage-patch-target",
                showcase_id="showcase-blocks-storage-patch",
                type="custom_html",
                order=10,
                visible=True,
                title="Original custom block",
                subtitle="Original subtitle",
                desktop_settings={"width": "narrow"},
                mobile_settings={"width": "compact"},
                data={"html": "<section>Original</section>"},
            )
        )
        await self.storage_helper.create_admin_showcase_draft_block(
            block=self.factory.admin_showcase_draft_block(
                id="block-storage-delete-target",
                showcase_id="showcase-blocks-storage-patch",
                type="offers",
                order=20,
                visible=True,
                title="Delete me",
                subtitle="Delete subtitle",
                desktop_settings={"columns": 3},
                mobile_settings={"columns": 1},
                data={"layout": "cards"},
            )
        )
        await self.storage_helper.create_admin_showcase_draft_offer(
            offer=self.factory.admin_showcase_draft_offer(
                id="offer-storage-preserved",
                showcase_id="showcase-blocks-storage-patch",
                block_id="block-storage-delete-target",
                manual_order=1,
                data={"source": "manual"},
            )
        )
        storage = DatabaseAdminShowcaseStorage(session=self.storage_helper.session)
        params = AdminShowcaseDraftBlockPatchParams(
            values={
                "order": 30,
                "visible": False,
                "title": "Updated custom block",
                "subtitle": None,
                "desktop_settings": {"width": "full", "theme": "dark"},
                "mobile_settings": {"width": "stacked"},
                "data": {"html": "<script>window.ownerDraftOnly = true</script>"},
            }
        )

        patched = await storage.patch_draft_block(
            showcase_id="showcase-blocks-storage-patch",
            block_id="block-storage-patch-target",
            params=params,
        )
        await storage.delete_draft_block(
            showcase_id="showcase-blocks-storage-patch",
            block_id="block-storage-delete-target",
        )

        assert patched.id == "block-storage-patch-target"
        assert patched.showcase_id == "showcase-blocks-storage-patch"
        assert patched.type == "custom_html"
        assert patched.order == 30
        assert patched.visible is False
        assert patched.title == "Updated custom block"
        assert patched.subtitle is None
        assert patched.desktop_settings == {"width": "full", "theme": "dark"}
        assert patched.mobile_settings == {"width": "stacked"}
        assert patched.data == {"html": "<script>window.ownerDraftOnly = true</script>"}

        blocks = await storage.list_draft_blocks(showcase_id="showcase-blocks-storage-patch")
        assert [block.id for block in blocks] == ["block-storage-patch-target"]
        persisted = await storage.get_draft_by_id(showcase_id="showcase-blocks-storage-patch")
        assert persisted.published_snapshot == published_snapshot
        offers = await self.storage_helper.list_admin_showcase_draft_offers(
            showcase_id="showcase-blocks-storage-patch"
        )
        assert [offer.id for offer in offers] == ["offer-storage-preserved"]

    async def test_raises_not_found_when_patching_or_deleting_missing_draft_block(self) -> None:
        await self.storage_helper.create_admin_showcase(
            id="showcase-blocks-storage-missing-block",
            owner_partner_id="partner-1",
            title="Missing block showcase",
        )
        storage = DatabaseAdminShowcaseStorage(session=self.storage_helper.session)
        params = AdminShowcaseDraftBlockPatchParams(values={"visible": False})

        with pytest.raises(AdminShowcaseDraftBlockNotFoundError) as patch_error:
            await storage.patch_draft_block(
                showcase_id="showcase-blocks-storage-missing-block",
                block_id="missing-block",
                params=params,
            )

        with pytest.raises(AdminShowcaseDraftBlockNotFoundError) as delete_error:
            await storage.delete_draft_block(
                showcase_id="showcase-blocks-storage-missing-block",
                block_id="missing-block",
            )

        assert patch_error.value.detail == "ADMIN_SHOWCASE_DRAFT_BLOCK_NOT_FOUND_ERROR"
        assert delete_error.value.detail == "ADMIN_SHOWCASE_DRAFT_BLOCK_NOT_FOUND_ERROR"

    async def test_creates_unassigned_offer_and_clears_block_assignment(self) -> None:
        await self.storage_helper.create_admin_showcase(
            id="showcase-offers-storage-null-block",
            owner_partner_id="partner-1",
            title="Nullable block offer showcase",
        )
        await self.storage_helper.create_admin_showcase_draft_offer(
            offer=self.factory.admin_showcase_draft_offer(
                id="offer-storage-null-block-target",
                showcase_id="showcase-offers-storage-null-block",
                block_id="block-storage-original",
            )
        )
        storage = DatabaseAdminShowcaseStorage(session=self.storage_helper.session)

        created = await storage.create_draft_offer(
            showcase_id="showcase-offers-storage-null-block",
            offer_id="offer-storage-null-block-created",
            params=self.factory.admin_showcase_draft_offer_create_params(block_id=None),
        )
        patched = await storage.patch_draft_offer(
            showcase_id="showcase-offers-storage-null-block",
            offer_id="offer-storage-null-block-target",
            params=AdminShowcaseDraftOfferPatchParams(values={"block_id": None}),
        )

        assert created.block_id is None
        assert patched.block_id is None
        offers = await storage.list_draft_offers(showcase_id="showcase-offers-storage-null-block")
        offers_by_id = {offer.id: offer for offer in offers}
        assert offers_by_id["offer-storage-null-block-created"].block_id is None
        assert offers_by_id["offer-storage-null-block-target"].block_id is None

    async def test_empty_draft_offer_patch_returns_unchanged_offer(self) -> None:
        await self.storage_helper.create_admin_showcase(
            id="showcase-offers-storage-empty-patch",
            owner_partner_id="partner-1",
            title="Empty offer patch showcase",
        )
        offer = self.factory.admin_showcase_draft_offer(
            id="offer-storage-empty-patch",
            showcase_id="showcase-offers-storage-empty-patch",
            block_id=None,
            enabled=False,
            manual_order=10,
            fields=[{"key": "rate", "value": "12%", "visible": False}],
        )
        await self.storage_helper.create_admin_showcase_draft_offer(offer=offer)
        storage = DatabaseAdminShowcaseStorage(session=self.storage_helper.session)

        result = await storage.patch_draft_offer(
            showcase_id="showcase-offers-storage-empty-patch",
            offer_id="offer-storage-empty-patch",
            params=AdminShowcaseDraftOfferPatchParams(values={}),
        )

        assert result == offer
        persisted_offers = await storage.list_draft_offers(
            showcase_id="showcase-offers-storage-empty-patch"
        )
        assert persisted_offers == [offer]

    async def test_creates_and_lists_draft_offers_ordered_by_block_and_manual_order(self) -> None:
        await self.storage_helper.create_admin_showcase(
            id="showcase-offers-storage-1",
            owner_partner_id="partner-1",
            title="Offer storage showcase",
            published_snapshot={"id": "public-offers-storage-1"},
        )
        await self.storage_helper.create_admin_showcase_draft_offer(
            offer=self.factory.admin_showcase_draft_offer(
                id="offer-storage-existing",
                showcase_id="showcase-offers-storage-1",
                block_id="block-storage-offers-b",
                enabled=False,
                manual_order=20,
                fields=[{"key": "rate", "value": "12%", "visible": False}],
                categories=["loans"],
                display_name="Existing disabled offer",
            )
        )
        storage = DatabaseAdminShowcaseStorage(session=self.storage_helper.session)
        params = AdminShowcaseDraftOfferCreateParams(
            block_id="block-storage-offers-a",
            enabled=True,
            manual_order=10,
            cta_text="Apply now",
            usp_text="Decision in 5 minutes",
            fields=[
                {"key": "amount", "value": "100000", "visible": True},
                {"key": "internal_score", "value": "A", "visible": False},
            ],
            categories=["cash", "cards"],
            logo_url="https://cdn.example.test/new-logo.png",
            rounded_logo_url="https://cdn.example.test/new-rounded.png",
            display_name="New storage offer",
            site_name="New Bank",
            cpa_url="https://cpa.example.test/new",
            legal_entity="New Bank LLC",
            inn="1234567890",
            erid="erid-new",
            data={"source": "manual", "rating": 5},
        )

        created = await storage.create_draft_offer(
            showcase_id="showcase-offers-storage-1",
            offer_id="offer-storage-created",
            params=params,
        )
        offers = await storage.list_draft_offers(showcase_id="showcase-offers-storage-1")

        assert created.id == "offer-storage-created"
        assert created.showcase_id == "showcase-offers-storage-1"
        assert created.block_id == "block-storage-offers-a"
        assert created.enabled is True
        assert created.manual_order == 10
        assert created.cta_text == "Apply now"
        assert created.usp_text == "Decision in 5 minutes"
        assert created.fields == [
            {"key": "amount", "value": "100000", "visible": True},
            {"key": "internal_score", "value": "A", "visible": False},
        ]
        assert created.categories == ["cash", "cards"]
        assert created.logo_url == "https://cdn.example.test/new-logo.png"
        assert created.rounded_logo_url == "https://cdn.example.test/new-rounded.png"
        assert created.display_name == "New storage offer"
        assert created.site_name == "New Bank"
        assert created.cpa_url == "https://cpa.example.test/new"
        assert created.legal_entity == "New Bank LLC"
        assert created.inn == "1234567890"
        assert created.erid == "erid-new"
        assert created.data == {"source": "manual", "rating": 5}
        assert [offer.id for offer in offers] == [
            "offer-storage-created",
            "offer-storage-existing",
        ]

    async def test_patches_and_deletes_draft_offer_without_changing_related_state(self) -> None:
        published_snapshot: JsonObject = {
            "id": "public-offers-storage-patch",
            "blocks": [{"type": "offers", "offers": [{"id": "published-offer"}]}],
        }
        await self.storage_helper.create_admin_showcase(
            id="showcase-offers-storage-patch",
            owner_partner_id="partner-1",
            title="Offer patch showcase",
            published_snapshot=published_snapshot,
        )
        await self.storage_helper.create_admin_showcase_draft_block(
            block=self.factory.admin_showcase_draft_block(
                id="block-storage-offers-preserved",
                showcase_id="showcase-offers-storage-patch",
                order=10,
                data={"layout": "cards"},
            )
        )
        await self.storage_helper.create_admin_showcase_draft_offer(
            offer=self.factory.admin_showcase_draft_offer(
                id="offer-storage-patch-target",
                showcase_id="showcase-offers-storage-patch",
                block_id="block-storage-offers-original",
                enabled=True,
                manual_order=20,
                cta_text="Original CTA",
                usp_text="Original USP",
                fields=[{"key": "rate", "value": "12%", "visible": True}],
                categories=["loans"],
                display_name="Original offer",
                data={"source": "manual"},
            )
        )
        await self.storage_helper.create_admin_showcase_draft_offer(
            offer=self.factory.admin_showcase_draft_offer(
                id="offer-storage-delete-target",
                showcase_id="showcase-offers-storage-patch",
                block_id="block-storage-offers-preserved",
                manual_order=30,
                display_name="Delete me",
            )
        )
        storage = DatabaseAdminShowcaseStorage(session=self.storage_helper.session)
        params = AdminShowcaseDraftOfferPatchParams(
            values={
                "block_id": "block-storage-offers-preserved",
                "enabled": False,
                "manual_order": 5,
                "cta_text": None,
                "usp_text": "Updated USP",
                "fields": [{"key": "internal_score", "value": "A", "visible": False}],
                "categories": ["cash"],
                "logo_url": "https://cdn.example.test/updated-logo.png",
                "rounded_logo_url": None,
                "display_name": "Updated storage offer",
                "site_name": "Updated Bank",
                "cpa_url": "https://cpa.example.test/updated",
                "legal_entity": "Updated Bank LLC",
                "inn": "2222222222",
                "erid": "erid-updated",
                "data": {"source": "manual", "tier": "draft"},
            }
        )

        patched = await storage.patch_draft_offer(
            showcase_id="showcase-offers-storage-patch",
            offer_id="offer-storage-patch-target",
            params=params,
        )
        await storage.delete_draft_offer(
            showcase_id="showcase-offers-storage-patch",
            offer_id="offer-storage-delete-target",
        )

        assert patched.id == "offer-storage-patch-target"
        assert patched.showcase_id == "showcase-offers-storage-patch"
        assert patched.block_id == "block-storage-offers-preserved"
        assert patched.enabled is False
        assert patched.manual_order == 5
        assert patched.cta_text is None
        assert patched.usp_text == "Updated USP"
        assert patched.fields == [{"key": "internal_score", "value": "A", "visible": False}]
        assert patched.categories == ["cash"]
        assert patched.logo_url == "https://cdn.example.test/updated-logo.png"
        assert patched.rounded_logo_url is None
        assert patched.display_name == "Updated storage offer"
        assert patched.site_name == "Updated Bank"
        assert patched.cpa_url == "https://cpa.example.test/updated"
        assert patched.legal_entity == "Updated Bank LLC"
        assert patched.inn == "2222222222"
        assert patched.erid == "erid-updated"
        assert patched.data == {"source": "manual", "tier": "draft"}

        offers = await storage.list_draft_offers(showcase_id="showcase-offers-storage-patch")
        assert [offer.id for offer in offers] == ["offer-storage-patch-target"]
        blocks = await self.storage_helper.list_admin_showcase_draft_blocks(
            showcase_id="showcase-offers-storage-patch"
        )
        assert [block.id for block in blocks] == ["block-storage-offers-preserved"]
        persisted = await storage.get_draft_by_id(showcase_id="showcase-offers-storage-patch")
        assert persisted.published_snapshot == published_snapshot

    async def test_raises_not_found_when_patching_or_deleting_missing_draft_offer(self) -> None:
        await self.storage_helper.create_admin_showcase(
            id="showcase-offers-storage-missing-offer",
            owner_partner_id="partner-1",
            title="Missing offer showcase",
        )
        storage = DatabaseAdminShowcaseStorage(session=self.storage_helper.session)
        params = AdminShowcaseDraftOfferPatchParams(values={"enabled": False})

        with pytest.raises(AdminShowcaseDraftOfferNotFoundError) as patch_error:
            await storage.patch_draft_offer(
                showcase_id="showcase-offers-storage-missing-offer",
                offer_id="missing-offer",
                params=params,
            )

        with pytest.raises(AdminShowcaseDraftOfferNotFoundError) as delete_error:
            await storage.delete_draft_offer(
                showcase_id="showcase-offers-storage-missing-offer",
                offer_id="missing-offer",
            )

        assert patch_error.value.detail == "ADMIN_SHOWCASE_DRAFT_OFFER_NOT_FOUND_ERROR"
        assert delete_error.value.detail == "ADMIN_SHOWCASE_DRAFT_OFFER_NOT_FOUND_ERROR"

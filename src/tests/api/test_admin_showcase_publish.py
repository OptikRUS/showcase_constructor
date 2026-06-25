from __future__ import annotations

from typing import TYPE_CHECKING, cast

import pytest
from httpx2 import codes

from src.storages.showcases import DatabaseAdminShowcaseStorage
from src.tests.fixtures import APIFixture, FactoryFixture, StorageFixture

if TYPE_CHECKING:
    from src.core.showcases.schemas import JsonObject


def _as_json_object(value: object) -> JsonObject:
    return cast("JsonObject", value)


class TestAdminShowcasePublishAPI(APIFixture, FactoryFixture, StorageFixture):
    async def test_publish_creates_active_snapshot_and_audit_record(self) -> None:
        await self.storage_helper.create_admin_showcase(
            id="showcase-publish-api",
            owner_partner_id="partner-1",
            title="Publish API showcase",
            draft_settings={
                "affiliate_id": "affiliate-publish-api",
                "type": "showcase",
                "tracking_domain": "publish.example.test",
                "text_title": "Draft publish title",
                "text_subtitle": "Draft publish subtitle",
                "custom_head_code": "<script>window.publishHead = true</script>",
                "custom_body_code": "<noscript>publish body pixel</noscript>",
            },
            published_snapshot={
                "id": "old-public-publish-api",
                "settings": {"text_title": "Old published title"},
            },
        )
        await self.storage_helper.create_admin_showcase_draft_block(
            block=self.factory.admin_showcase_draft_block(
                id="block-publish-api-visible",
                showcase_id="showcase-publish-api",
                visible=True,
                title="Published offers",
            )
        )
        await self.storage_helper.create_admin_showcase_draft_block(
            block=self.factory.admin_showcase_draft_block(
                id="block-publish-api-hidden",
                showcase_id="showcase-publish-api",
                visible=False,
                title="Hidden offers",
            )
        )
        await self.storage_helper.create_admin_showcase_draft_offer(
            offer=self.factory.admin_showcase_draft_offer(
                id="offer-publish-api-enabled",
                showcase_id="showcase-publish-api",
                block_id="block-publish-api-visible",
                enabled=True,
                fields=[
                    {"key": "amount", "value": "100000", "visible": True},
                    {"key": "internal_score", "value": "A", "visible": False},
                ],
                categories=["cash"],
                display_name="Published offer",
            )
        )
        await self.storage_helper.create_admin_showcase_draft_offer(
            offer=self.factory.admin_showcase_draft_offer(
                id="offer-publish-api-disabled",
                showcase_id="showcase-publish-api",
                block_id="block-publish-api-visible",
                enabled=False,
                display_name="Disabled offer",
            )
        )
        await self.storage_helper.commit()

        response = self.api.publish_admin_showcase(showcase_id="showcase-publish-api")

        assert response.status_code == codes.OK
        payload = response.json()
        assert payload["id"] == "showcase-publish-api"
        assert payload["publicId"]
        assert payload["version"] == 1
        assert payload["published"] is True

        public_id = payload["publicId"]
        state = await self.storage_helper.get_admin_showcase_publication_state(
            showcase_id="showcase-publish-api"
        )
        snapshots = await self.storage_helper.list_published_showcase_snapshots(
            showcase_id="showcase-publish-api"
        )
        audit_records = await self.storage_helper.list_showcase_audit_records(
            showcase_id="showcase-publish-api"
        )

        assert state.public_id == public_id
        assert state.version == 1
        assert state.active is True
        assert len(snapshots) == 1
        snapshot = snapshots[0]
        assert snapshot.public_id == public_id
        assert snapshot.version == 1
        assert snapshot.created_by_user_id == "admin-user-1"
        assert snapshot.created_by_partner_id == "partner-1"
        assert snapshot.snapshot["id"] == public_id
        assert snapshot.snapshot["affiliate_id"] == "affiliate-publish-api"
        snapshot_settings = _as_json_object(snapshot.snapshot["settings"])
        assert snapshot_settings["text_title"] == "Draft publish title"
        assert snapshot.snapshot["custom_head_code"] == (
            "<script>window.publishHead = true</script>"
        )
        assert snapshot.snapshot["custom_body_code"] == "<noscript>publish body pixel</noscript>"
        assert snapshot.snapshot["blocks"] == [
            {
                "type": "offers",
                "title": "Published offers",
                "offers": [
                    {
                        "id": "offer-publish-api-enabled",
                        "offer_categories": ["cash"],
                        "logo_url": "https://cdn.example.test/logo.png",
                        "rounded_logo_url": "https://cdn.example.test/logo-rounded.png",
                        "name": "Published offer",
                        "site_name": "Example Bank",
                        "url": "https://cpa.example.test/click",
                        "fields": [
                            {"key": "amount", "value": "100000", "visible": True},
                        ],
                    }
                ],
            }
        ]
        assert state.snapshot == snapshot.snapshot
        assert len(audit_records) == 1
        assert audit_records[0].action == "showcase_published"
        assert audit_records[0].actor_user_id == "admin-user-1"
        assert audit_records[0].actor_partner_id == "partner-1"
        assert audit_records[0].metadata == {
            "public_id": public_id,
            "version": 1,
        }
        assert "publishHead" not in str(audit_records[0].metadata)
        assert "publish body pixel" not in str(audit_records[0].metadata)

    async def test_republish_reuses_public_id_and_preserves_snapshot_history(self) -> None:
        await self.storage_helper.create_admin_showcase(
            id="showcase-republish-api",
            owner_partner_id="partner-1",
            title="Republish API showcase",
            draft_settings={
                "affiliate_id": "affiliate-republish-api",
                "type": "showcase",
                "text_title": "First published title",
            },
        )
        await self.storage_helper.create_admin_showcase_draft_block(
            block=self.factory.admin_showcase_draft_block(
                id="block-republish-api",
                showcase_id="showcase-republish-api",
                title="Republish offers",
            )
        )
        await self.storage_helper.create_admin_showcase_draft_offer(
            offer=self.factory.admin_showcase_draft_offer(
                id="offer-republish-api",
                showcase_id="showcase-republish-api",
                block_id="block-republish-api",
                enabled=True,
            )
        )
        await self.storage_helper.commit()

        first_response = self.api.publish_admin_showcase(showcase_id="showcase-republish-api")
        patch_response = self.api.patch_admin_showcase_draft_settings(
            showcase_id="showcase-republish-api",
            json={"textTitle": "Second published title"},
        )
        second_response = self.api.publish_admin_showcase(showcase_id="showcase-republish-api")

        assert first_response.status_code == codes.OK
        assert patch_response.status_code == codes.OK
        assert second_response.status_code == codes.OK
        first_payload = first_response.json()
        second_payload = second_response.json()
        assert second_payload["publicId"] == first_payload["publicId"]
        assert second_payload["version"] == 2

        state = await self.storage_helper.get_admin_showcase_publication_state(
            showcase_id="showcase-republish-api"
        )
        snapshots = await self.storage_helper.list_published_showcase_snapshots(
            showcase_id="showcase-republish-api"
        )

        assert state.public_id == first_payload["publicId"]
        assert state.version == 2
        state_snapshot = _as_json_object(state.snapshot)
        state_settings = _as_json_object(state_snapshot["settings"])
        assert state_settings["text_title"] == "Second published title"
        assert [snapshot.version for snapshot in snapshots] == [1, 2]
        first_snapshot_settings = _as_json_object(snapshots[0].snapshot["settings"])
        second_snapshot_settings = _as_json_object(snapshots[1].snapshot["settings"])
        assert first_snapshot_settings["text_title"] == "First published title"
        assert second_snapshot_settings["text_title"] == "Second published title"

    async def test_publish_validation_failure_preserves_old_visibility(self) -> None:
        await self.storage_helper.create_admin_showcase(
            id="showcase-publish-validation-api",
            owner_partner_id="partner-1",
            title="Validation API showcase",
            draft_settings={
                "affiliate_id": "affiliate-publish-validation-api",
                "type": "showcase",
                "text_title": "Valid first title",
            },
        )
        await self.storage_helper.create_admin_showcase_draft_block(
            block=self.factory.admin_showcase_draft_block(
                id="block-publish-validation-api",
                showcase_id="showcase-publish-validation-api",
                title="Validation offers",
            )
        )
        await self.storage_helper.create_admin_showcase_draft_offer(
            offer=self.factory.admin_showcase_draft_offer(
                id="offer-publish-validation-api",
                showcase_id="showcase-publish-validation-api",
                block_id="block-publish-validation-api",
                enabled=True,
            )
        )
        await self.storage_helper.commit()
        first_response = self.api.publish_admin_showcase(
            showcase_id="showcase-publish-validation-api"
        )
        patch_offer_response = self.api.patch_admin_showcase_offer(
            showcase_id="showcase-publish-validation-api",
            offer_id="offer-publish-validation-api",
            json={"enabled": False},
        )

        response = self.api.publish_admin_showcase(showcase_id="showcase-publish-validation-api")

        assert first_response.status_code == codes.OK
        assert patch_offer_response.status_code == codes.OK
        assert response.status_code == codes.UNPROCESSABLE_ENTITY
        assert response.json() == {
            "detail": "ADMIN_SHOWCASE_PUBLICATION_REQUIRES_AVAILABLE_OFFER_OR_FALLBACK"
        }
        state = await self.storage_helper.get_admin_showcase_publication_state(
            showcase_id="showcase-publish-validation-api"
        )
        snapshots = await self.storage_helper.list_published_showcase_snapshots(
            showcase_id="showcase-publish-validation-api"
        )
        audit_records = await self.storage_helper.list_showcase_audit_records(
            showcase_id="showcase-publish-validation-api"
        )
        assert state.active is True
        assert state.version == 1
        assert len(snapshots) == 1
        assert [record.action for record in audit_records] == ["showcase_published"]

    async def test_publish_audit_failure_rolls_back_new_visibility(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        await self.storage_helper.create_admin_showcase(
            id="showcase-publish-audit-failure-api",
            owner_partner_id="partner-1",
            title="Publish audit failure showcase",
            draft_settings={
                "affiliate_id": "affiliate-publish-audit-failure-api",
                "type": "showcase",
                "text_title": "First audit title",
            },
        )
        await self.storage_helper.create_admin_showcase_draft_block(
            block=self.factory.admin_showcase_draft_block(
                id="block-publish-audit-failure-api",
                showcase_id="showcase-publish-audit-failure-api",
                title="Audit failure offers",
            )
        )
        await self.storage_helper.create_admin_showcase_draft_offer(
            offer=self.factory.admin_showcase_draft_offer(
                id="offer-publish-audit-failure-api",
                showcase_id="showcase-publish-audit-failure-api",
                block_id="block-publish-audit-failure-api",
                enabled=True,
            )
        )
        await self.storage_helper.commit()
        first_response = self.api.publish_admin_showcase(
            showcase_id="showcase-publish-audit-failure-api"
        )
        patch_response = self.api.patch_admin_showcase_draft_settings(
            showcase_id="showcase-publish-audit-failure-api",
            json={"textTitle": "Rolled back title"},
        )

        async def fail_append_showcase_audit_record(
            self: DatabaseAdminShowcaseStorage,
            **kwargs: object,
        ) -> object:
            _ = self, kwargs
            message = "audit append failed"
            raise RuntimeError(message)

        monkeypatch.setattr(
            DatabaseAdminShowcaseStorage,
            "append_showcase_audit_record",
            fail_append_showcase_audit_record,
        )
        with pytest.raises(RuntimeError, match="audit append failed"):
            self.api.publish_admin_showcase(showcase_id="showcase-publish-audit-failure-api")

        assert first_response.status_code == codes.OK
        assert patch_response.status_code == codes.OK
        state = await self.storage_helper.get_admin_showcase_publication_state(
            showcase_id="showcase-publish-audit-failure-api"
        )
        snapshots = await self.storage_helper.list_published_showcase_snapshots(
            showcase_id="showcase-publish-audit-failure-api"
        )
        audit_records = await self.storage_helper.list_showcase_audit_records(
            showcase_id="showcase-publish-audit-failure-api"
        )
        assert state.version == 1
        state_snapshot = _as_json_object(state.snapshot)
        state_settings = _as_json_object(state_snapshot["settings"])
        assert state_settings["text_title"] == "First audit title"
        assert [snapshot.version for snapshot in snapshots] == [1]
        assert [record.action for record in audit_records] == ["showcase_published"]

    async def test_forbids_foreign_owner_publish_without_mutation(self) -> None:
        await self.storage_helper.create_admin_showcase(
            id="showcase-publish-foreign-api",
            owner_partner_id="partner-2",
            title="Foreign publish showcase",
            draft_settings={
                "affiliate_id": "affiliate-publish-foreign-api",
                "type": "showcase",
                "fallback_text": "Fallback only",
            },
        )
        await self.storage_helper.commit()

        response = self.api.publish_admin_showcase(showcase_id="showcase-publish-foreign-api")

        assert response.status_code == codes.FORBIDDEN
        assert response.json() == {"detail": "SHOWCASE_ACCESS_DENIED_ERROR"}
        state = await self.storage_helper.get_admin_showcase_publication_state(
            showcase_id="showcase-publish-foreign-api"
        )
        audit_records = await self.storage_helper.list_showcase_audit_records(
            showcase_id="showcase-publish-foreign-api"
        )
        assert state.public_id is None
        assert state.active is False
        assert audit_records == []

    def test_returns_not_found_for_missing_publish_showcase(self) -> None:
        response = self.api.publish_admin_showcase(showcase_id="missing-showcase")

        assert response.status_code == codes.NOT_FOUND
        assert response.json() == {"detail": "ADMIN_SHOWCASE_NOT_FOUND_ERROR"}


class TestAdminShowcaseUnpublishAPI(APIFixture, FactoryFixture, StorageFixture):
    async def test_unpublish_removes_active_visibility_and_preserves_history(self) -> None:
        await self.storage_helper.create_admin_showcase(
            id="showcase-unpublish-api",
            owner_partner_id="partner-1",
            title="Unpublish API showcase",
            draft_settings={
                "affiliate_id": "affiliate-unpublish-api",
                "type": "showcase",
                "text_title": "Unpublish title",
                "custom_head_code": "<script>window.unpublishHead = true</script>",
            },
        )
        await self.storage_helper.create_admin_showcase_draft_block(
            block=self.factory.admin_showcase_draft_block(
                id="block-unpublish-api",
                showcase_id="showcase-unpublish-api",
                title="Unpublish offers",
            )
        )
        await self.storage_helper.create_admin_showcase_draft_offer(
            offer=self.factory.admin_showcase_draft_offer(
                id="offer-unpublish-api",
                showcase_id="showcase-unpublish-api",
                block_id="block-unpublish-api",
                enabled=True,
            )
        )
        await self.storage_helper.commit()
        publish_response = self.api.publish_admin_showcase(showcase_id="showcase-unpublish-api")
        public_id = publish_response.json()["publicId"]
        route_binding = await self.storage_helper.create_published_route_binding(
            showcase_id="showcase-unpublish-api",
            public_id=public_id,
            host="unpublish.example.test",
            path="/offers",
        )
        await self.storage_helper.commit()

        response = self.api.unpublish_admin_showcase(showcase_id="showcase-unpublish-api")

        assert publish_response.status_code == codes.OK
        assert route_binding.active is True
        assert response.status_code == codes.OK
        assert response.json() == {
            "id": "showcase-unpublish-api",
            "publicId": public_id,
            "version": 2,
            "published": False,
        }
        state = await self.storage_helper.get_admin_showcase_publication_state(
            showcase_id="showcase-unpublish-api"
        )
        snapshots = await self.storage_helper.list_published_showcase_snapshots(
            showcase_id="showcase-unpublish-api"
        )
        route_bindings = await self.storage_helper.list_published_route_bindings(
            showcase_id="showcase-unpublish-api"
        )
        audit_records = await self.storage_helper.list_showcase_audit_records(
            showcase_id="showcase-unpublish-api"
        )
        assert state.public_id == public_id
        assert state.version == 2
        assert state.active is False
        assert state.snapshot is None
        assert len(snapshots) == 1
        assert route_bindings[0].active is False
        assert [record.action for record in audit_records] == [
            "showcase_published",
            "showcase_unpublished",
        ]
        assert audit_records[-1].metadata == {
            "public_id": public_id,
            "version": 2,
        }
        assert "unpublishHead" not in str(audit_records[-1].metadata)

    async def test_forbids_foreign_owner_unpublish_without_mutation(self) -> None:
        old_snapshot: JsonObject = {
            "id": "public-unpublish-foreign-api",
            "settings": {"text_title": "Foreign active title"},
        }
        await self.storage_helper.create_admin_showcase(
            id="showcase-unpublish-foreign-api",
            owner_partner_id="partner-2",
            title="Foreign unpublish showcase",
        )
        await self.storage_helper.create_active_published_showcase_snapshot(
            showcase_id="showcase-unpublish-foreign-api",
            public_id="public-unpublish-foreign-api",
            version=1,
            snapshot=old_snapshot,
        )
        await self.storage_helper.commit()

        response = self.api.unpublish_admin_showcase(
            showcase_id="showcase-unpublish-foreign-api"
        )

        assert response.status_code == codes.FORBIDDEN
        assert response.json() == {"detail": "SHOWCASE_ACCESS_DENIED_ERROR"}
        state = await self.storage_helper.get_admin_showcase_publication_state(
            showcase_id="showcase-unpublish-foreign-api"
        )
        audit_records = await self.storage_helper.list_showcase_audit_records(
            showcase_id="showcase-unpublish-foreign-api"
        )
        assert state.public_id == "public-unpublish-foreign-api"
        assert state.version == 1
        assert state.active is True
        assert state.snapshot == old_snapshot
        assert audit_records == []

    def test_returns_not_found_for_missing_unpublish_showcase(self) -> None:
        response = self.api.unpublish_admin_showcase(showcase_id="missing-showcase")

        assert response.status_code == codes.NOT_FOUND
        assert response.json() == {"detail": "ADMIN_SHOWCASE_NOT_FOUND_ERROR"}


class TestAdminShowcasePublishNoAuthAPI(APIFixture, FactoryFixture, StorageFixture):
    async def test_requires_authentication_for_publish_without_mutation(self) -> None:
        await self.storage_helper.create_admin_showcase(
            id="showcase-publish-no-auth-api",
            owner_partner_id="partner-1",
            title="No auth publish showcase",
            draft_settings={
                "affiliate_id": "affiliate-publish-no-auth-api",
                "type": "showcase",
                "fallback_text": "Fallback only",
            },
        )
        await self.storage_helper.commit()

        response = self.no_auth_api.publish_admin_showcase(
            showcase_id="showcase-publish-no-auth-api"
        )

        assert response.status_code == codes.UNAUTHORIZED
        assert response.json() == {"detail": "ADMIN_AUTHENTICATION_REQUIRED_ERROR"}
        state = await self.storage_helper.get_admin_showcase_publication_state(
            showcase_id="showcase-publish-no-auth-api"
        )
        audit_records = await self.storage_helper.list_showcase_audit_records(
            showcase_id="showcase-publish-no-auth-api"
        )
        assert state.public_id is None
        assert state.active is False
        assert audit_records == []

    async def test_requires_authentication_for_unpublish_without_mutation(self) -> None:
        old_snapshot: JsonObject = {
            "id": "public-unpublish-no-auth-api",
            "settings": {"text_title": "No auth active title"},
        }
        await self.storage_helper.create_admin_showcase(
            id="showcase-unpublish-no-auth-api",
            owner_partner_id="partner-1",
            title="No auth unpublish showcase",
        )
        await self.storage_helper.create_active_published_showcase_snapshot(
            showcase_id="showcase-unpublish-no-auth-api",
            public_id="public-unpublish-no-auth-api",
            version=1,
            snapshot=old_snapshot,
        )
        await self.storage_helper.commit()

        response = self.no_auth_api.unpublish_admin_showcase(
            showcase_id="showcase-unpublish-no-auth-api"
        )

        assert response.status_code == codes.UNAUTHORIZED
        assert response.json() == {"detail": "ADMIN_AUTHENTICATION_REQUIRED_ERROR"}
        state = await self.storage_helper.get_admin_showcase_publication_state(
            showcase_id="showcase-unpublish-no-auth-api"
        )
        audit_records = await self.storage_helper.list_showcase_audit_records(
            showcase_id="showcase-unpublish-no-auth-api"
        )
        assert state.public_id == "public-unpublish-no-auth-api"
        assert state.version == 1
        assert state.active is True
        assert state.snapshot == old_snapshot
        assert audit_records == []

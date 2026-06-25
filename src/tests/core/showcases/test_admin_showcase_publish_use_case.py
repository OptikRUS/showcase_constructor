from typing import TYPE_CHECKING, cast
from unittest.mock import AsyncMock

import pytest

from src.core.admin_auth.schemas import AdminActorContext
from src.core.showcases.cache import PublicShowcaseCacheInvalidator
from src.core.showcases.exceptions import (
    AdminShowcaseNotFoundError,
    AdminShowcasePublicationValidationError,
    ShowcaseAccessDeniedError,
)
from src.core.showcases.use_cases import (
    PublishAdminShowcaseUseCase,
    UnpublishAdminShowcaseUseCase,
)
from src.core.storages import AdminShowcaseStorage
from src.tests.fixtures import FactoryFixture

if TYPE_CHECKING:
    from src.core.showcases.schemas import JsonObject


class TestPublishAdminShowcaseUseCase(FactoryFixture):
    async def test_publishes_draft_snapshot_with_audit_and_cache_invalidation(self) -> None:
        storage = AsyncMock(spec=AdminShowcaseStorage)
        cache_invalidator = AsyncMock(spec=PublicShowcaseCacheInvalidator)
        storage.get_by_id.return_value = self.factory.admin_showcase(
            id="showcase-publish-core",
            owner_partner_id="partner-1",
            public_id="public-publish-core",
            publication_version=0,
        )
        storage.get_draft_by_id.return_value = self.factory.admin_showcase_draft(
            id="showcase-publish-core",
            owner_partner_id="partner-1",
            settings={
                "affiliate_id": "affiliate-publish-core",
                "type": "showcase",
                "text_title": "Core publish title",
                "custom_head_code": "<script>window.corePublishHead = true</script>",
                "custom_body_code": "<noscript>core publish body</noscript>",
            },
        )
        storage.list_draft_blocks.return_value = [
            self.factory.admin_showcase_draft_block(
                id="block-publish-core-visible",
                showcase_id="showcase-publish-core",
                visible=True,
                title="Core offers",
            ),
            self.factory.admin_showcase_draft_block(
                id="block-publish-core-hidden",
                showcase_id="showcase-publish-core",
                visible=False,
                title="Hidden offers",
            ),
        ]
        storage.list_draft_offers.return_value = [
            self.factory.admin_showcase_draft_offer(
                id="offer-publish-core-enabled",
                showcase_id="showcase-publish-core",
                block_id="block-publish-core-visible",
                enabled=True,
                fields=[
                    {"key": "amount", "value": "100000", "visible": True},
                    {"key": "internal_score", "value": "A", "visible": False},
                ],
            ),
            self.factory.admin_showcase_draft_offer(
                id="offer-publish-core-disabled",
                showcase_id="showcase-publish-core",
                block_id="block-publish-core-visible",
                enabled=False,
            ),
        ]
        async def create_published_snapshot(**kwargs: object) -> object:
            return self.factory.published_showcase_snapshot(
                showcase_id=str(kwargs["showcase_id"]),
                public_id=str(kwargs["public_id"]),
                version=cast("int", kwargs["version"]),
                snapshot=cast("JsonObject", kwargs["snapshot"]),
                created_by_user_id=str(kwargs["created_by_user_id"]),
                created_by_partner_id=str(kwargs["created_by_partner_id"]),
            )

        storage.create_published_snapshot.side_effect = create_published_snapshot
        storage.activate_published_snapshot.return_value = (
            self.factory.admin_showcase_publication_state(
                id="showcase-publish-core",
                public_id="public-publish-core",
                version=1,
                active=True,
                snapshot={"id": "public-publish-core"},
            )
        )
        use_case = PublishAdminShowcaseUseCase(
            storage=storage,
            cache_invalidator=cache_invalidator,
        )
        context = AdminActorContext(user_id="admin-user-1", partner_id="partner-1")

        result = await use_case.execute(showcase_id="showcase-publish-core", context=context)

        assert result == self.factory.admin_showcase_publication(
            id="showcase-publish-core",
            public_id="public-publish-core",
            version=1,
            published=True,
        )
        storage.get_by_id.assert_awaited_once_with(showcase_id="showcase-publish-core")
        storage.get_draft_by_id.assert_awaited_once_with(showcase_id="showcase-publish-core")
        storage.list_draft_blocks.assert_awaited_once_with(showcase_id="showcase-publish-core")
        storage.list_draft_offers.assert_awaited_once_with(showcase_id="showcase-publish-core")
        storage.public_id_exists.assert_not_awaited()
        storage.ensure_showcase_public_id.assert_not_awaited()
        create_kwargs = storage.create_published_snapshot.await_args.kwargs
        assert create_kwargs["showcase_id"] == "showcase-publish-core"
        assert create_kwargs["public_id"] == "public-publish-core"
        assert create_kwargs["version"] == 1
        assert create_kwargs["created_by_user_id"] == "admin-user-1"
        assert create_kwargs["created_by_partner_id"] == "partner-1"
        assert create_kwargs["snapshot"]["id"] == "public-publish-core"
        assert create_kwargs["snapshot"]["custom_head_code"] == (
            "<script>window.corePublishHead = true</script>"
        )
        assert create_kwargs["snapshot"]["custom_body_code"] == (
            "<noscript>core publish body</noscript>"
        )
        assert create_kwargs["snapshot"]["blocks"][0]["offers"][0]["id"] == (
            "offer-publish-core-enabled"
        )
        assert storage.activate_published_snapshot.await_args.kwargs == {
            "showcase_id": "showcase-publish-core",
            "public_id": "public-publish-core",
            "version": 1,
            "snapshot": create_kwargs["snapshot"],
        }
        storage.append_showcase_audit_record.assert_awaited_once_with(
            showcase_id="showcase-publish-core",
            action="showcase_published",
            actor_user_id="admin-user-1",
            actor_partner_id="partner-1",
            metadata={"public_id": "public-publish-core", "version": 1},
        )
        cache_invalidator.invalidate_public_showcase.assert_awaited_once_with(
            public_id="public-publish-core"
        )

    async def test_allows_publish_with_configured_fallback_without_enabled_offers(self) -> None:
        storage = AsyncMock(spec=AdminShowcaseStorage)
        cache_invalidator = AsyncMock(spec=PublicShowcaseCacheInvalidator)
        storage.get_by_id.return_value = self.factory.admin_showcase(
            id="showcase-publish-core-fallback",
            owner_partner_id="partner-1",
            public_id="public-publish-core-fallback",
        )
        storage.get_draft_by_id.return_value = self.factory.admin_showcase_draft(
            id="showcase-publish-core-fallback",
            owner_partner_id="partner-1",
            settings={
                "affiliate_id": "affiliate-publish-core-fallback",
                "type": "showcase",
                "fallback_text": "No offers available",
            },
        )
        storage.list_draft_blocks.return_value = []
        storage.list_draft_offers.return_value = []
        storage.create_published_snapshot.return_value = self.factory.published_showcase_snapshot(
            showcase_id="showcase-publish-core-fallback",
            public_id="public-publish-core-fallback",
            version=1,
        )
        storage.activate_published_snapshot.return_value = (
            self.factory.admin_showcase_publication_state(
                id="showcase-publish-core-fallback",
                public_id="public-publish-core-fallback",
                version=1,
            )
        )
        use_case = PublishAdminShowcaseUseCase(
            storage=storage,
            cache_invalidator=cache_invalidator,
        )
        context = AdminActorContext(user_id="admin-user-1", partner_id="partner-1")

        result = await use_case.execute(
            showcase_id="showcase-publish-core-fallback",
            context=context,
        )

        assert result.public_id == "public-publish-core-fallback"
        assert result.version == 1
        storage.public_id_exists.assert_not_awaited()
        storage.ensure_showcase_public_id.assert_not_awaited()
        storage.create_published_snapshot.assert_awaited_once()
        storage.append_showcase_audit_record.assert_awaited_once()
        cache_invalidator.invalidate_public_showcase.assert_awaited_once_with(
            public_id="public-publish-core-fallback"
        )

    async def test_rejects_publish_without_enabled_offer_or_fallback(self) -> None:
        storage = AsyncMock(spec=AdminShowcaseStorage)
        cache_invalidator = AsyncMock(spec=PublicShowcaseCacheInvalidator)
        storage.get_by_id.return_value = self.factory.admin_showcase(
            id="showcase-publish-core-invalid",
            owner_partner_id="partner-1",
            public_id="public-publish-core-invalid",
            publication_version=1,
        )
        storage.get_draft_by_id.return_value = self.factory.admin_showcase_draft(
            id="showcase-publish-core-invalid",
            owner_partner_id="partner-1",
            settings={
                "affiliate_id": "affiliate-publish-core-invalid",
                "type": "showcase",
            },
        )
        storage.list_draft_blocks.return_value = []
        storage.list_draft_offers.return_value = [
            self.factory.admin_showcase_draft_offer(enabled=False)
        ]
        use_case = PublishAdminShowcaseUseCase(
            storage=storage,
            cache_invalidator=cache_invalidator,
        )
        context = AdminActorContext(user_id="admin-user-1", partner_id="partner-1")

        with pytest.raises(AdminShowcasePublicationValidationError) as error:
            await use_case.execute(showcase_id="showcase-publish-core-invalid", context=context)

        assert error.value.detail == (
            "ADMIN_SHOWCASE_PUBLICATION_REQUIRES_AVAILABLE_OFFER_OR_FALLBACK"
        )
        storage.ensure_showcase_public_id.assert_not_awaited()
        storage.create_published_snapshot.assert_not_awaited()
        storage.activate_published_snapshot.assert_not_awaited()
        storage.append_showcase_audit_record.assert_not_awaited()
        cache_invalidator.invalidate_public_showcase.assert_not_awaited()

    async def test_forbids_foreign_owner_before_publish_reads(self) -> None:
        storage = AsyncMock(spec=AdminShowcaseStorage)
        cache_invalidator = AsyncMock(spec=PublicShowcaseCacheInvalidator)
        storage.get_by_id.return_value = self.factory.admin_showcase(
            id="showcase-publish-core-foreign",
            owner_partner_id="partner-2",
        )
        use_case = PublishAdminShowcaseUseCase(
            storage=storage,
            cache_invalidator=cache_invalidator,
        )
        context = AdminActorContext(user_id="admin-user-1", partner_id="partner-1")

        with pytest.raises(ShowcaseAccessDeniedError) as error:
            await use_case.execute(showcase_id="showcase-publish-core-foreign", context=context)

        assert error.value.detail == "SHOWCASE_ACCESS_DENIED_ERROR"
        storage.get_by_id.assert_awaited_once_with(showcase_id="showcase-publish-core-foreign")
        storage.get_draft_by_id.assert_not_awaited()
        storage.create_published_snapshot.assert_not_awaited()
        storage.append_showcase_audit_record.assert_not_awaited()
        cache_invalidator.invalidate_public_showcase.assert_not_awaited()

    async def test_audit_failure_prevents_cache_invalidation(self) -> None:
        storage = AsyncMock(spec=AdminShowcaseStorage)
        cache_invalidator = AsyncMock(spec=PublicShowcaseCacheInvalidator)
        storage.get_by_id.return_value = self.factory.admin_showcase(
            id="showcase-publish-core-audit-failure",
            owner_partner_id="partner-1",
            public_id="public-publish-core-audit-failure",
        )
        storage.get_draft_by_id.return_value = self.factory.admin_showcase_draft(
            id="showcase-publish-core-audit-failure",
            owner_partner_id="partner-1",
            settings={
                "affiliate_id": "affiliate-publish-core-audit-failure",
                "type": "showcase",
                "fallback_text": "Fallback only",
            },
        )
        storage.list_draft_blocks.return_value = []
        storage.list_draft_offers.return_value = []
        storage.create_published_snapshot.return_value = self.factory.published_showcase_snapshot(
            showcase_id="showcase-publish-core-audit-failure",
            public_id="public-publish-core-audit-failure",
            version=1,
        )
        storage.append_showcase_audit_record.side_effect = RuntimeError("audit failed")
        use_case = PublishAdminShowcaseUseCase(
            storage=storage,
            cache_invalidator=cache_invalidator,
        )
        context = AdminActorContext(user_id="admin-user-1", partner_id="partner-1")

        with pytest.raises(RuntimeError, match="audit failed"):
            await use_case.execute(
                showcase_id="showcase-publish-core-audit-failure",
                context=context,
            )

        storage.create_published_snapshot.assert_not_awaited()
        storage.activate_published_snapshot.assert_not_awaited()
        storage.public_id_exists.assert_not_awaited()
        storage.ensure_showcase_public_id.assert_not_awaited()
        storage.append_showcase_audit_record.assert_awaited_once()
        cache_invalidator.invalidate_public_showcase.assert_not_awaited()

    async def test_propagates_not_found_before_publish_reads(self) -> None:
        storage = AsyncMock(spec=AdminShowcaseStorage)
        cache_invalidator = AsyncMock(spec=PublicShowcaseCacheInvalidator)
        storage.get_by_id.side_effect = AdminShowcaseNotFoundError
        use_case = PublishAdminShowcaseUseCase(
            storage=storage,
            cache_invalidator=cache_invalidator,
        )
        context = AdminActorContext(user_id="admin-user-1", partner_id="partner-1")

        with pytest.raises(AdminShowcaseNotFoundError) as error:
            await use_case.execute(showcase_id="missing-showcase", context=context)

        assert error.value.detail == "ADMIN_SHOWCASE_NOT_FOUND_ERROR"
        storage.get_by_id.assert_awaited_once_with(showcase_id="missing-showcase")
        storage.get_draft_by_id.assert_not_awaited()
        storage.create_published_snapshot.assert_not_awaited()
        cache_invalidator.invalidate_public_showcase.assert_not_awaited()


class TestUnpublishAdminShowcaseUseCase(FactoryFixture):
    async def test_unpublishes_active_snapshot_with_audit_and_cache_invalidation(self) -> None:
        storage = AsyncMock(spec=AdminShowcaseStorage)
        cache_invalidator = AsyncMock(spec=PublicShowcaseCacheInvalidator)
        storage.get_by_id.return_value = self.factory.admin_showcase(
            id="showcase-unpublish-core",
            owner_partner_id="partner-1",
            public_id="public-unpublish-core",
            publication_version=1,
            published_snapshot={"id": "public-unpublish-core"},
        )
        storage.deactivate_published_showcase.return_value = (
            self.factory.admin_showcase_publication_state(
                id="showcase-unpublish-core",
                public_id="public-unpublish-core",
                version=2,
                active=False,
                snapshot=None,
            )
        )
        use_case = UnpublishAdminShowcaseUseCase(
            storage=storage,
            cache_invalidator=cache_invalidator,
        )
        context = AdminActorContext(user_id="admin-user-1", partner_id="partner-1")

        result = await use_case.execute(showcase_id="showcase-unpublish-core", context=context)

        assert result == self.factory.admin_showcase_publication(
            id="showcase-unpublish-core",
            public_id="public-unpublish-core",
            version=2,
            published=False,
        )
        storage.get_by_id.assert_awaited_once_with(showcase_id="showcase-unpublish-core")
        storage.deactivate_published_showcase.assert_awaited_once_with(
            showcase_id="showcase-unpublish-core",
            version=2,
        )
        storage.deactivate_published_route_bindings.assert_awaited_once_with(
            showcase_id="showcase-unpublish-core",
            public_id="public-unpublish-core",
        )
        storage.append_showcase_audit_record.assert_awaited_once_with(
            showcase_id="showcase-unpublish-core",
            action="showcase_unpublished",
            actor_user_id="admin-user-1",
            actor_partner_id="partner-1",
            metadata={"public_id": "public-unpublish-core", "version": 2},
        )
        cache_invalidator.invalidate_public_showcase.assert_awaited_once_with(
            public_id="public-unpublish-core"
        )

    async def test_rejects_unpublish_without_active_publication(self) -> None:
        storage = AsyncMock(spec=AdminShowcaseStorage)
        cache_invalidator = AsyncMock(spec=PublicShowcaseCacheInvalidator)
        storage.get_by_id.return_value = self.factory.admin_showcase(
            id="showcase-unpublish-core-inactive",
            owner_partner_id="partner-1",
            public_id=None,
            publication_version=0,
            published_snapshot=None,
        )
        use_case = UnpublishAdminShowcaseUseCase(
            storage=storage,
            cache_invalidator=cache_invalidator,
        )
        context = AdminActorContext(user_id="admin-user-1", partner_id="partner-1")

        with pytest.raises(AdminShowcasePublicationValidationError) as error:
            await use_case.execute(
                showcase_id="showcase-unpublish-core-inactive",
                context=context,
            )

        assert error.value.detail == "ADMIN_SHOWCASE_PUBLICATION_NOT_ACTIVE"
        storage.deactivate_published_showcase.assert_not_awaited()
        storage.deactivate_published_route_bindings.assert_not_awaited()
        storage.append_showcase_audit_record.assert_not_awaited()
        cache_invalidator.invalidate_public_showcase.assert_not_awaited()

    async def test_forbids_foreign_owner_before_unpublish_mutation(self) -> None:
        storage = AsyncMock(spec=AdminShowcaseStorage)
        cache_invalidator = AsyncMock(spec=PublicShowcaseCacheInvalidator)
        storage.get_by_id.return_value = self.factory.admin_showcase(
            id="showcase-unpublish-core-foreign",
            owner_partner_id="partner-2",
            public_id="public-unpublish-core-foreign",
            publication_version=1,
            published_snapshot={"id": "public-unpublish-core-foreign"},
        )
        use_case = UnpublishAdminShowcaseUseCase(
            storage=storage,
            cache_invalidator=cache_invalidator,
        )
        context = AdminActorContext(user_id="admin-user-1", partner_id="partner-1")

        with pytest.raises(ShowcaseAccessDeniedError) as error:
            await use_case.execute(showcase_id="showcase-unpublish-core-foreign", context=context)

        assert error.value.detail == "SHOWCASE_ACCESS_DENIED_ERROR"
        storage.get_by_id.assert_awaited_once_with(showcase_id="showcase-unpublish-core-foreign")
        storage.deactivate_published_showcase.assert_not_awaited()
        storage.append_showcase_audit_record.assert_not_awaited()
        cache_invalidator.invalidate_public_showcase.assert_not_awaited()

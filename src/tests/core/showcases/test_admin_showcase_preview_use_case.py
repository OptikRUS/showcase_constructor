from unittest.mock import AsyncMock

import pytest

from src.core.admin_auth.schemas import AdminActorContext
from src.core.showcases.exceptions import AdminShowcaseNotFoundError, ShowcaseAccessDeniedError
from src.core.showcases.schemas import AdminShowcasePreviewMode
from src.core.showcases.use_cases import BuildAdminShowcasePreviewUseCase
from src.core.storages import AdminShowcaseStorage
from src.tests.fixtures import FactoryFixture


class TestBuildAdminShowcasePreviewUseCase(FactoryFixture):
    async def test_builds_preview_from_draft_without_publication_mutation(self) -> None:
        storage = AsyncMock(spec=AdminShowcaseStorage)
        storage.get_by_id.return_value = self.factory.admin_showcase(
            id="showcase-preview-core",
            owner_partner_id="partner-1",
            title="Preview core showcase",
        )
        storage.get_draft_by_id.return_value = self.factory.admin_showcase_draft(
            id="showcase-preview-core",
            owner_partner_id="partner-1",
            title="Preview core showcase",
            settings={
                "affiliate_id": "affiliate-preview-core",
                "type": "showcase",
                "text_title": "Core draft title",
                "custom_head_code": "<script>window.coreHead = true</script>",
                "custom_body_code": "<noscript>core body pixel</noscript>",
            },
            published_snapshot={"id": "public-preview-core"},
        )
        storage.list_draft_blocks.return_value = [
            self.factory.admin_showcase_draft_block(
                id="block-core-preview-visible",
                showcase_id="showcase-preview-core",
                visible=True,
                title="Visible preview block",
            ),
            self.factory.admin_showcase_draft_block(
                id="block-core-preview-hidden",
                showcase_id="showcase-preview-core",
                visible=False,
                title="Hidden preview block",
            ),
        ]
        storage.list_draft_offers.return_value = [
            self.factory.admin_showcase_draft_offer(
                id="offer-core-preview-enabled",
                showcase_id="showcase-preview-core",
                block_id="block-core-preview-visible",
                enabled=True,
                fields=[
                    {"key": "amount", "value": "100000", "visible": True},
                    {"key": "internal_score", "value": "A", "visible": False},
                ],
                categories=["loans"],
                display_name="Core preview offer",
            ),
            self.factory.admin_showcase_draft_offer(
                id="offer-core-preview-disabled",
                showcase_id="showcase-preview-core",
                block_id="block-core-preview-visible",
                enabled=False,
                display_name="Disabled core preview offer",
            ),
        ]
        use_case = BuildAdminShowcasePreviewUseCase(storage=storage)
        context = AdminActorContext(user_id="admin-user-1", partner_id="partner-1")

        result = await use_case.execute(
            showcase_id="showcase-preview-core",
            mode="mobile",
            context=context,
        )

        assert result.preview is True
        assert result.mode == "mobile"
        assert result.config.id == "preview-showcase-preview-core"
        assert result.config.affiliate_id == "affiliate-preview-core"
        assert result.config.settings.text_title == "Core draft title"
        assert [block.title for block in result.config.blocks] == ["Visible preview block"]
        assert result.config.blocks[0].offers[0].id == "offer-core-preview-enabled"
        assert [field.key for field in result.config.blocks[0].offers[0].fields] == ["amount"]
        assert result.config.widget_info is None
        assert result.html is not None
        assert 'data-preview="true"' in result.html
        assert 'data-preview-mode="mobile"' in result.html
        assert "<script>window.coreHead = true</script>" in result.html
        assert "<noscript>core body pixel</noscript>" in result.html
        storage.get_by_id.assert_awaited_once_with(showcase_id="showcase-preview-core")
        storage.get_draft_by_id.assert_awaited_once_with(showcase_id="showcase-preview-core")
        storage.list_draft_blocks.assert_awaited_once_with(showcase_id="showcase-preview-core")
        storage.list_draft_offers.assert_awaited_once_with(showcase_id="showcase-preview-core")
        storage.update_draft_settings.assert_not_awaited()
        storage.create_published_snapshot.assert_not_awaited()
        storage.append_showcase_audit_record.assert_not_awaited()

    @pytest.mark.parametrize("mode", ["desktop", "mobile"])
    async def test_accepts_supported_preview_modes(self, mode: AdminShowcasePreviewMode) -> None:
        storage = AsyncMock(spec=AdminShowcaseStorage)
        storage.get_by_id.return_value = self.factory.admin_showcase(
            id="showcase-preview-core-mode",
            owner_partner_id="partner-1",
        )
        storage.get_draft_by_id.return_value = self.factory.admin_showcase_draft(
            id="showcase-preview-core-mode",
            owner_partner_id="partner-1",
        )
        storage.list_draft_blocks.return_value = []
        storage.list_draft_offers.return_value = []
        use_case = BuildAdminShowcasePreviewUseCase(storage=storage)
        context = AdminActorContext(user_id="admin-user-1", partner_id="partner-1")

        result = await use_case.execute(
            showcase_id="showcase-preview-core-mode",
            mode=mode,
            context=context,
        )

        assert result.mode == mode
        assert result.preview is True

    async def test_forbids_foreign_owner_before_reading_draft_data(self) -> None:
        storage = AsyncMock(spec=AdminShowcaseStorage)
        storage.get_by_id.return_value = self.factory.admin_showcase(
            id="showcase-preview-core-foreign",
            owner_partner_id="partner-2",
        )
        use_case = BuildAdminShowcasePreviewUseCase(storage=storage)
        context = AdminActorContext(user_id="admin-user-1", partner_id="partner-1")

        with pytest.raises(ShowcaseAccessDeniedError) as error:
            await use_case.execute(
                showcase_id="showcase-preview-core-foreign",
                mode="desktop",
                context=context,
            )

        assert error.value.detail == "SHOWCASE_ACCESS_DENIED_ERROR"
        storage.get_by_id.assert_awaited_once_with(showcase_id="showcase-preview-core-foreign")
        storage.get_draft_by_id.assert_not_awaited()
        storage.list_draft_blocks.assert_not_awaited()
        storage.list_draft_offers.assert_not_awaited()
        storage.create_published_snapshot.assert_not_awaited()
        storage.append_showcase_audit_record.assert_not_awaited()

    async def test_propagates_not_found_before_preview_reads(self) -> None:
        storage = AsyncMock(spec=AdminShowcaseStorage)
        storage.get_by_id.side_effect = AdminShowcaseNotFoundError
        use_case = BuildAdminShowcasePreviewUseCase(storage=storage)
        context = AdminActorContext(user_id="admin-user-1", partner_id="partner-1")

        with pytest.raises(AdminShowcaseNotFoundError) as error:
            await use_case.execute(
                showcase_id="missing-showcase",
                mode="desktop",
                context=context,
            )

        assert error.value.detail == "ADMIN_SHOWCASE_NOT_FOUND_ERROR"
        storage.get_by_id.assert_awaited_once_with(showcase_id="missing-showcase")
        storage.get_draft_by_id.assert_not_awaited()
        storage.list_draft_blocks.assert_not_awaited()
        storage.list_draft_offers.assert_not_awaited()

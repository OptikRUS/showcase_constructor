import pytest

from src.core.showcases.exceptions import (
    AdminShowcaseDraftBlockNotFoundError,
    AdminShowcaseDraftOfferNotFoundError,
    AdminShowcaseNotFoundError,
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

from __future__ import annotations

from typing import TYPE_CHECKING

from httpx2 import codes

from src.tests.fixtures import APIFixture, FactoryFixture, StorageFixture

if TYPE_CHECKING:
    from src.core.showcases.schemas import JsonObject


class TestAdminShowcaseOffersAPI(APIFixture, FactoryFixture, StorageFixture):
    async def test_creates_and_lists_draft_offers(self) -> None:
        published_snapshot: JsonObject = {
            "id": "public-showcase-api-offers-1",
            "blocks": [{"type": "offers", "offers": [{"id": "published-offer"}]}],
        }
        await self.storage_helper.create_admin_showcase(
            id="showcase-api-offers-1",
            owner_partner_id="partner-1",
            title="Offers showcase",
            draft_settings={"design_id": "classic"},
            published_snapshot=published_snapshot,
        )
        await self.storage_helper.create_admin_showcase_draft_block(
            block=self.factory.admin_showcase_draft_block(
                id="block-api-offers-a",
                showcase_id="showcase-api-offers-1",
                order=10,
                title="Primary offers",
            )
        )
        await self.storage_helper.create_admin_showcase_draft_block(
            block=self.factory.admin_showcase_draft_block(
                id="block-api-offers-b",
                showcase_id="showcase-api-offers-1",
                order=20,
                title="Secondary offers",
            )
        )
        await self.storage_helper.create_admin_showcase_draft_offer(
            offer=self.factory.admin_showcase_draft_offer(
                id="offer-api-existing-disabled",
                showcase_id="showcase-api-offers-1",
                block_id="block-api-offers-b",
                enabled=False,
                manual_order=20,
                cta_text="Draft disabled CTA",
                usp_text="Draft disabled USP",
                fields=[{"key": "rate", "value": "12%", "visible": False}],
                categories=["loans"],
                logo_url="https://cdn.example.test/existing-logo.png",
                rounded_logo_url="https://cdn.example.test/existing-rounded.png",
                display_name="Disabled draft offer",
                site_name="Existing Bank",
                cpa_url="https://cpa.example.test/existing",
                legal_entity="Existing Bank LLC",
                inn="9876543210",
                erid="erid-existing",
                data={"source": "manual"},
            )
        )
        await self.storage_helper.commit()

        create_response = self.api.create_admin_showcase_offer(
            showcase_id="showcase-api-offers-1",
            json={
                "blockId": "block-api-offers-a",
                "enabled": True,
                "manualOrder": 10,
                "ctaText": "Apply now",
                "uspText": "Decision in 5 minutes",
                "fields": [
                    {"key": "amount", "value": "100000", "visible": True},
                    {"key": "internal_score", "value": "A", "visible": False},
                ],
                "categories": ["cash", "cards"],
                "logoUrl": "https://cdn.example.test/new-logo.png",
                "roundedLogoUrl": "https://cdn.example.test/new-rounded.png",
                "displayName": "New draft offer",
                "siteName": "New Bank",
                "cpaUrl": "https://cpa.example.test/new",
                "legalEntity": "New Bank LLC",
                "inn": "1234567890",
                "erid": "erid-new",
                "data": {"source": "manual", "rating": 5},
            },
        )

        assert create_response.status_code == codes.CREATED
        created_payload = create_response.json()
        assert created_payload == {
            "id": created_payload["id"],
            "blockId": "block-api-offers-a",
            "enabled": True,
            "manualOrder": 10,
            "ctaText": "Apply now",
            "uspText": "Decision in 5 minutes",
            "fields": [
                {"key": "amount", "value": "100000", "visible": True},
                {"key": "internal_score", "value": "A", "visible": False},
            ],
            "categories": ["cash", "cards"],
            "logoUrl": "https://cdn.example.test/new-logo.png",
            "roundedLogoUrl": "https://cdn.example.test/new-rounded.png",
            "displayName": "New draft offer",
            "siteName": "New Bank",
            "cpaUrl": "https://cpa.example.test/new",
            "legalEntity": "New Bank LLC",
            "inn": "1234567890",
            "erid": "erid-new",
            "data": {"source": "manual", "rating": 5},
        }
        assert isinstance(created_payload["id"], str)
        assert created_payload["id"]

        list_response = self.api.list_admin_showcase_offers(showcase_id="showcase-api-offers-1")

        assert list_response.status_code == codes.OK
        assert list_response.json() == [
            created_payload,
            {
                "id": "offer-api-existing-disabled",
                "blockId": "block-api-offers-b",
                "enabled": False,
                "manualOrder": 20,
                "ctaText": "Draft disabled CTA",
                "uspText": "Draft disabled USP",
                "fields": [{"key": "rate", "value": "12%", "visible": False}],
                "categories": ["loans"],
                "logoUrl": "https://cdn.example.test/existing-logo.png",
                "roundedLogoUrl": "https://cdn.example.test/existing-rounded.png",
                "displayName": "Disabled draft offer",
                "siteName": "Existing Bank",
                "cpaUrl": "https://cpa.example.test/existing",
                "legalEntity": "Existing Bank LLC",
                "inn": "9876543210",
                "erid": "erid-existing",
                "data": {"source": "manual"},
            },
        ]

        persisted_offers = await self.storage_helper.list_admin_showcase_draft_offers(
            showcase_id="showcase-api-offers-1"
        )
        assert [offer.id for offer in persisted_offers] == [
            created_payload["id"],
            "offer-api-existing-disabled",
        ]
        persisted = await self.storage_helper.get_admin_showcase_draft(
            showcase_id="showcase-api-offers-1"
        )
        assert persisted.published_snapshot == published_snapshot

    async def test_forbids_foreign_owner_offer_access(self) -> None:
        await self.storage_helper.create_admin_showcase(
            id="showcase-api-offers-foreign",
            owner_partner_id="partner-2",
            title="Foreign offers showcase",
            published_snapshot={"id": "public-offers-foreign"},
        )
        await self.storage_helper.create_admin_showcase_draft_block(
            block=self.factory.admin_showcase_draft_block(
                id="block-api-offers-foreign",
                showcase_id="showcase-api-offers-foreign",
            )
        )
        await self.storage_helper.commit()

        list_response = self.api.list_admin_showcase_offers(
            showcase_id="showcase-api-offers-foreign"
        )
        create_response = self.api.create_admin_showcase_offer(
            showcase_id="showcase-api-offers-foreign",
            json={
                "blockId": "block-api-offers-foreign",
                "manualOrder": 1,
                "displayName": "Foreign offer",
            },
        )

        assert list_response.status_code == codes.FORBIDDEN
        assert list_response.json() == {"detail": "SHOWCASE_ACCESS_DENIED_ERROR"}
        assert create_response.status_code == codes.FORBIDDEN
        assert create_response.json() == {"detail": "SHOWCASE_ACCESS_DENIED_ERROR"}
        persisted_offers = await self.storage_helper.list_admin_showcase_draft_offers(
            showcase_id="showcase-api-offers-foreign"
        )
        assert persisted_offers == []

    async def test_patches_and_deletes_draft_offer(self) -> None:
        published_snapshot: JsonObject = {
            "id": "public-showcase-api-offers-patch",
            "blocks": [{"type": "offers", "offers": [{"id": "published-offer"}]}],
        }
        await self.storage_helper.create_admin_showcase(
            id="showcase-api-offers-patch",
            owner_partner_id="partner-1",
            title="Patch offers showcase",
            published_snapshot=published_snapshot,
        )
        await self.storage_helper.create_admin_showcase_draft_block(
            block=self.factory.admin_showcase_draft_block(
                id="block-api-offers-patch-a",
                showcase_id="showcase-api-offers-patch",
                order=10,
                title="Primary offers",
            )
        )
        await self.storage_helper.create_admin_showcase_draft_block(
            block=self.factory.admin_showcase_draft_block(
                id="block-api-offers-patch-b",
                showcase_id="showcase-api-offers-patch",
                order=20,
                title="Secondary offers",
            )
        )
        await self.storage_helper.create_admin_showcase_draft_offer(
            offer=self.factory.admin_showcase_draft_offer(
                id="offer-api-patch-target",
                showcase_id="showcase-api-offers-patch",
                block_id="block-api-offers-patch-b",
                enabled=True,
                manual_order=20,
                cta_text="Original CTA",
                usp_text="Original USP",
                fields=[{"key": "rate", "value": "12%", "visible": True}],
                categories=["loans"],
                logo_url="https://cdn.example.test/original-logo.png",
                rounded_logo_url="https://cdn.example.test/original-rounded.png",
                display_name="Original offer",
                site_name="Original Bank",
                cpa_url="https://cpa.example.test/original",
                legal_entity="Original Bank LLC",
                inn="1111111111",
                erid="erid-original",
                data={"source": "manual"},
            )
        )
        await self.storage_helper.create_admin_showcase_draft_offer(
            offer=self.factory.admin_showcase_draft_offer(
                id="offer-api-delete-target",
                showcase_id="showcase-api-offers-patch",
                block_id="block-api-offers-patch-a",
                enabled=True,
                manual_order=10,
                display_name="Delete me",
            )
        )
        await self.storage_helper.create_admin_showcase_draft_offer(
            offer=self.factory.admin_showcase_draft_offer(
                id="offer-api-preserved",
                showcase_id="showcase-api-offers-patch",
                block_id="block-api-offers-patch-b",
                enabled=True,
                manual_order=30,
                display_name="Preserved offer",
            )
        )
        await self.storage_helper.commit()

        patch_response = self.api.patch_admin_showcase_offer(
            showcase_id="showcase-api-offers-patch",
            offer_id="offer-api-patch-target",
            json={
                "blockId": "block-api-offers-patch-a",
                "enabled": False,
                "manualOrder": 5,
                "ctaText": None,
                "uspText": "Updated hidden USP",
                "fields": [
                    {"key": "amount", "value": "100000", "visible": True},
                    {"key": "internal_score", "value": "A", "visible": False},
                ],
                "categories": ["cash", "cards"],
                "logoUrl": "https://cdn.example.test/updated-logo.png",
                "roundedLogoUrl": None,
                "displayName": "Updated draft offer",
                "siteName": "Updated Bank",
                "cpaUrl": "https://cpa.example.test/updated",
                "legalEntity": "Updated Bank LLC",
                "inn": "2222222222",
                "erid": "erid-updated",
                "data": {"source": "manual", "tier": "draft"},
            },
        )
        delete_response = self.api.delete_admin_showcase_offer(
            showcase_id="showcase-api-offers-patch",
            offer_id="offer-api-delete-target",
        )

        assert patch_response.status_code == codes.OK
        assert patch_response.json() == {
            "id": "offer-api-patch-target",
            "blockId": "block-api-offers-patch-a",
            "enabled": False,
            "manualOrder": 5,
            "ctaText": None,
            "uspText": "Updated hidden USP",
            "fields": [
                {"key": "amount", "value": "100000", "visible": True},
                {"key": "internal_score", "value": "A", "visible": False},
            ],
            "categories": ["cash", "cards"],
            "logoUrl": "https://cdn.example.test/updated-logo.png",
            "roundedLogoUrl": None,
            "displayName": "Updated draft offer",
            "siteName": "Updated Bank",
            "cpaUrl": "https://cpa.example.test/updated",
            "legalEntity": "Updated Bank LLC",
            "inn": "2222222222",
            "erid": "erid-updated",
            "data": {"source": "manual", "tier": "draft"},
        }
        assert delete_response.status_code == codes.NO_CONTENT
        assert delete_response.content == b""

        list_response = self.api.list_admin_showcase_offers(
            showcase_id="showcase-api-offers-patch"
        )
        assert list_response.status_code == codes.OK
        assert list_response.json() == [
            patch_response.json(),
            {
                "id": "offer-api-preserved",
                "blockId": "block-api-offers-patch-b",
                "enabled": True,
                "manualOrder": 30,
                "ctaText": "Open offer",
                "uspText": "Fast approval",
                "fields": [],
                "categories": [],
                "logoUrl": "https://cdn.example.test/logo.png",
                "roundedLogoUrl": "https://cdn.example.test/logo-rounded.png",
                "displayName": "Preserved offer",
                "siteName": "Example Bank",
                "cpaUrl": "https://cpa.example.test/click",
                "legalEntity": "Example Bank LLC",
                "inn": "1234567890",
                "erid": None,
                "data": {},
            },
        ]
        persisted = await self.storage_helper.get_admin_showcase_draft(
            showcase_id="showcase-api-offers-patch"
        )
        assert persisted.published_snapshot == published_snapshot

    async def test_forbids_foreign_owner_offer_mutation(self) -> None:
        await self.storage_helper.create_admin_showcase(
            id="showcase-api-offers-patch-foreign",
            owner_partner_id="partner-2",
            title="Foreign offer mutation showcase",
        )
        await self.storage_helper.create_admin_showcase_draft_offer(
            offer=self.factory.admin_showcase_draft_offer(
                id="offer-api-patch-foreign",
                showcase_id="showcase-api-offers-patch-foreign",
                enabled=True,
                manual_order=10,
            )
        )
        await self.storage_helper.commit()

        patch_response = self.api.patch_admin_showcase_offer(
            showcase_id="showcase-api-offers-patch-foreign",
            offer_id="offer-api-patch-foreign",
            json={"enabled": False},
        )
        delete_response = self.api.delete_admin_showcase_offer(
            showcase_id="showcase-api-offers-patch-foreign",
            offer_id="offer-api-patch-foreign",
        )

        assert patch_response.status_code == codes.FORBIDDEN
        assert patch_response.json() == {"detail": "SHOWCASE_ACCESS_DENIED_ERROR"}
        assert delete_response.status_code == codes.FORBIDDEN
        assert delete_response.json() == {"detail": "SHOWCASE_ACCESS_DENIED_ERROR"}
        persisted_offers = await self.storage_helper.list_admin_showcase_draft_offers(
            showcase_id="showcase-api-offers-patch-foreign"
        )
        assert persisted_offers[0].enabled is True

    async def test_returns_not_found_for_missing_offer(self) -> None:
        await self.storage_helper.create_admin_showcase(
            id="showcase-api-offers-missing-offer",
            owner_partner_id="partner-1",
            title="Missing offer showcase",
        )
        await self.storage_helper.commit()

        patch_response = self.api.patch_admin_showcase_offer(
            showcase_id="showcase-api-offers-missing-offer",
            offer_id="missing-offer",
            json={"enabled": False},
        )
        delete_response = self.api.delete_admin_showcase_offer(
            showcase_id="showcase-api-offers-missing-offer",
            offer_id="missing-offer",
        )

        assert patch_response.status_code == codes.NOT_FOUND
        assert patch_response.json() == {"detail": "ADMIN_SHOWCASE_DRAFT_OFFER_NOT_FOUND_ERROR"}
        assert delete_response.status_code == codes.NOT_FOUND
        assert delete_response.json() == {"detail": "ADMIN_SHOWCASE_DRAFT_OFFER_NOT_FOUND_ERROR"}

    async def test_returns_not_found_for_missing_offer_block_assignment(self) -> None:
        await self.storage_helper.create_admin_showcase(
            id="showcase-api-offers-patch-missing-block",
            owner_partner_id="partner-1",
            title="Missing patch block showcase",
        )
        await self.storage_helper.create_admin_showcase_draft_block(
            block=self.factory.admin_showcase_draft_block(
                id="block-api-offers-patch-existing",
                showcase_id="showcase-api-offers-patch-missing-block",
            )
        )
        await self.storage_helper.create_admin_showcase_draft_offer(
            offer=self.factory.admin_showcase_draft_offer(
                id="offer-api-patch-missing-block",
                showcase_id="showcase-api-offers-patch-missing-block",
                block_id="block-api-offers-patch-existing",
                enabled=True,
            )
        )
        await self.storage_helper.commit()

        response = self.api.patch_admin_showcase_offer(
            showcase_id="showcase-api-offers-patch-missing-block",
            offer_id="offer-api-patch-missing-block",
            json={"blockId": "missing-block"},
        )

        assert response.status_code == codes.NOT_FOUND
        assert response.json() == {"detail": "ADMIN_SHOWCASE_DRAFT_BLOCK_NOT_FOUND_ERROR"}
        persisted_offers = await self.storage_helper.list_admin_showcase_draft_offers(
            showcase_id="showcase-api-offers-patch-missing-block"
        )
        assert persisted_offers[0].block_id == "block-api-offers-patch-existing"

    def test_returns_not_found_for_missing_showcase(self) -> None:
        list_response = self.api.list_admin_showcase_offers(showcase_id="missing-showcase")
        create_response = self.api.create_admin_showcase_offer(
            showcase_id="missing-showcase",
            json={"manualOrder": 1, "displayName": "Missing showcase offer"},
        )
        patch_response = self.api.patch_admin_showcase_offer(
            showcase_id="missing-showcase",
            offer_id="missing-offer",
            json={"enabled": False},
        )
        delete_response = self.api.delete_admin_showcase_offer(
            showcase_id="missing-showcase",
            offer_id="missing-offer",
        )

        assert list_response.status_code == codes.NOT_FOUND
        assert list_response.json() == {"detail": "ADMIN_SHOWCASE_NOT_FOUND_ERROR"}
        assert create_response.status_code == codes.NOT_FOUND
        assert create_response.json() == {"detail": "ADMIN_SHOWCASE_NOT_FOUND_ERROR"}
        assert patch_response.status_code == codes.NOT_FOUND
        assert patch_response.json() == {"detail": "ADMIN_SHOWCASE_NOT_FOUND_ERROR"}
        assert delete_response.status_code == codes.NOT_FOUND
        assert delete_response.json() == {"detail": "ADMIN_SHOWCASE_NOT_FOUND_ERROR"}

    async def test_returns_not_found_for_missing_block_assignment(self) -> None:
        await self.storage_helper.create_admin_showcase(
            id="showcase-api-offers-missing-block",
            owner_partner_id="partner-1",
            title="Missing block offer showcase",
        )
        await self.storage_helper.commit()

        response = self.api.create_admin_showcase_offer(
            showcase_id="showcase-api-offers-missing-block",
            json={
                "blockId": "missing-block",
                "manualOrder": 1,
                "displayName": "Offer with missing block",
            },
        )

        assert response.status_code == codes.NOT_FOUND
        assert response.json() == {"detail": "ADMIN_SHOWCASE_DRAFT_BLOCK_NOT_FOUND_ERROR"}
        persisted_offers = await self.storage_helper.list_admin_showcase_draft_offers(
            showcase_id="showcase-api-offers-missing-block"
        )
        assert persisted_offers == []


class TestAdminShowcaseOffersNoAuthAPI(APIFixture, StorageFixture):
    async def test_requires_authentication(self) -> None:
        await self.storage_helper.create_admin_showcase(
            id="showcase-api-offers-no-auth",
            owner_partner_id="partner-1",
            title="No auth offers showcase",
            published_snapshot={"id": "public-offers-no-auth"},
        )
        await self.storage_helper.commit()

        list_response = self.no_auth_api.list_admin_showcase_offers(
            showcase_id="showcase-api-offers-no-auth"
        )
        create_response = self.no_auth_api.create_admin_showcase_offer(
            showcase_id="showcase-api-offers-no-auth",
            json={"manualOrder": 1, "displayName": "No auth offer"},
        )
        patch_response = self.no_auth_api.patch_admin_showcase_offer(
            showcase_id="showcase-api-offers-no-auth",
            offer_id="offer-no-auth",
            json={"enabled": False},
        )
        delete_response = self.no_auth_api.delete_admin_showcase_offer(
            showcase_id="showcase-api-offers-no-auth",
            offer_id="offer-no-auth",
        )

        assert list_response.status_code == codes.UNAUTHORIZED
        assert list_response.json() == {"detail": "ADMIN_AUTHENTICATION_REQUIRED_ERROR"}
        assert create_response.status_code == codes.UNAUTHORIZED
        assert create_response.json() == {"detail": "ADMIN_AUTHENTICATION_REQUIRED_ERROR"}
        assert patch_response.status_code == codes.UNAUTHORIZED
        assert patch_response.json() == {"detail": "ADMIN_AUTHENTICATION_REQUIRED_ERROR"}
        assert delete_response.status_code == codes.UNAUTHORIZED
        assert delete_response.json() == {"detail": "ADMIN_AUTHENTICATION_REQUIRED_ERROR"}
        persisted_offers = await self.storage_helper.list_admin_showcase_draft_offers(
            showcase_id="showcase-api-offers-no-auth"
        )
        assert persisted_offers == []

from unittest.mock import AsyncMock
from uuid import UUID

import pytest

from src.core.admin_auth.schemas import AdminActorContext
from src.core.showcases.exceptions import (
    AdminShowcaseDraftBlockNotFoundError,
    AdminShowcaseNotFoundError,
    ShowcaseAccessDeniedError,
)
from src.core.showcases.use_cases import (
    CreateAdminShowcaseOfferUseCase,
    ListAdminShowcaseOffersUseCase,
)
from src.core.storages import AdminShowcaseStorage
from src.tests.fixtures import FactoryFixture


class TestListAdminShowcaseOffersUseCase(FactoryFixture):
    async def test_lists_same_owner_draft_offers(self) -> None:
        storage = AsyncMock(spec=AdminShowcaseStorage)
        storage.get_by_id.return_value = self.factory.admin_showcase(
            id="showcase-offers-core-list",
            owner_partner_id="partner-1",
        )
        offers = [
            self.factory.admin_showcase_draft_offer(
                id="offer-core-list-1",
                showcase_id="showcase-offers-core-list",
                enabled=False,
            )
        ]
        storage.list_draft_offers.return_value = offers
        use_case = ListAdminShowcaseOffersUseCase(storage=storage)
        context = AdminActorContext(user_id="admin-user-1", partner_id="partner-1")

        result = await use_case.execute(showcase_id="showcase-offers-core-list", context=context)

        assert result == offers
        storage.get_by_id.assert_awaited_once_with(showcase_id="showcase-offers-core-list")
        storage.list_draft_offers.assert_awaited_once_with(
            showcase_id="showcase-offers-core-list"
        )

    async def test_forbids_listing_foreign_draft_offers(self) -> None:
        storage = AsyncMock(spec=AdminShowcaseStorage)
        storage.get_by_id.return_value = self.factory.admin_showcase(
            id="showcase-offers-core-foreign",
            owner_partner_id="partner-2",
        )
        use_case = ListAdminShowcaseOffersUseCase(storage=storage)
        context = AdminActorContext(user_id="admin-user-1", partner_id="partner-1")

        with pytest.raises(ShowcaseAccessDeniedError) as error:
            await use_case.execute(showcase_id="showcase-offers-core-foreign", context=context)

        assert error.value.detail == "SHOWCASE_ACCESS_DENIED_ERROR"
        storage.get_by_id.assert_awaited_once_with(showcase_id="showcase-offers-core-foreign")
        storage.list_draft_offers.assert_not_awaited()

    async def test_propagates_not_found_from_storage(self) -> None:
        storage = AsyncMock(spec=AdminShowcaseStorage)
        storage.get_by_id.side_effect = AdminShowcaseNotFoundError
        use_case = ListAdminShowcaseOffersUseCase(storage=storage)
        context = AdminActorContext(user_id="admin-user-1", partner_id="partner-1")

        with pytest.raises(AdminShowcaseNotFoundError) as error:
            await use_case.execute(showcase_id="missing-showcase", context=context)

        assert error.value.detail == "ADMIN_SHOWCASE_NOT_FOUND_ERROR"
        storage.get_by_id.assert_awaited_once_with(showcase_id="missing-showcase")
        storage.list_draft_offers.assert_not_awaited()


class TestCreateAdminShowcaseOfferUseCase(FactoryFixture):
    async def test_creates_same_owner_draft_offer(self) -> None:
        storage = AsyncMock(spec=AdminShowcaseStorage)
        storage.get_by_id.return_value = self.factory.admin_showcase(
            id="showcase-offers-core-create",
            owner_partner_id="partner-1",
        )
        storage.list_draft_blocks.return_value = [
            self.factory.admin_showcase_draft_block(
                id="block-core-offers",
                showcase_id="showcase-offers-core-create",
            )
        ]
        params = self.factory.admin_showcase_draft_offer_create_params(
            block_id="block-core-offers",
            enabled=True,
            manual_order=5,
            fields=[{"key": "amount", "value": "100000", "visible": True}],
            categories=["cash"],
            display_name="Core offer",
        )
        offer_id = UUID("00000000-0000-0000-0000-000000000007")
        created_offer = self.factory.admin_showcase_draft_offer(
            id=str(offer_id),
            showcase_id="showcase-offers-core-create",
            block_id="block-core-offers",
            enabled=True,
            manual_order=5,
            fields=[{"key": "amount", "value": "100000", "visible": True}],
            categories=["cash"],
            display_name="Core offer",
        )
        storage.create_draft_offer.return_value = created_offer
        use_case = CreateAdminShowcaseOfferUseCase(storage=storage, offer_id=offer_id)
        context = AdminActorContext(user_id="admin-user-1", partner_id="partner-1")

        result = await use_case.execute(
            showcase_id="showcase-offers-core-create",
            params=params,
            context=context,
        )

        assert result == created_offer
        storage.get_by_id.assert_awaited_once_with(showcase_id="showcase-offers-core-create")
        storage.list_draft_blocks.assert_awaited_once_with(
            showcase_id="showcase-offers-core-create"
        )
        storage.create_draft_offer.assert_awaited_once_with(
            showcase_id="showcase-offers-core-create",
            offer_id=str(offer_id),
            params=params,
        )

    async def test_forbids_creating_foreign_draft_offer(self) -> None:
        storage = AsyncMock(spec=AdminShowcaseStorage)
        storage.get_by_id.return_value = self.factory.admin_showcase(
            id="showcase-offers-core-create-foreign",
            owner_partner_id="partner-2",
        )
        params = self.factory.admin_showcase_draft_offer_create_params(
            block_id="block-core-foreign"
        )
        offer_id = UUID("00000000-0000-0000-0000-000000000008")
        use_case = CreateAdminShowcaseOfferUseCase(storage=storage, offer_id=offer_id)
        context = AdminActorContext(user_id="admin-user-1", partner_id="partner-1")

        with pytest.raises(ShowcaseAccessDeniedError) as error:
            await use_case.execute(
                showcase_id="showcase-offers-core-create-foreign",
                params=params,
                context=context,
            )

        assert error.value.detail == "SHOWCASE_ACCESS_DENIED_ERROR"
        storage.get_by_id.assert_awaited_once_with(
            showcase_id="showcase-offers-core-create-foreign"
        )
        storage.list_draft_blocks.assert_not_awaited()
        storage.create_draft_offer.assert_not_awaited()

    async def test_rejects_missing_block_assignment(self) -> None:
        storage = AsyncMock(spec=AdminShowcaseStorage)
        storage.get_by_id.return_value = self.factory.admin_showcase(
            id="showcase-offers-core-missing-block",
            owner_partner_id="partner-1",
        )
        storage.list_draft_blocks.return_value = [
            self.factory.admin_showcase_draft_block(
                id="block-core-existing",
                showcase_id="showcase-offers-core-missing-block",
            )
        ]
        params = self.factory.admin_showcase_draft_offer_create_params(
            block_id="block-core-missing"
        )
        offer_id = UUID("00000000-0000-0000-0000-000000000009")
        use_case = CreateAdminShowcaseOfferUseCase(storage=storage, offer_id=offer_id)
        context = AdminActorContext(user_id="admin-user-1", partner_id="partner-1")

        with pytest.raises(AdminShowcaseDraftBlockNotFoundError) as error:
            await use_case.execute(
                showcase_id="showcase-offers-core-missing-block",
                params=params,
                context=context,
            )

        assert error.value.detail == "ADMIN_SHOWCASE_DRAFT_BLOCK_NOT_FOUND_ERROR"
        storage.get_by_id.assert_awaited_once_with(
            showcase_id="showcase-offers-core-missing-block"
        )
        storage.list_draft_blocks.assert_awaited_once_with(
            showcase_id="showcase-offers-core-missing-block"
        )
        storage.create_draft_offer.assert_not_awaited()

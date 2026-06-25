import pytest
from httpx2 import codes

from src.tests.fixtures import APIFixture, FactoryFixture, StorageFixture


class TestPublicConfigRoutesAPI(APIFixture, FactoryFixture, StorageFixture):
    async def test_get_public_config_returns_active_published_snapshot_only(self) -> None:
        await self.storage_helper.create_admin_showcase(
            id="showcase-public-read-api",
            owner_partner_id="partner-1",
            title="Public read API showcase",
            draft_settings={
                "text_title": "Draft title",
                "custom_head_code": "<script>window.draftHead = true</script>",
            },
        )
        await self.storage_helper.create_active_published_showcase_snapshot(
            showcase_id="showcase-public-read-api",
            public_id="public-read-api",
            version=2,
            snapshot=self.factory.published_public_config_snapshot_payload(
                public_id="public-read-api",
                affiliate_id="affiliate-public-read-api",
                text_title="Published title",
                custom_head_code="<script>window.publishedHead = true</script>",
                custom_body_code="<noscript>published body pixel</noscript>",
                extra={
                    "owner_id": "owner-private-1",
                    "admin_showcase_id": "showcase-public-read-api",
                    "draft_settings": {
                        "custom_head_code": "<script>window.draftHead = true</script>",
                    },
                    "custom_code_review_metadata": {"status": "not-public"},
                },
            ),
        )
        await self.storage_helper.commit()

        response = self.no_auth_api.get_public_config(public_id="public-read-api")

        assert response.status_code == codes.OK
        payload = response.json()
        assert payload["id"] == "public-read-api"
        assert payload["affiliateId"] == "affiliate-public-read-api"
        assert payload["settings"]["textTitle"] == "Published title"
        assert payload["customHeadCode"] == "<script>window.publishedHead = true</script>"
        assert payload["customBodyCode"] == "<noscript>published body pixel</noscript>"
        assert payload["blocks"][0]["offers"][0]["fields"] == [
            {"key": "amount", "value": "100000", "visible": True},
        ]
        for forbidden_value in (
            "showcase-public-read-api",
            "owner-private-1",
            "draftHead",
            "custom_code_review_metadata",
            "draftSecret",
            "hidden-draft-value",
        ):
            assert forbidden_value not in response.text
        audit_records = await self.storage_helper.list_showcase_audit_records(
            showcase_id="showcase-public-read-api"
        )
        assert audit_records == []

    async def test_resolve_public_config_returns_explicit_active_route_binding(self) -> None:
        await self.storage_helper.create_admin_showcase(
            id="showcase-public-resolve-api",
            owner_partner_id="partner-1",
            title="Public resolve API showcase",
        )
        await self.storage_helper.create_active_published_showcase_snapshot(
            showcase_id="showcase-public-resolve-api",
            public_id="public-resolve-api",
            version=1,
            snapshot=self.factory.published_public_config_snapshot_payload(
                public_id="public-resolve-api",
                affiliate_id="affiliate-public-resolve-api",
                text_title="Resolved title",
            ),
        )
        await self.storage_helper.create_published_route_binding(
            showcase_id="showcase-public-resolve-api",
            public_id="public-resolve-api",
            host="resolve.example.test",
            path="/offers",
        )
        await self.storage_helper.commit()

        response = self.no_auth_api.resolve_public_config(
            host="resolve.example.test",
            path="/offers",
        )

        assert response.status_code == codes.OK
        payload = response.json()
        assert payload["id"] == "public-resolve-api"
        assert payload["affiliateId"] == "affiliate-public-resolve-api"
        assert payload["settings"]["textTitle"] == "Resolved title"

    async def test_public_reads_return_not_found_for_missing_unpublished_and_inactive(
        self,
    ) -> None:
        await self.storage_helper.create_admin_showcase(
            id="showcase-public-draft-only-api",
            owner_partner_id="partner-1",
            title="Draft-only public API showcase",
            public_id="public-draft-only-api",
        )
        await self.storage_helper.create_admin_showcase(
            id="showcase-public-unpublished-api",
            owner_partner_id="partner-1",
            title="Unpublished public API showcase",
            draft_settings={
                "affiliate_id": "affiliate-public-unpublished-api",
                "type": "showcase",
                "fallback_text": "Fallback only",
            },
        )
        await self.storage_helper.create_active_published_showcase_snapshot(
            showcase_id="showcase-public-unpublished-api",
            public_id="public-unpublished-api",
            version=1,
            snapshot=self.factory.published_public_config_snapshot_payload(
                public_id="public-unpublished-api",
            ),
        )
        await self.storage_helper.create_published_route_binding(
            showcase_id="showcase-public-unpublished-api",
            public_id="public-unpublished-api",
            host="inactive.example.test",
            path="/offers",
        )
        await self.storage_helper.deactivate_admin_showcase_publication(
            showcase_id="showcase-public-unpublished-api",
            public_id="public-unpublished-api",
            version=2,
        )
        await self.storage_helper.commit()

        missing_response = self.no_auth_api.get_public_config(public_id="missing-public-api")
        draft_only_response = self.no_auth_api.get_public_config(
            public_id="public-draft-only-api"
        )
        unpublished_response = self.no_auth_api.get_public_config(
            public_id="public-unpublished-api"
        )
        inactive_resolve_response = self.no_auth_api.resolve_public_config(
            host="inactive.example.test",
            path="/offers",
        )

        assert missing_response.status_code == codes.NOT_FOUND
        assert draft_only_response.status_code == codes.NOT_FOUND
        assert unpublished_response.status_code == codes.NOT_FOUND
        assert inactive_resolve_response.status_code == codes.NOT_FOUND


class TestPublicConfigRouteExposure(APIFixture):
    @pytest.mark.parametrize("method", ["HEAD", "OPTIONS", "POST", "PATCH", "DELETE"])
    def test_unsupported_public_showcase_methods_are_not_exposed(self, method: str) -> None:
        response = self.api.client.request(
            method=method,
            url="/api/v1/public/showcases/example",
        )

        assert response.status_code in {codes.NOT_FOUND, codes.METHOD_NOT_ALLOWED}

from httpx2 import codes

from src.tests.fixtures import APIFixture


class TestDocsAPI(APIFixture):
    def test_swagger_docs_open(self) -> None:
        response = self.api.get_swagger_docs()

        assert response.status_code == codes.OK

    def test_openapi_schema_open(self) -> None:
        response = self.api.get_openapi_schema()

        assert response.status_code == codes.OK

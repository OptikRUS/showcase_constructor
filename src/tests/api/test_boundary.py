from datetime import UTC, datetime

from pydantic import Field

from src.api.boundary import BoundaryModel, SnakeBoundaryModel


class CamelExample(BoundaryModel):
    created_at: datetime
    public_id: str


class SnakeExample(SnakeBoundaryModel):
    created_at: datetime
    public_id: str = Field(alias="public_id")


class TestBoundaryModel:
    def test_parse_validates_payload(self) -> None:
        model = CamelExample.parse(
            {
                "createdAt": "2026-01-02T03:04:05Z",
                "publicId": "showcase-1",
            }
        )

        assert model == CamelExample(
            created_at=datetime(2026, 1, 2, 3, 4, 5, tzinfo=UTC),
            public_id="showcase-1",
        )

    def test_parse_json_validates_payload(self) -> None:
        model = CamelExample.parse_json(
            '{"createdAt": "2026-01-02T03:04:05Z", "publicId": "showcase-1"}'
        )

        assert model.public_id == "showcase-1"
        assert model.created_at == datetime(2026, 1, 2, 3, 4, 5, tzinfo=UTC)

    def test_dict_uses_json_mode_and_aliases(self) -> None:
        model = CamelExample(
            created_at=datetime(2026, 1, 2, 3, 4, 5, tzinfo=UTC),
            public_id="showcase-1",
        )

        assert model.dict() == {
            "createdAt": "2026-01-02T03:04:05Z",
            "publicId": "showcase-1",
        }


class TestSnakeBoundaryModel:
    def test_parse_validates_payload(self) -> None:
        model = SnakeExample.parse(
            {
                "created_at": "2026-01-02T03:04:05Z",
                "public_id": "showcase-1",
            }
        )

        assert model == SnakeExample(
            created_at=datetime(2026, 1, 2, 3, 4, 5, tzinfo=UTC),
            public_id="showcase-1",
        )

    def test_parse_json_validates_payload(self) -> None:
        model = SnakeExample.parse_json(
            '{"created_at": "2026-01-02T03:04:05Z", "public_id": "showcase-1"}'
        )

        assert model.public_id == "showcase-1"
        assert model.created_at == datetime(2026, 1, 2, 3, 4, 5, tzinfo=UTC)

    def test_dict_uses_json_mode_and_aliases(self) -> None:
        model = SnakeExample(
            created_at=datetime(2026, 1, 2, 3, 4, 5, tzinfo=UTC),
            public_id="showcase-1",
        )

        assert model.dict() == {
            "created_at": "2026-01-02T03:04:05Z",
            "public_id": "showcase-1",
        }

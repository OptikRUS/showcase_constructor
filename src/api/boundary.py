from typing import Any, Self

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel, to_snake


class BoundaryModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        from_attributes=True,
        populate_by_name=True,
    )

    @classmethod
    def parse(cls, data: Any) -> Self:
        return cls.model_validate(data)

    @classmethod
    def parse_json(cls, data: Any) -> Self:
        return cls.model_validate_json(data)

    def dict(self, **kwargs: Any) -> dict[str, Any]:
        return self.model_dump(mode="json", by_alias=True, **kwargs)


class SnakeBoundaryModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_snake,
        from_attributes=True,
        populate_by_name=True,
    )

    @classmethod
    def parse(cls, data: Any) -> Self:
        return cls.model_validate(data)

    @classmethod
    def parse_json(cls, data: Any) -> Self:
        return cls.model_validate_json(data)

    def dict(self, **kwargs: Any) -> dict[str, Any]:
        return self.model_dump(mode="json", by_alias=True, **kwargs)

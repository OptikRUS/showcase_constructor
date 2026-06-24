from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel, to_snake


class BoundaryModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        from_attributes=True,
        populate_by_name=True,
    )


class SnakeBoundaryModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_snake,
        from_attributes=True,
        populate_by_name=True,
    )

from pydantic import BaseModel, Field


class IdSchema(BaseModel):
    id: int = Field(
        description="User ID",
        example=1,
        gt=0,
    )


class InstanceVersionSchema(BaseModel):
    version: int = Field(
        description="Instance version",
        examples=[3, 4],
        gt=0,
    )

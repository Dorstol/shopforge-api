from apps.core.schemas import IdSchema, InstanceVersionSchema
from pydantic import BaseModel, ConfigDict, Field


class NewCategory(BaseModel):
    name: str = Field(min_length=3, max_length=50, examples=["Laptops", "Books"])

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")


class SavedCategorySchema(NewCategory, IdSchema, InstanceVersionSchema):
    pass

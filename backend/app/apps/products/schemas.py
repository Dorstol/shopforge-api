from apps.core.schemas import IdSchema, InstanceVersionSchema, PaginationResponseSchema
from pydantic import BaseModel, ConfigDict, Field


class NewCategory(BaseModel):
    name: str = Field(min_length=3, max_length=50, examples=["Laptops", "Books"])

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")


class SavedCategorySchema(NewCategory, IdSchema, InstanceVersionSchema):
    class Config:
        from_attributes = True


class PaginatorSavedCategoryResponseSchema(PaginationResponseSchema):
    items: list[SavedCategorySchema]


class PatchCategorySchema(InstanceVersionSchema, NewCategory):
    pass


class SavedProductSchema(IdSchema):
    title: str
    description: str
    price: float
    category_id: int
    images: list[str]
    main_image: str

    class Config:
        from_attributes = True

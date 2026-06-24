from datetime import datetime
from enum import StrEnum

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


class PaginatorSavedProductResponseSchema(PaginationResponseSchema):
    items: list[SavedProductSchema]


class OrderProductsSchema(BaseModel):
    price: float
    quantity: int
    total: float
    product: SavedProductSchema

    model_config = ConfigDict(from_attributes=True)


class OrderSchema(BaseModel):
    created_at: datetime = Field(examples=[datetime.now()])
    is_closed: bool
    user_id: int
    cost: float
    products: list[OrderProductsSchema]

    class Config:
        from_attributes = True


class ModeChangeOrderProductQuantityEnum(StrEnum):
    INCREASE = "increase"
    DECREASE = "decrease"
    SET = "set"

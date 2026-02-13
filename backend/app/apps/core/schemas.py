from enum import IntEnum, StrEnum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


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


class PaginationResponseSchema(BaseModel):
    items: list
    total: int
    page: int
    limit: int
    pages: int


class PaginationParamsEnum(IntEnum):
    MAX_RESULTS_PER_PAGE = 50
    MIN_RESULTS_PER_PAGE = 1
    DEFAULT_RESULTS_PER_PAGE = 10


class SortEnum(StrEnum):
    ASC = "asc"
    DESC = "desc"


class SortFieldsEnum(StrEnum):
    ID = "id"
    UPDATED_AT = "updated_at"


class SearchParamsSchema(BaseModel):
    q: Optional[str] = Field(None)
    page: int = Field(default=1, ge=1)
    limit: int = Field(
        default=PaginationParamsEnum.DEFAULT_RESULTS_PER_PAGE.value,
        le=PaginationParamsEnum.MAX_RESULTS_PER_PAGE.value,
        ge=PaginationParamsEnum.MIN_RESULTS_PER_PAGE.value,
    )
    sort_direction: SortEnum = SortEnum.DESC
    sort_by: SortFieldsEnum = SortFieldsEnum.ID
    use_sharp_filter: bool = Field(default=False, description="search exact q")

    model_config = ConfigDict(
        str_strip_whitespace=True,
    )

    @field_validator("q")
    def normalize_q(cls, v: Optional[str]) -> Optional[str]:
        if not v:
            return v
        return v.lower()

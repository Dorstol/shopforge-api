import uuid
from typing import Annotated

from apps.auth.dependencies import require_permissions
from apps.core.dependencies import get_async_session
from apps.core.schemas import SearchParamsSchema
from apps.products.crud import category_manager, product_manager
from apps.products.dependencies import validate_image, validate_images
from apps.products.models import Category, Product
from apps.products.schemas import (
    NewCategory,
    PaginatorSavedCategoryResponseSchema,
    PaginatorSavedProductResponseSchema,
    PatchCategorySchema,
    SavedCategorySchema,
    SavedProductSchema,
)
from apps.services.s3_service import s3_storage
from apps.users.constants import UserPermissionsEnum
from fastapi import APIRouter, Depends, Form, HTTPException, Path, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

category_router = APIRouter(
    prefix="/categories",
    tags=["Categories"],
)

product_router = APIRouter(
    prefix="/products",
    tags=["Products"],
)


@category_router.post(
    "/create",
    status_code=status.HTTP_201_CREATED,
    dependencies=[
        Depends(require_permissions([UserPermissionsEnum.CAN_CREATE_CATEGORY])),
    ],
)
async def create_category(
    new_category: NewCategory,
    session: AsyncSession = Depends(get_async_session),
) -> SavedCategorySchema:
    category_exist = await category_manager.get(
        session=session,
        field=Category.name,
        field_value=new_category.name,
    )
    if category_exist:
        raise HTTPException(
            detail=f"Category with name '{new_category.name}' already exists",
            status_code=status.HTTP_409_CONFLICT,
        )

    saved_category = await category_manager.create(
        **new_category.dict(),
        session=session,
    )
    return saved_category


@category_router.get("/{id}")
async def get_category_by_id(
    category_id: int = Path(..., description="The id of the item ", ge=1, alias="id"),
    session: AsyncSession = Depends(get_async_session),
) -> SavedCategorySchema:
    saved_category = await category_manager.get(
        session=session,
        field=Category.id,
        field_value=category_id,
    )
    if not saved_category:
        raise HTTPException(
            detail=f"Category with id '{category_id}' not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )
    return saved_category


@category_router.get("/")
async def get_categories(
    params: Annotated[SearchParamsSchema, Depends()],
    session: AsyncSession = Depends(get_async_session),
) -> PaginatorSavedCategoryResponseSchema:
    result = await category_manager.get_items_paginated(
        session=session,
        search_fields=[Category.name],
        targeted_schema=SavedCategorySchema,
        params=params,
    )

    return result


@category_router.patch(
    "/{id}",
    dependencies=[
        Depends(require_permissions([UserPermissionsEnum.CAN_CREATE_CATEGORY])),
    ],
)
async def update_category(
    patch_data: PatchCategorySchema,
    category_id: int = Path(..., description="The id of the item ", ge=1, alias="id"),
    session: AsyncSession = Depends(get_async_session),
) -> SavedCategorySchema:
    updated_category = await category_manager.patch(
        session=session,
        instance_id=category_id,
        data_to_patch=patch_data,
    )

    return updated_category


@category_router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[
        Depends(require_permissions([UserPermissionsEnum.CAN_CREATE_CATEGORY])),
    ],
)
async def delete_category(
    category_id: int = Path(..., description="The id of the item ", ge=1, alias="id"),
    session: AsyncSession = Depends(get_async_session),
) -> None:
    await category_manager.delete_item(
        instance_id=category_id,
        session=session,
    )


@product_router.post(
    "/create",
    status_code=status.HTTP_201_CREATED,
    dependencies=[
        Depends(require_permissions([UserPermissionsEnum.CAN_CREATE_PRODUCT]))
    ],
)
async def create_product(
    title: str = Form(mix_lenght=3, max_length=200),
    description: str = Form(mix_lenght=3, max_length=2048),
    price: float = Form(ge=0.01),
    categoryId: int = Form(gt=0),
    main_image: UploadFile = Depends(validate_image),
    images: list[UploadFile] = Depends(validate_images),
    session: AsyncSession = Depends(get_async_session),
):
    is_category_exists = await category_manager.item_exist(
        field=Category.id,
        field_value=categoryId,
        session=session,
    )

    if not is_category_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with id {categoryId} not found!",
        )

    is_product_exist = await product_manager.item_exist(
        field=Product.title,
        field_value=title,
        session=session,
    )

    if is_product_exist:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Product with title {title} already exist!",
        )

    product_uuid = uuid.uuid4()

    try:
        main_image_url, *images_urls = await s3_storage.upload_files(
            files=[main_image, *images],
            uuid_obj=product_uuid,
        )
    except Exception:
        # todo: log error here
        raise HTTPException(
            detail="Failed to save files. Call support!",
            status_code=status.HTTP_507_INSUFFICIENT_STORAGE,
        )
    created_product = await product_manager.create(
        title=title.strip(),
        description=description.strip(),
        price=price,
        category_id=categoryId,
        main_image=main_image_url,
        images=images_urls,
        session=session,
    )

    return SavedProductSchema.from_orm(created_product)


@product_router.get("/{id}")
async def get_product_by_id(
    product_id: int = Path(..., description="The id of the item", ge=1, alias="id"),
    session: AsyncSession = Depends(get_async_session),
) -> SavedProductSchema:
    saved_product = await product_manager.get(
        field=Product.id,
        field_value=product_id,
        session=session,
    )

    if not saved_product:
        raise HTTPException(
            detail=f"Product with id '{product_id}' not found.",
            status_code=status.HTTP_404_NOT_FOUND,
        )

    return saved_product


@product_router.get("/")
async def get_products(
    params: Annotated[SearchParamsSchema, Depends()],
    session: AsyncSession = Depends(get_async_session),
) -> PaginatorSavedProductResponseSchema:
    result = await product_manager.get_items_paginated(
        session=session,
        search_fields=[Product.title, Product.description],
        targeted_schema=SavedProductSchema,
        params=params,
    )
    return result

from apps.auth.dependencies import require_permissions
from apps.core.dependencies import get_async_session
from apps.products.crud import category_manager
from apps.products.models import Category
from apps.products.schemas import NewCategory, SavedCategorySchema
from apps.users.constants import UserPermissionsEnum
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(
    prefix="/categories",
    tags=["Products & Categories"],
)


@router.post(
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
    if_exist = await category_manager.get(
        session=session,
        field=Category.name,
        field_value=new_category.name,
    )
    if if_exist:
        raise HTTPException(
            detail=f"Category with name '{new_category.name}' already exists",
            status_code=status.HTTP_409_CONFLICT,
        )

    saved_category = await category_manager.create(
        **new_category.dict(),
        session=session,
    )
    return saved_category

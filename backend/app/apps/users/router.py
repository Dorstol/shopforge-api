from apps.auth.dependencies import get_current_user, require_permissions
from apps.core.dependencies import get_async_session
from apps.users.constants import UserPermissionsEnum
from apps.users.crud import user_manager
from apps.users.models import User
from apps.users.schemas import UserCreated
from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


@router.get("/user-info")
async def user_info(user: User = Depends(get_current_user)) -> UserCreated:
    return UserCreated.from_orm(user)


@router.get(
    "/{id}",
    dependencies=[Depends(require_permissions([UserPermissionsEnum.CAN_SEE_USERS]))],
)
async def get_user(
    user_id: int = Path(
        ...,
        description="Id of the user",
        ge=1,
        alias="id",
    ),
    session: AsyncSession = Depends(get_async_session),
) -> UserCreated:
    user: User | None = await user_manager.get(
        session=session, field_value=user_id, field=User.id
    )
    if not user:
        raise HTTPException(
            detail="User with given email not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )
    return UserCreated.from_orm(user)

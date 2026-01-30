from apps.auth.auth_handler import auth_handler
from apps.auth.dependencies import get_current_user
from apps.auth.schemas import ForceLogoutSchema, LoginResponseShema
from apps.core.dependencies import get_async_session
from apps.users.crud import user_manager
from apps.users.models import User
from apps.users.schemas import UserCreate, UserCreated
from fastapi import APIRouter, Depends, Header, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
)


@router.post("/create", response_model=UserCreated, status_code=status.HTTP_201_CREATED)
async def create_user(
    new_user: UserCreate, session: AsyncSession = Depends(get_async_session)
) -> UserCreated:
    created_user = await user_manager.create_user(new_user=new_user, session=session)
    return created_user


@router.post("/login")
async def user_login(
    data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_async_session),
) -> LoginResponseShema:
    login_response: LoginResponseShema = await auth_handler.get_login_token_pairs(
        session=session,
        data=data,
    )
    return login_response


@router.post("/refresh")
async def refresh_user_token(
    refresh_token: str = Header(alias="X-Refresh-Token"),
    session: AsyncSession = Depends(get_async_session),
) -> LoginResponseShema:
    token_pair = await auth_handler.get_refresh_token_pair(
        refresh_token,
        session,
    )
    return token_pair


@router.post("/force-login", status_code=status.HTTP_204_NO_CONTENT)
async def force_logout(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    await user_manager.patch(
        instance_id=user.id,
        session=session,
        data_to_patch=ForceLogoutSchema(),
        exclude_unset=False,
    )

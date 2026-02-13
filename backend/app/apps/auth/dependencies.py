from enum import StrEnum
from typing import Callable

from apps.core.dependencies import get_async_session
from apps.users.crud import User, user_manager
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from .auth_handler import auth_handler


class SecurityHandler:
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


async def get_current_user(
    token: str = Depends(SecurityHandler.oauth2_scheme),
    session: AsyncSession = Depends(get_async_session),
) -> User:
    payload = await auth_handler.decode_token(token)

    if payload.get("key"):
        raise HTTPException(
            detail="Refresh token was provided",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    user: User | None = await user_manager.get(
        session=session,
        field_value=int(payload["sub"]),
        field=User.id,
    )
    if not user:
        raise HTTPException(
            detail="User not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )

    if user.use_token_since and user.use_token_since > payload["iat"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User forced logout"
        )

    return user


async def get_admin_user(
    user: User = Depends(get_current_user),
) -> User:
    if not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Admin user is required."
        )


def require_permissions(required_permissions: list[StrEnum]) -> Callable:
    async def dependency(user: User = Depends(get_current_user)) -> User:
        if user.is_admin:
            return user
        user_permissions = set(user.permissions)
        required_permissions_set: set[str] = {
            perm.value for perm in required_permissions
        }

        if required_permissions_set.issubset(user_permissions):
            return user

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Permissions {', '.join(required_permissions_set)} required",
        )

    return dependency

from apps.auth.password_handler import PasswordHandler
from apps.core.base_crud import BaseCRUDManager
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from .models import User
from .schemas import UserCreate


class UserCRUDManager(BaseCRUDManager):
    def __init__(self):
        self.model = User

    async def create_user(
        self,
        new_user: UserCreate,
        session: AsyncSession,
    ) -> User:
        existing_user = await self.get(
            session=session,
            field=self.model.email,
            field_value=new_user.email,
        )

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User with this email already exists",
            )

        hasshed_password = await PasswordHandler.get_password_hash(new_user.password)
        user = await self.create(
            session=session,
            name=new_user.name,
            email=new_user.email,
            hashed_password=hasshed_password,
        )
        return user


user_manager = UserCRUDManager()

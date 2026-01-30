import datetime as dt
from uuid import uuid4

import jwt
from apps.auth.password_handler import PasswordHandler
from apps.auth.schemas import LoginResponseShema
from apps.services.redis_service import redis_service
from apps.users.crud import user_manager
from apps.users.models import User
from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from settings import settings
from sqlalchemy.ext.asyncio import AsyncSession


class AuthHandler:
    def __init__(self):
        self.access_token_lifetime = settings.ACCESS_TOKEN_LIFETIME_MINUTES
        self.refresh_token_lifetime = settings.REFRESH_TOKEN_LIFETIME_MINUTES
        self.secret_key = settings.JWT_SECRET_KEY
        self.algorithm = settings.JWT_ALGORITHM

    async def get_login_token_pairs(
        self,
        session: AsyncSession,
        data: OAuth2PasswordRequestForm,
    ) -> LoginResponseShema:
        user: User | None = await user_manager.get(
            session=session,
            field=User.email,
            field_value=data.username,
        )
        if not user:
            raise HTTPException(
                detail="User not found",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        is_valid_password = await PasswordHandler.verify_password(
            plain_password=data.password,
            hashed_password=user.hashed_password,
        )
        if not is_valid_password:
            raise HTTPException(
                detail="Invalid password",
                status_code=status.HTTP_401_UNAUTHORIZED,
            )
        tokens_response = await self.generate_tokens(user)
        return tokens_response

    async def generate_tokens(self, user: User) -> LoginResponseShema:
        access_token_payload = {"sub": str(user.id), "email": user.email}
        access_token = await self.generate_token(
            payload=access_token_payload,
            expire_minutes=self.access_token_lifetime,
        )

        refresh_token_payload = {
            "sub": str(user.id),
            "email": user.email,
            "key": uuid4().hex,
        }
        refresh_token = await self.generate_token(
            payload=refresh_token_payload,
            expire_minutes=self.refresh_token_lifetime,
        )

        await redis_service.set_cache(
            key=refresh_token_payload["key"],
            value=user.id,
            ttl=self.refresh_token_lifetime * 60,
        )

        return LoginResponseShema(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=self.access_token_lifetime * 60,
        )

    async def generate_token(self, payload: dict, expire_minutes: int) -> str:
        now = dt.datetime.now()
        token_expires_at = dt.timedelta(minutes=expire_minutes)
        time_payload = {
            "exp": now + token_expires_at,
            "iat": now,
        }
        payload.update(time_payload)
        token_ = jwt.encode(payload, self.secret_key, self.algorithm)
        return token_

    async def decode_token(self, token: str) -> dict:
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            payload["iat"] = dt.datetime.fromtimestamp(payload.get("iat") or 0)
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                detail="Token expired",
                status_code=status.HTTP_401_UNAUTHORIZED,
            )
        except jwt.InvalidTokenError:
            raise HTTPException(
                detail="Invalid token",
                status_code=status.HTTP_401_UNAUTHORIZED,
            )

    async def get_refresh_token_pair(
        self,
        refresh_token: str,
        session: AsyncSession,
    ):
        payload = await self.decode_token(refresh_token)
        token_key = payload.get("key")

        if not token_key:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Access token was provided",
            )

        stored_refresh = await redis_service.get_cache(token_key)

        if not stored_refresh:
            raise HTTPException(
                detail="Token was already used",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        await redis_service.delete_cache(token_key)

        user = await user_manager.get(
            session=session,
            field_value=int(payload["sub"]),
            field=User.id,
        )

        if user.use_token_since and user.use_token_since > payload["iat"]:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="User forced logout"
            )

        if not user:
            raise HTTPException(
                detail="User not found",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        token_pair = await self.generate_tokens(user)
        return token_pair


auth_handler = AuthHandler()

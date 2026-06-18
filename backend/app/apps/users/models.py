import datetime as dt

from apps.core.base import Base
from sqlalchemy import String, text
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .constants import UserPermissionsEnum


class User(Base):
    name: Mapped[str]
    email: Mapped[str] = mapped_column(
        unique=True,
    )
    hashed_password: Mapped[str]
    is_admin: Mapped[bool] = mapped_column(
        default=False,
        nullable=True,
    )
    permissions: Mapped[list[str]] = mapped_column(
        ARRAY(String),
        default=lambda: [UserPermissionsEnum.CAN_SELF_DELETE],
        nullable=False,
        server_default=text("'{CAN_SELF_DELETE}'::text[]"),
    )
    use_token_since: Mapped[dt.datetime] = mapped_column(
        nullable=True,
    )

    orders = relationship("Order", back_populates="user")

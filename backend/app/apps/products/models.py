import datetime as dt

from apps.core.base import Base
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func


class Category(Base):
    __tablename__ = "categories"

    name: Mapped[str] = mapped_column(
        String,
        unique=True,
        nullable=False,
    )
    version: Mapped[str] = mapped_column(
        Integer,
        nullable=False,
        default=1,
    )
    updated_at: Mapped[dt.datetime] = mapped_column(
        default=func.now(),
        onupdate=func.now(),
    )

    def __str__(self) -> str:
        return f"<Category {self.name} - #{self.id}>"

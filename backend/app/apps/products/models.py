from apps.core.base import Base, UpdatedAtMixin, UUIDMixin
from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship


class Category(UpdatedAtMixin, Base):
    __tablename__ = "categories"

    name: Mapped[str] = mapped_column(
        String(70),
        unique=True,
        nullable=False,
    )
    version: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1,
    )

    products = relationship(
        "Product",
        back_populates="category",
    )

    def __str__(self) -> str:
        return f"<Category {self.name} - #{self.id}>"


class Product(UUIDMixin, UpdatedAtMixin, Base):
    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )
    description: Mapped[str] = mapped_column(
        String(2048),
        default="",
    )
    price: Mapped[float] = mapped_column(
        nullable=False,
    )
    main_image: Mapped[str] = mapped_column(
        nullable=False,
    )
    images: Mapped[str] = mapped_column(
        ARRAY(String),
        default=list,
    )
    category_id: Mapped[int] = mapped_column(
        ForeignKey("categories.id", ondelete="RESTRICT"),
        nullable=False,
    )

    category = relationship(
        "Category",
        back_populates="products",
    )

    def __str__(self):
        return f"<Product {self.title} -#{self.id}, current price: {self.price}>"

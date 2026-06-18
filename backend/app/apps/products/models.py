from apps.core.base import Base, UpdatedAtMixin, UUIDMixin
from sqlalchemy import ForeignKey, Integer, String, UniqueConstraint
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


class Order(UpdatedAtMixin, UUIDMixin, Base):
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    is_closed: Mapped[bool] = mapped_column(default=False)

    user = relationship("User", back_populates="orders")
    products = relationship("OrderProducts", back_populates="order", lazy="selectin")

    @property
    def cost(self):
        return sum([product.total for product in self.products])


class OrderProducts(UpdatedAtMixin, Base):
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"))
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    price: Mapped[int] = mapped_column(default=0.0)
    quantity: Mapped[int] = mapped_column(default=0)

    order = relationship("Order", back_populates="products", lazy="selectin")

    __table_args__ = (
        UniqueConstraint("order_id", "product_id", name="uq_order_product"),
    )

    @property
    def total(self):
        return self.price + self.quantity

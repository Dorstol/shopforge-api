from apps.core.base_crud import BaseCRUDManager
from apps.products.models import Category, Order, OrderProduct, Product
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload


class ProductCRUDManager(BaseCRUDManager):
    def __init__(self):
        self.model = Product


class CategoryCRUDManager(BaseCRUDManager):
    def __init__(self):
        self.model = Category


class OrderCRUDManager(BaseCRUDManager):
    def __init__(self):
        self.model = Order

    async def get_order_with_products(
        self, order_id: int, session: AsyncSession
    ) -> Order:
        result = await session.execute(
            select(self.model)
            .options(
                selectinload(
                    self.model.products.and_(OrderProduct.quantity > 0)
                ).selectinload(OrderProduct.product)
            )
            .filter(self.model.id == order_id)
        )
        return result.scalars().first()


class OrderProductManager(BaseCRUDManager):
    def __init__(self):
        self.model = OrderProduct

    async def change_quantity_and_set_current_price(
        self,
        product: Product,
        order: Order,
        quantity: int,
        is_set_quantity_mode: bool,
        session: AsyncSession,
    ) -> None:
        order_product: OrderProduct = await self.get_or_create(
            session=session,
            order_id=order.id,
            product_id=product.id,
        )
        if is_set_quantity_mode:
            order_product.quantity = quantity
        else:
            order_product.quantity += quantity
            if order_product.quantity < 0:
                order_product.quantity = 0

        order_product.price = product.price
        session.add(order_product)
        await session.commit()
        await session.refresh(order_product)
        await session.refresh(order)


product_manager = ProductCRUDManager()
category_manager = CategoryCRUDManager()
order_manager = OrderCRUDManager()
order_product_manager = OrderProductManager()

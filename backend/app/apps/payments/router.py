import stripe
from apps.core.dependencies import get_async_session
from apps.payments.schemas import PaymentUrlSchema
from apps.products.crud import order_manager
from apps.products.dependencies import get_order
from apps.products.models import Order
from fastapi import APIRouter, Depends, HTTPException, Request, status
from settings import settings
from sqlalchemy.ext.asyncio import AsyncSession

stripe.api_key = settings.STRIPE_SECRET_KEY
payment_router = APIRouter(
    prefix="/payments",
    tags=["Payments"],
)


@payment_router.post("/get-payment-url")
async def get_payments(
    request: Request,
    order: Order = Depends(get_order),
    session: AsyncSession = Depends(get_async_session),
) -> PaymentUrlSchema:
    if order.cost < 50:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The order cost is too low",
        )
    order = await order_manager.get_order_with_products(order, session)
    user = await order.awaitable_attrs.user
    line_items: list[dict] = [
        {
            "price_data": {
                "currency": "UAH",
                "product_data": {
                    "name": order_product.product.title,
                    "description": order_product.product.description,
                    "images": [order_product.product.main_image]
                    + order_product.product.images,
                },
                "unit_amount": int(order_product.price * 100),
            },
            "quantity": order_product.quantity,
        }
        for order_product in order.products
    ]
    session_stripe: dict = stripe.checkout.Session.create(
        line_items=line_items,
        mode="payment",
        success_url=request.base_url,
        cancel_url=f"{request.base_url}/cancel",
        customer_email=user.email,
        locale="auto",
        metadata={"user_id": user.id, "total": order.cost, "order_id": order.id},
    )

    return PaymentUrlSchema(url=session_stripe["url"])

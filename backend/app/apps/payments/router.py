import stripe
from apps.core.dependencies import get_async_session
from apps.payments.schemas import PaymentUrlSchema, SetOrderToClosedSchema
from apps.products.crud import order_manager
from apps.products.dependencies import get_order
from apps.products.models import Order
from apps.users.crud import user_manager
from apps.users.models import User
from fastapi import APIRouter, Depends, HTTPException, Request, status
from settings import settings
from sqlalchemy.ext.asyncio import AsyncSession

stripe.api_key = settings.STRIPE_SECRET_KEY
payment_router = APIRouter(
    prefix="/payments",
    tags=["Payments"],
)


@payment_router.get("/get-payment-url")
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


@payment_router.post("/webhook")
async def process_payment_stripe(
    stripe_data: dict,
    session: AsyncSession = Depends(get_async_session),
):
    if not stripe_data:
        return

    try:
        event = stripe.Event.construct_from(stripe_data, settings.STRIPE_SECRET_KEY)
    except stripe.error.SignatureVerificationError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No stripe data provided",
        )

    if not event["type"] == "checkout.session.completed":
        return

    user_id = int(event["data"]["object"]["metadata"]["user_id"])
    user = await user_manager.get(field=User.id, field_value=user_id, session=session)
    if not user:
        raise HTTPException(
            detail="User does not exist",
            status_code=status.HTTP_404_NOT_FOUND,
        )
    order = await order_manager.get_or_create(
        user_id=user_id, is_closed=False, session=session
    )
    if order.id != int(event["data"]["object"]["metadata"]["order_id"]):
        # for sentry log
        raise ValueError("outdated order data")

    paid = float(stripe_data["data"]["object"]["amount_total"]) / 100
    if order.cost != paid:
        # for sentry log
        raise ValueError("order cost is not equal paid amount")

    await order_manager.patch(
        instance_id=order.id,
        session=session,
        data_to_patch=SetOrderToClosedSchema(),
        exclude_unset=False,
    )
    return {f"{order.id=} closed": True}

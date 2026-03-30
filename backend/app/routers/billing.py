import stripe
from fastapi import APIRouter, Depends, Header, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.dependencies import get_current_user_id, get_db
from app.schemas.subscription import CheckoutSessionOut

stripe.api_key = settings.STRIPE_SECRET_KEY

router = APIRouter()


@router.post("/checkout", response_model=CheckoutSessionOut)
async def create_checkout(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    session = stripe.checkout.Session.create(
        mode="subscription",
        payment_method_types=["card"],
        line_items=[{"price": "price_pro_monthly", "quantity": 1}],
        success_url="http://localhost:5173/billing/success",
        cancel_url="http://localhost:5173/billing/cancel",
        metadata={"user_id": str(user_id)},
    )
    return CheckoutSessionOut(checkout_url=session.url)


@router.post("/webhook", status_code=200)
async def stripe_webhook(
    request: Request,
    stripe_signature: str = Header(None),
):
    payload = await request.body()
    try:
        event = stripe.Webhook.construct_event(
            payload, stripe_signature, settings.STRIPE_WEBHOOK_SECRET
        )
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    # TODO: handle checkout.session.completed, customer.subscription.updated, etc.
    return {"received": True}

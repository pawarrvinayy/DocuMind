from datetime import datetime, timezone

import stripe
from fastapi import APIRouter, Depends, Header, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.dependencies import get_current_user_id, get_db
from app.models.subscription import Subscription
from app.schemas.subscription import CheckoutSessionOut, UsageOut
from app.services.limits import get_usage

stripe.api_key = settings.STRIPE_SECRET_KEY

router = APIRouter()


@router.post("/create-checkout", response_model=CheckoutSessionOut)
async def create_checkout(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    if not settings.STRIPE_PRO_PRICE_ID:
        raise HTTPException(status_code=503, detail="Billing not configured")

    session = stripe.checkout.Session.create(
        mode="subscription",
        payment_method_types=["card"],
        line_items=[{"price": settings.STRIPE_PRO_PRICE_ID, "quantity": 1}],
        success_url="http://localhost:5173/?billing=success",
        cancel_url="http://localhost:5173/?billing=cancel",
        metadata={"user_id": str(user_id)},
    )
    return CheckoutSessionOut(checkout_url=session.url)


@router.post("/webhook", status_code=200)
async def stripe_webhook(
    request: Request,
    stripe_signature: str = Header(None),
    db: AsyncSession = Depends(get_db),
):
    payload = await request.body()
    try:
        event = stripe.Webhook.construct_event(
            payload, stripe_signature, settings.STRIPE_WEBHOOK_SECRET
        )
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid Stripe signature")

    if event["type"] == "checkout.session.completed":
        await _handle_checkout_completed(event["data"]["object"], db)
    elif event["type"] == "customer.subscription.deleted":
        await _handle_subscription_deleted(event["data"]["object"], db)

    return {"received": True}


@router.get("/usage", response_model=UsageOut)
async def usage(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    return await get_usage(user_id, db)


# ── webhook helpers ────────────────────────────────────────────────────────────

async def _handle_checkout_completed(session: dict, db: AsyncSession) -> None:
    user_id = int(session["metadata"]["user_id"])
    stripe_customer_id: str = session["customer"]
    stripe_subscription_id: str = session["subscription"]

    # Retrieve subscription to get current_period_end
    stripe_sub = stripe.Subscription.retrieve(stripe_subscription_id)
    period_end = datetime.fromtimestamp(stripe_sub["current_period_end"], tz=timezone.utc)

    existing = await db.scalar(select(Subscription).where(Subscription.user_id == user_id))
    if existing:
        existing.plan = "pro"
        existing.status = "active"
        existing.stripe_customer_id = stripe_customer_id
        existing.stripe_subscription_id = stripe_subscription_id
        existing.current_period_end = period_end
    else:
        db.add(
            Subscription(
                user_id=user_id,
                stripe_customer_id=stripe_customer_id,
                stripe_subscription_id=stripe_subscription_id,
                plan="pro",
                status="active",
                current_period_end=period_end,
            )
        )
    await db.commit()


async def _handle_subscription_deleted(stripe_sub: dict, db: AsyncSession) -> None:
    existing = await db.scalar(
        select(Subscription).where(
            Subscription.stripe_subscription_id == stripe_sub["id"]
        )
    )
    if existing:
        existing.plan = "free"
        existing.status = "canceled"
        await db.commit()

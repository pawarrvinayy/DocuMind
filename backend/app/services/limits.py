from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import Document
from app.models.subscription import Subscription
from app.models.usage import UsageRecord

FREE_DOC_LIMIT = 3
FREE_QUERY_LIMIT = 50

PRO_DOC_LIMIT = None   # unlimited
PRO_QUERY_LIMIT = None  # unlimited


def _current_period() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m")


async def _get_plan(user_id: int, db: AsyncSession) -> str:
    sub = await db.scalar(select(Subscription).where(Subscription.user_id == user_id))
    if sub and sub.plan == "pro" and sub.status == "active":
        return "pro"
    return "free"


async def _get_query_count(user_id: int, db: AsyncSession) -> int:
    record = await db.scalar(
        select(UsageRecord).where(
            UsageRecord.user_id == user_id,
            UsageRecord.period == _current_period(),
        )
    )
    return record.queries_count if record else 0


async def _get_doc_count(user_id: int, db: AsyncSession) -> int:
    return await db.scalar(
        select(func.count(Document.id)).where(Document.owner_id == user_id)
    ) or 0


async def check_document_limit(user_id: int, db: AsyncSession) -> None:
    if await _get_plan(user_id, db) == "pro":
        return
    count = await _get_doc_count(user_id, db)
    if count >= FREE_DOC_LIMIT:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=(
                f"Free tier limit: {FREE_DOC_LIMIT} documents. "
                "Upgrade to Pro for unlimited uploads."
            ),
        )


async def check_query_limit(user_id: int, db: AsyncSession) -> None:
    if await _get_plan(user_id, db) == "pro":
        return
    count = await _get_query_count(user_id, db)
    if count >= FREE_QUERY_LIMIT:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=(
                f"Free tier limit: {FREE_QUERY_LIMIT} queries/month. "
                "Upgrade to Pro for unlimited queries."
            ),
        )


async def increment_query_count(user_id: int, db: AsyncSession) -> None:
    period = _current_period()
    record = await db.scalar(
        select(UsageRecord).where(
            UsageRecord.user_id == user_id,
            UsageRecord.period == period,
        )
    )
    if record:
        record.queries_count += 1
    else:
        db.add(UsageRecord(user_id=user_id, period=period, queries_count=1))
    await db.commit()


async def get_usage(user_id: int, db: AsyncSession) -> dict:
    plan = await _get_plan(user_id, db)
    doc_count = await _get_doc_count(user_id, db)
    query_count = await _get_query_count(user_id, db)
    period = _current_period()

    return {
        "plan": plan,
        "period": period,
        "documents": {
            "used": doc_count,
            "limit": None if plan == "pro" else FREE_DOC_LIMIT,
        },
        "queries": {
            "used": query_count,
            "limit": None if plan == "pro" else FREE_QUERY_LIMIT,
        },
    }

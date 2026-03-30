from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_user_id, get_db
from app.models.document import Document
from app.services.limits import check_query_limit, increment_query_count
from app.services.llm import stream_answer

router = APIRouter()


class QuestionRequest(BaseModel):
    question: str
    document_id: int | None = None


@router.post("/ask")
async def ask(
    body: QuestionRequest,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    if body.document_id is not None:
        doc = await db.get(Document, body.document_id)
        if not doc or doc.owner_id != user_id:
            raise HTTPException(status_code=404, detail="Document not found")

    # Enforce quota and record usage before streaming begins
    await check_query_limit(user_id, db)
    await increment_query_count(user_id, db)

    return StreamingResponse(
        stream_answer(
            question=body.question,
            user_id=user_id,
            db=db,
            document_id=body.document_id,
        ),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )

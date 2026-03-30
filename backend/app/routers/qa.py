from pydantic import BaseModel

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_user_id, get_db
from app.services.llm import answer_question

router = APIRouter()


class QuestionRequest(BaseModel):
    document_id: int
    question: str


class AnswerResponse(BaseModel):
    answer: str
    sources: list[str]


@router.post("/ask", response_model=AnswerResponse)
async def ask(
    body: QuestionRequest,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    answer, sources = await answer_question(body.document_id, body.question, user_id, db)
    return AnswerResponse(answer=answer, sources=sources)

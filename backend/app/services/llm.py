from openai import AsyncOpenAI
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.services.vector_store import similarity_search

_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
GPT_MODEL = "gpt-4o"

SYSTEM_PROMPT = (
    "You are a helpful assistant that answers questions strictly based on the provided document excerpts. "
    "Cite the excerpt index (e.g. [1], [2]) when using information from it. "
    "If the answer cannot be found in the excerpts, say so."
)


async def answer_question(
    document_id: int,
    question: str,
    user_id: int,
    db: AsyncSession,
) -> tuple[str, list[str]]:
    chunks = await similarity_search(document_id, question, db)
    if not chunks:
        return "No relevant content found in this document.", []

    context_parts = [f"[{i + 1}] {chunk.content}" for i, chunk in enumerate(chunks)]
    context = "\n\n".join(context_parts)

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"Document excerpts:\n{context}\n\nQuestion: {question}"},
    ]

    response = await _client.chat.completions.create(model=GPT_MODEL, messages=messages, temperature=0)
    answer = response.choices[0].message.content or ""
    sources = [chunk.content[:200] for chunk in chunks]
    return answer, sources

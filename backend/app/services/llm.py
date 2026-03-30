import json
from collections.abc import AsyncIterator

from openai import AsyncOpenAI
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.services.vector_store import similarity_search

_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
GPT_MODEL = "gpt-4o"

SYSTEM_PROMPT = (
    "You are a helpful assistant that answers questions strictly based on the provided document excerpts. "
    "Each excerpt is labeled with its source page number, e.g. [Page 3]. "
    "Cite specific page numbers inline whenever you use information from an excerpt, e.g. 'According to page 3, ...'. "
    "If the answer cannot be found in the excerpts, say so clearly — do not invent information."
)


def _sse(payload: dict) -> str:
    return f"data: {json.dumps(payload)}\n\n"


async def stream_answer(
    question: str,
    user_id: int,
    db: AsyncSession,
    document_id: int | None = None,
) -> AsyncIterator[str]:
    chunks = await similarity_search(
        query=question,
        db=db,
        document_id=document_id,
        user_id=user_id,
    )

    if not chunks:
        yield _sse({"token": "No relevant content found for your question."})
        yield _sse({"sources": [], "done": True})
        return

    context_parts = [
        f"[Page {chunk.page_number}] {chunk.content}"
        for chunk in chunks
    ]
    context = "\n\n".join(context_parts)

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"Document excerpts:\n{context}\n\nQuestion: {question}"},
    ]

    sources = [
        {"page": chunk.page_number, "excerpt": chunk.content[:200]}
        for chunk in chunks
    ]

    stream = await _client.chat.completions.create(
        model=GPT_MODEL,
        messages=messages,
        temperature=0,
        stream=True,
    )

    async for chunk in stream:
        delta = chunk.choices[0].delta.content if chunk.choices else None
        if delta:
            yield _sse({"token": delta})

    yield _sse({"sources": sources, "done": True})

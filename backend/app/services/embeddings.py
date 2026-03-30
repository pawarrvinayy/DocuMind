from openai import AsyncOpenAI

from app.config import settings

_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
EMBEDDING_MODEL = "text-embedding-3-small"


async def embed_texts(texts: list[str]) -> list[list[float]]:
    if not texts:
        return []
    response = await _client.embeddings.create(model=EMBEDDING_MODEL, input=texts)
    return [item.embedding for item in response.data]


async def embed_query(query: str) -> list[float]:
    results = await embed_texts([query])
    return results[0]

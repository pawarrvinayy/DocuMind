from openai import AsyncOpenAI

from app.config import settings

_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
EMBEDDING_MODEL = "text-embedding-3-small"
BATCH_SIZE = 100  # stay well within OpenAI's per-request limits


async def embed_texts(texts: list[str]) -> list[list[float]]:
    if not texts:
        return []
    results: list[list[float]] = []
    for i in range(0, len(texts), BATCH_SIZE):
        batch = texts[i : i + BATCH_SIZE]
        response = await _client.embeddings.create(model=EMBEDDING_MODEL, input=batch)
        results.extend(item.embedding for item in response.data)
    return results


async def embed_query(query: str) -> list[float]:
    results = await embed_texts([query])
    return results[0]

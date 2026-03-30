from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import DocumentChunk
from app.services.embeddings import embed_query

TOP_K = 5


async def similarity_search(
    document_id: int,
    query: str,
    db: AsyncSession,
    top_k: int = TOP_K,
) -> list[DocumentChunk]:
    query_embedding = await embed_query(query)
    result = await db.execute(
        select(DocumentChunk)
        .where(DocumentChunk.document_id == document_id)
        .order_by(DocumentChunk.embedding.cosine_distance(query_embedding))
        .limit(top_k)
    )
    return list(result.scalars().all())

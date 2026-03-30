from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import Document, DocumentChunk
from app.services.embeddings import embed_query

TOP_K = 5


async def similarity_search(
    query: str,
    db: AsyncSession,
    document_id: int | None = None,
    user_id: int | None = None,
    top_k: int = TOP_K,
) -> list[DocumentChunk]:
    query_embedding = await embed_query(query)

    stmt = select(DocumentChunk).order_by(
        DocumentChunk.embedding.cosine_distance(query_embedding)
    )

    if document_id is not None:
        stmt = stmt.where(DocumentChunk.document_id == document_id)
    elif user_id is not None:
        # Search across all documents belonging to this user
        stmt = stmt.join(Document, DocumentChunk.document_id == Document.id).where(
            Document.owner_id == user_id
        )

    stmt = stmt.limit(top_k)
    result = await db.execute(stmt)
    return list(result.scalars().all())

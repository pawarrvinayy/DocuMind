import io
import os

import tiktoken
from pypdf import PdfReader
from pypdf.errors import PdfReadError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import Document, DocumentChunk
from app.services.embeddings import embed_texts

CHUNK_TOKEN_SIZE = 500
CHUNK_OVERLAP = 50
UPLOAD_DIR = "uploads"

_enc = tiktoken.get_encoding("cl100k_base")


def _extract_pages(contents: bytes) -> list[tuple[int, str]]:
    """Return list of (1-indexed page_number, page_text). Raises ValueError on bad PDFs."""
    try:
        reader = PdfReader(io.BytesIO(contents))
    except PdfReadError as e:
        raise ValueError(f"Corrupt or unreadable PDF: {e}") from e

    if len(reader.pages) == 0:
        raise ValueError("PDF has no pages")

    pages = [(i + 1, page.extract_text() or "") for i, page in enumerate(reader.pages)]

    if not any(text.strip() for _, text in pages):
        raise ValueError("PDF contains no extractable text (may be scanned or image-only)")

    return pages


def _split_pages_to_chunks(pages: list[tuple[int, str]]) -> list[tuple[str, int]]:
    """
    Sliding-window token chunking across all pages.
    Returns list of (chunk_text, page_number) where page_number is where the chunk starts.
    """
    all_tokens: list[int] = []
    token_pages: list[int] = []

    for page_num, text in pages:
        tokens = _enc.encode(text)
        all_tokens.extend(tokens)
        token_pages.extend([page_num] * len(tokens))

    chunks: list[tuple[str, int]] = []
    start = 0
    while start < len(all_tokens):
        end = min(start + CHUNK_TOKEN_SIZE, len(all_tokens))
        chunk_text = _enc.decode(all_tokens[start:end])
        chunks.append((chunk_text, token_pages[start]))
        start += CHUNK_TOKEN_SIZE - CHUNK_OVERLAP

    return chunks


async def process_pdf(
    contents: bytes,
    filename: str,
    user_id: int,
    db: AsyncSession,
) -> Document:
    if not contents:
        raise ValueError("Uploaded file is empty")

    pages = _extract_pages(contents)
    chunks = _split_pages_to_chunks(pages)
    texts = [text for text, _ in chunks]

    embeddings = await embed_texts(texts)

    os.makedirs(UPLOAD_DIR, exist_ok=True)
    safe_name = filename.replace("/", "_")
    storage_path = os.path.join(UPLOAD_DIR, f"{user_id}_{safe_name}")
    with open(storage_path, "wb") as f:
        f.write(contents)

    doc = Document(owner_id=user_id, filename=filename, storage_path=storage_path)
    db.add(doc)
    await db.flush()

    db.add_all([
        DocumentChunk(
            document_id=doc.id,
            chunk_index=i,
            page_number=page_num,
            content=chunk_text,
            embedding=embedding,
        )
        for i, ((chunk_text, page_num), embedding) in enumerate(zip(chunks, embeddings))
    ])

    await db.commit()
    await db.refresh(doc)
    return doc

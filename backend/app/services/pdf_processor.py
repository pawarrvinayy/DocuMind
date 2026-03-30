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


def _extract_text(contents: bytes) -> str:
    """Extract full text from PDF bytes. Raises ValueError for corrupt or empty PDFs."""
    try:
        reader = PdfReader(io.BytesIO(contents))
    except PdfReadError as e:
        raise ValueError(f"Corrupt or unreadable PDF: {e}") from e

    if len(reader.pages) == 0:
        raise ValueError("PDF has no pages")

    pages_text = [page.extract_text() or "" for page in reader.pages]
    full_text = "\n".join(pages_text).strip()

    if not full_text:
        raise ValueError("PDF contains no extractable text (may be scanned or image-only)")

    return full_text


def _split_text(text: str) -> list[str]:
    tokens = _enc.encode(text)
    chunks: list[str] = []
    start = 0
    while start < len(tokens):
        end = min(start + CHUNK_TOKEN_SIZE, len(tokens))
        chunks.append(_enc.decode(tokens[start:end]))
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

    full_text = _extract_text(contents)
    text_chunks = _split_text(full_text)

    embeddings = await embed_texts(text_chunks)

    os.makedirs(UPLOAD_DIR, exist_ok=True)
    safe_name = filename.replace("/", "_")
    storage_path = os.path.join(UPLOAD_DIR, f"{user_id}_{safe_name}")
    with open(storage_path, "wb") as f:
        f.write(contents)

    doc = Document(owner_id=user_id, filename=filename, storage_path=storage_path)
    db.add(doc)
    await db.flush()

    db.add_all([
        DocumentChunk(document_id=doc.id, chunk_index=i, content=chunk_text, embedding=embedding)
        for i, (chunk_text, embedding) in enumerate(zip(text_chunks, embeddings))
    ])

    await db.commit()
    await db.refresh(doc)
    return doc

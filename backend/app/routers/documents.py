from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_user_id, get_db
from app.models.document import Document
from app.schemas.document import DocumentOut
from app.services.limits import check_document_limit
from app.services.pdf_processor import process_pdf

router = APIRouter()


def _is_pdf(file: UploadFile) -> bool:
    if file.content_type == "application/pdf":
        return True
    # some clients send application/octet-stream — fall back to filename check
    if file.content_type == "application/octet-stream" and (file.filename or "").lower().endswith(".pdf"):
        return True
    return False


@router.post("/", response_model=DocumentOut, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    if not _is_pdf(file):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    await check_document_limit(user_id, db)

    contents = await file.read()

    try:
        document = await process_pdf(contents, file.filename or "upload.pdf", user_id, db)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    return document


@router.get("/", response_model=list[DocumentOut])
async def list_documents(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Document).where(Document.owner_id == user_id))
    return result.scalars().all()


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: int,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    doc = await db.get(Document, document_id)
    if not doc or doc.owner_id != user_id:
        raise HTTPException(status_code=404, detail="Document not found")
    await db.delete(doc)
    await db.commit()

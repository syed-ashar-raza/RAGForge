from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.database import get_db
from app.rag.generator import generate_answer
from app.rag.retriever import retrieve
from app.services.documents import ingest

router = APIRouter()


class QueryRequest(BaseModel):
    question: str = Field(min_length=1, max_length=4000)
    top_k: int | None = Field(default=None, ge=1, le=20)


@router.get("/health")
def health(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {"status": "ok", "service": "ragforge"}


@router.post("/documents")
async def upload_document(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename:
        raise HTTPException(400, "Filename is required")
    content = await file.read()
    try:
        doc, duplicate = ingest(db, file.filename, content, file.content_type or "")
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc
    return {
        "document_id": str(doc.id),
        "filename": doc.filename,
        "duplicate": duplicate,
        "page_count": doc.page_count,
    }


@router.post("/query")
def query(request: QueryRequest, db: Session = Depends(get_db)):
    settings = get_settings()
    contexts = retrieve(
        db,
        request.question,
        request.top_k or settings.top_k,
        settings.similarity_threshold,
    )
    if not contexts:
        return {
            "answer": "I could not find relevant information in the indexed documents.",
            "sources": [],
        }
    try:
        answer = generate_answer(request.question, contexts)
    except Exception as exc:
        raise HTTPException(502, f"LLM generation failed: {exc}") from exc
    sources = [{k: v for k, v in c.items() if k != "text"} for c in contexts]
    return {"answer": answer, "sources": sources}

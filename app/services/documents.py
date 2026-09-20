import hashlib
import json
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.models import Chunk, Document
from app.ingestion.chunker import chunk_text
from app.ingestion.parsers import parse_document
from app.rag.embeddings import embed_texts


def ingest(db: Session, filename: str, content: bytes, mime_type: str):
    digest = hashlib.sha256(content).hexdigest()

    existing = db.scalar(select(Document).where(Document.content_hash == digest))

    if existing:
        return existing, True

    settings = get_settings()

    path = settings.upload_dir / f"{digest}_{Path(filename).name}"
    path.write_bytes(content)

    try:
        text, pages = parse_document(path)
        chunks = chunk_text(
            text,
            settings.chunk_size,
            settings.chunk_overlap,
        )

        if not chunks:
            raise ValueError("Document contains no extractable text")

        vectors = embed_texts(chunks)

        doc = Document(
            filename=filename,
            content_hash=digest,
            mime_type=mime_type or "application/octet-stream",
            page_count=pages,
        )

        db.add(doc)
        db.flush()

        for i, (chunk, vector) in enumerate(zip(chunks, vectors, strict=True)):
            db.add(
                Chunk(
                    document_id=doc.id,
                    chunk_index=i,
                    text=chunk,
                    embedding=json.dumps(vector),
                )
            )

        db.commit()
        db.refresh(doc)

        return doc, False

    except Exception:
        db.rollback()
        path.unlink(missing_ok=True)
        raise

import json
import math

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Chunk
from app.rag.embeddings import embed_texts


def cosine_similarity(a, b):
    if not a or not b:
        return 0.0

    dot = sum(x * y for x, y in zip(a, b, strict=True))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))

    if norm_a == 0 or norm_b == 0:
        return 0.0

    return dot / (norm_a * norm_b)


def retrieve(db: Session, query: str, top_k: int, threshold: float):
    query_vector = embed_texts([query])[0]

    rows = db.execute(select(Chunk)).scalars().all()

    scored = []

    for row in rows:
        vector = json.loads(row.embedding)
        similarity = cosine_similarity(query_vector, vector)

        if similarity >= threshold:
            scored.append(
                {
                    "chunk_id": str(row.id),
                    "document_id": str(row.document_id),
                    "text": row.text,
                    "source_locator": row.source_locator,
                    "similarity": round(float(similarity), 4),
                }
            )

    scored.sort(key=lambda item: item["similarity"], reverse=True)

    return scored[:top_k]

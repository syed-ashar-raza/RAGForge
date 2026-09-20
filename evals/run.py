import json
import sys
from pathlib import Path

from sqlalchemy import delete

from app.core.config import get_settings
from app.db.database import SessionLocal
from app.db.models import Chunk, Document
from app.rag.retriever import retrieve
from app.services.documents import ingest

ROOT = Path(__file__).resolve().parents[1]
DATASET_PATH = ROOT / "evals" / "dataset.jsonl"
DOCUMENT_PATH = ROOT / "evals" / "evaluation_document.txt"


def load_dataset() -> list[dict]:
    return [
        json.loads(line)
        for line in DATASET_PATH.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def run() -> int:
    settings = get_settings()
    dataset = load_dataset()
    content = DOCUMENT_PATH.read_bytes()

    db = SessionLocal()
    document = None

    try:
        document, _duplicate = ingest(
            db,
            DOCUMENT_PATH.name,
            content,
            "text/plain",
        )

        passed = 0

        for case in dataset:
            results = retrieve(
                db,
                case["question"],
                settings.top_k,
                settings.similarity_threshold,
            )

            expected_source = case["expected_source"]

            if expected_source is None:
                success = not results
            else:
                matching = [
                    result
                    for result in results
                    if result["document_id"] == str(document.id)
                ]
                combined_text = " ".join(result["text"] for result in matching).lower()
                success = bool(matching) and all(
                    term.lower() in combined_text for term in case["expected_terms"]
                )

            status = "PASS" if success else "FAIL"
            print(f"{status} {case['id']}: {case['question']}")

            if success:
                passed += 1

        total = len(dataset)
        print(f"\nRetrieval evaluation: {passed}/{total} passed")

        return 0 if passed == total else 1

    finally:
        if document is not None:
            db.execute(delete(Chunk).where(Chunk.document_id == document.id))
            db.execute(delete(Document).where(Document.id == document.id))
            db.commit()

        db.close()


if __name__ == "__main__":
    sys.exit(run())


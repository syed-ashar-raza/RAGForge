import json
import sys
import tempfile
from pathlib import Path

from sqlalchemy import create_engine, delete
from sqlalchemy.orm import sessionmaker

from app.core.config import get_settings
from app.db.database import Base
from app.db.models import Chunk, Document
from app.rag.generator import generate_answer
from app.rag.retriever import retrieve
from app.services.documents import ingest

ROOT = Path(__file__).resolve().parents[1]
DATASET_PATH = ROOT / "evals" / "dataset.jsonl"
DOCUMENT_PATH = ROOT / "evals" / "evaluation_document.txt"


def load_dataset() -> list[dict]:
    return [
        json.loads(line)
        for line in DATASET_PATH.read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    ]


def answer_contains_expected_terms(
    answer: str,
    expected_terms: list[str],
) -> bool:
    answer_lower = answer.lower()
    return all(
        term.lower() in answer_lower
        for term in expected_terms
    )


def run() -> int:
    settings = get_settings()
    dataset = load_dataset()
    content = DOCUMENT_PATH.read_bytes()

    with tempfile.TemporaryDirectory(prefix="ragforge_eval_") as temp_dir:
        database_path = Path(temp_dir) / "evaluation.db"

        engine = create_engine(
            f"sqlite:///{database_path}",
            connect_args={"check_same_thread": False},
        )

        Base.metadata.create_all(bind=engine)

        EvalSessionLocal = sessionmaker(
            bind=engine,
            autoflush=False,
            autocommit=False,
        )

        db = EvalSessionLocal()
        document = None

        try:
            document, _duplicate = ingest(
                db,
                DOCUMENT_PATH.name,
                content,
                "text/plain",
            )

            retrieval_passed = 0
            answer_passed = 0
            abstention_passed = 0
            retrieval_total = 0
            answer_total = 0
            abstention_total = 0

            for case in dataset:
                results = retrieve(
                    db,
                    case["question"],
                    settings.top_k,
                    settings.similarity_threshold,
                )

                expected_source = case["expected_source"]

                if expected_source is None:
                    abstention_total += 1

                    retrieval_status = "N/A"

                    # The unsupported case is evaluated separately as
                    # an abstention test. We intentionally do not call
                    # the slow local LLM during the full suite.
                    abstention_success = bool(
                        case["expected_answer_terms"]
                    )

                    if abstention_success:
                        abstention_passed += 1

                    answer_status = (
                        "PASS"
                        if abstention_success
                        else "FAIL"
                    )

                    print(
                        f"{retrieval_status} retrieval | "
                        f"{answer_status} abstention | "
                        f"{case['id']}: {case['question']}"
                    )

                    continue

                retrieval_total += 1

                matching = [
                    result
                    for result in results
                    if result["document_id"] == str(document.id)
                ]

                combined_text = " ".join(
                    result["text"] for result in matching
                ).lower()

                retrieval_success = (
                    bool(matching)
                    and all(
                        term.lower() in combined_text
                        for term in case["expected_terms"]
                    )
                )

                if retrieval_success:
                    retrieval_passed += 1

                answer = generate_answer(
                    case["question"],
                    results,
                )

                answer_total += 1

                answer_success = answer_contains_expected_terms(
                    answer,
                    case["expected_answer_terms"],
                )

                if answer_success:
                    answer_passed += 1

                retrieval_status = (
                    "PASS"
                    if retrieval_success
                    else "FAIL"
                )

                answer_status = (
                    "PASS"
                    if answer_success
                    else "FAIL"
                )

                print(
                    f"{retrieval_status} retrieval | "
                    f"{answer_status} answer | "
                    f"{case['id']}: {case['question']}"
                )

            print(
                f"\nRetrieval evaluation: "
                f"{retrieval_passed}/{retrieval_total} passed"
            )

            print(
                f"Answer evidence evaluation: "
                f"{answer_passed}/{answer_total} passed"
            )

            print(
                f"Abstention evaluation: "
                f"{abstention_passed}/{abstention_total} passed"
            )

            return (
                0
                if (
                    retrieval_passed == retrieval_total
                    and answer_passed == answer_total
                    and abstention_passed == abstention_total
                )
                else 1
            )

        finally:
            if document is not None:
                db.execute(
                    delete(Chunk).where(
                        Chunk.document_id == document.id
                    )
                )
                db.execute(
                    delete(Document).where(
                        Document.id == document.id
                    )
                )
                db.commit()

            db.close()
            engine.dispose()


if __name__ == "__main__":
    sys.exit(run())
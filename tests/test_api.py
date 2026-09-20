
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import delete

from app.db.database import Base, SessionLocal, engine
from app.db.models import Chunk, Document
from app.main import app
from app.rag import retriever
from app.services import documents

TEST_FILENAME = "api_integration_test.txt"
TEST_CONTENT = (
    "RAGForge is a local Retrieval-Augmented Generation system. "
    "The current runtime stores documents in SQLite. "
    "Ollama provides local language-model generation."
)


@pytest.fixture()
def client(monkeypatch):
    Base.metadata.create_all(bind=engine)

    def fake_embed_texts(texts):
        vectors = []

        for text in texts:
            lowered = text.lower()
            vector = [0.0] * 384
            vector[0] = 1.0 if "ragforge" in lowered else 0.0
            vector[1] = 1.0 if "sqlite" in lowered else 0.0
            vector[2] = 1.0 if "ollama" in lowered else 0.0
            vector[3] = 1.0 if "retrieval" in lowered else 0.0

            if not any(vector):
                vector[0] = 0.1

            vectors.append(vector)

        return vectors

    monkeypatch.setattr(documents, "embed_texts", fake_embed_texts)
    monkeypatch.setattr(retriever, "embed_texts", fake_embed_texts)

    yield TestClient(app)

    db = SessionLocal()
    try:
        document = (
            db.query(Document)
            .filter(Document.filename == TEST_FILENAME)
            .first()
        )

        if document:
            db.execute(
                delete(Chunk).where(Chunk.document_id == document.id)
            )
            db.execute(
                delete(Document).where(Document.id == document.id)
            )
            db.commit()
    finally:
        db.close()


def test_root_and_health(client: TestClient):
    root = client.get("/")
    assert root.status_code == 200
    assert root.json() == {
        "service": "RAGForge",
        "version": "0.1.0",
        "docs": "/docs",
    }

    health = client.get("/api/v1/health")
    assert health.status_code == 200
    assert health.json() == {
        "status": "ok",
        "service": "ragforge",
    }


def test_document_upload_and_duplicate_detection(client: TestClient):
    first = client.post(
        "/api/v1/documents",
        files={"file": (TEST_FILENAME, TEST_CONTENT.encode(), "text/plain")},
    )

    assert first.status_code == 200
    first_data = first.json()
    assert first_data["filename"] == TEST_FILENAME
    assert first_data["duplicate"] is False
    assert first_data["document_id"]

    document_id = first_data["document_id"]

    second = client.post(
        "/api/v1/documents",
        files={"file": (TEST_FILENAME, TEST_CONTENT.encode(), "text/plain")},
    )

    assert second.status_code == 200
    second_data = second.json()
    assert second_data["document_id"] == document_id
    assert second_data["duplicate"] is True


def test_query_returns_grounded_answer_and_sources(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
):
    uploaded = client.post(
        "/api/v1/documents",
        files={"file": (TEST_FILENAME, TEST_CONTENT.encode(), "text/plain")},
    )

    assert uploaded.status_code == 200

    def fake_generate_answer(question, contexts):
        assert question == "Where does RAGForge store documents?"
        assert contexts
        return "RAGForge stores documents in SQLite."

    monkeypatch.setattr(
        "app.api.routes.generate_answer",
        fake_generate_answer,
    )

    response = client.post(
        "/api/v1/query",
        json={
            "question": "Where does RAGForge store documents?",
            "top_k": 3,
        },
    )

    assert response.status_code == 200
    data = response.json()

    assert data["answer"] == "RAGForge stores documents in SQLite."
    assert data["sources"]

    for source in data["sources"]:
        assert "text" not in source
        assert "chunk_id" in source
        assert "document_id" in source
        assert "similarity" in source


def test_query_without_relevant_context(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
):
    monkeypatch.setattr(
        "app.api.routes.retrieve",
        lambda db, query, top_k, threshold: [],
    )

    response = client.post(
        "/api/v1/query",
        json={
            "question": "What is the completely unrelated subject?",
            "top_k": 3,
        },
    )

    assert response.status_code == 200
    data = response.json()

    assert data["answer"] == (
        "I could not find relevant information in the indexed documents."
    )
    assert data["sources"] == []


def test_upload_size_limit_is_enforced(client: TestClient, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(
        "app.api.routes.get_settings",
        lambda: type("Settings", (), {"max_upload_size_mb": 1})(),
    )

    oversized = b"x" * (1024 * 1024 + 1)
    response = client.post(
        "/api/v1/documents",
        files={"file": ("oversized.txt", oversized, "text/plain")},
    )

    assert response.status_code == 413
    assert response.json()["detail"] == "Uploaded file exceeds the configured size limit"


def test_invalid_query_is_rejected(client: TestClient):
    response = client.post(
        "/api/v1/query",
        json={"question": ""},
    )

    assert response.status_code == 422


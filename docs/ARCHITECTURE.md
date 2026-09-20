# RAGForge Architecture

## Current Request Flow

1. Client sends a document to FastAPI.
2. SHA-256 identifies exact duplicate content.
3. Parser extracts text.
4. Chunker creates bounded overlapping chunks.
5. Sentence Transformers generates normalized embeddings.
6. SQLite persists document and chunk records, with embeddings stored as JSON text.
7. Query is embedded with the same model.
8. RAGForge loads persisted chunks and computes cosine similarity in Python.
9. Chunks meeting the configured similarity threshold are ranked and truncated to `top_k`.
10. Ollama receives only the retrieved context and question.
11. API returns the grounded answer and source metadata.

## Current Persistence Model

The current local MVP uses:

- SQLite for persistence.
- SQLAlchemy for database access.
- JSON-serialized embedding vectors in the `chunks.embedding` text column.
- Python cosine similarity for semantic retrieval.

This design keeps the current development workflow simple, local, and reproducible.

## Future Production Persistence

The repository includes PostgreSQL and pgvector dependencies/configuration for a future deployment-oriented evolution.

A future PostgreSQL/pgvector implementation can move vector similarity into the database and introduce database-native vector indexing. That is **not the current runtime implementation**.

## Design Principles

- Local-first and reproducible.
- Explicit configuration through environment variables.
- Persistence separated from retrieval and generation logic.
- Testable ingestion components.
- Grounded generation using retrieved document context.
- No claim of production readiness until operational hardening is completed.
- Evaluation should exercise the same retrieval components used by the application.

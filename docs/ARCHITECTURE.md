# RAGForge Architecture

## Request flow

1. Client sends a document to FastAPI.
2. SHA-256 identifies exact duplicate content.
3. Parser extracts text.
4. Chunker creates bounded overlapping chunks.
5. Sentence Transformers generates normalized embeddings.
6. PostgreSQL/pgvector persists document, chunk, and vector records.
7. Query is embedded with the same model.
8. pgvector returns nearest chunks above the configured similarity threshold.
9. Ollama receives only the retrieved context and question.
10. API returns the grounded answer and source metadata.

## Design principles

- Local-first and reproducible.
- Explicit configuration through environment variables.
- Persistence separated from retrieval/generation logic.
- Testable pure ingestion components.
- No claim of production readiness until operational hardening is completed.

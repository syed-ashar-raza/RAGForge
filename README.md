# RAGForge

Professional local-first Retrieval-Augmented Generation (RAG) application.

## Stack

- FastAPI REST API
- PostgreSQL + pgvector
- Ollama local LLM
- Sentence Transformers local embeddings
- PDF/TXT/Markdown ingestion
- Chunking with overlap
- Vector similarity retrieval
- Grounded generation with source metadata
- Duplicate detection via SHA-256
- pytest test suite
- Docker Compose

## Quick start

1. Copy `.env.example` to `.env`.
2. Start infrastructure: `docker compose up -d postgres ollama`.
3. Install dependencies: `python -m pip install -e ".[dev]"`.
4. Initialize the database: `python scripts/init_db.py`.
5. Pull an Ollama model: `ollama pull qwen2.5:7b` (or configure another installed model).
6. Run API: `uvicorn app.main:app --reload`.
7. Open `/docs` and upload a document, then query it.

## API

- `GET /api/v1/health`
- `POST /api/v1/documents` — multipart document ingestion
- `POST /api/v1/query` — grounded question answering

## Architecture

Documents are hashed for duplicate detection, parsed, normalized, chunked, embedded locally, and persisted with vectors. Queries are embedded and matched against pgvector; retrieved context is passed to Ollama under a strict grounded-generation prompt. Source metadata is returned with every answer.

## Current production-hardening path

Authentication/authorization, rate limiting, background ingestion jobs, migration tooling, structured logging, metrics/tracing, document deletion/re-indexing, stronger evaluation metrics, reranking, secrets management, resource limits, and CI/CD should be added before production deployment.

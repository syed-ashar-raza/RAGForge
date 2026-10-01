# RAGForge

> Production-oriented local Retrieval-Augmented Generation (RAG) system built with Python, FastAPI, semantic embeddings, SQLite, Ollama, and Qwen3.

RAGForge is a complete working RAG application that ingests documents, creates semantic embeddings, retrieves relevant context, and generates grounded answers using a locally running LLM.

The project is designed as a practical AI engineering portfolio project demonstrating the core architecture behind modern document-grounded AI systems.

---

## 🚀 Overview

RAGForge implements an end-to-end local RAG pipeline:

```text
                    ┌─────────────────────┐
                    │       Document      │
                    │      Upload         │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   Document Parser   │
                    │    PDF / TXT        │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │      Chunking       │
                    │  Normalize + Split  │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │     Embeddings      │
                    │ MiniLM / 384-dim    │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │       SQLite        │
                    │ Documents + Chunks  │
                    └──────────┬──────────┘
                               │
                         User Query
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Semantic Retrieval  │
                    │ Cosine Similarity   │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   Grounded Prompt   │
                    │ Retrieved Context   │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   Ollama + Qwen3    │
                    │      4B Local LLM   │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Grounded Answer +   │
                    │ Source References   │
                    └─────────────────────┘
✨ Key Features
📄 PDF and TXT document ingestion
🔍 Semantic vector retrieval
🧠 Sentence-Transformers embeddings
🤖 Local LLM generation with Ollama
⚡ Qwen3 4B local model
📦 SQLite persistence
🧩 Configurable chunk size and overlap
🎯 Configurable retrieval threshold and top-k
🔐 SHA-256 duplicate-document detection
📚 Source-aware grounded answers
🌐 FastAPI REST API
🧪 Automated pytest test suite
🔎 Ruff static analysis
🛡️ Grounded-answer fallback behavior
🐳 Docker configuration included
⚙️ Environment-based configuration
📊 Isolated evaluation suite
💻 Fully local development workflow
🧠 RAG Pipeline

RAGForge follows a standard Retrieval-Augmented Generation architecture.

1. Document Ingestion

Supported documents are uploaded through the FastAPI API.

Current supported formats:

PDF
TXT

Each document receives a SHA-256 content hash.

If the same document is uploaded again, RAGForge detects the duplicate instead of ingesting it again.

2. Text Parsing

Documents are parsed into normalized text before being processed by the chunking pipeline.

PDF documents are processed with pypdf.

3. Chunking

Long documents are divided into smaller overlapping chunks.

Default configuration:

Chunk size:     800 characters
Chunk overlap:  120 characters

Chunking allows retrieval to operate on focused sections of documents instead of entire files.

4. Embeddings

RAGForge converts each chunk into a dense semantic vector using:

sentence-transformers/all-MiniLM-L6-v2

Embedding dimension:

384

These vectors allow semantic similarity comparison between user queries and document chunks.

5. Retrieval

When a user submits a question:

The query is embedded.
Stored chunk embeddings are loaded.
Cosine similarity is calculated.
Results below the configured similarity threshold are removed.
The highest-scoring chunks are selected.
The selected context is passed to the generation layer.

Default retrieval configuration:

Top K:                 5
Similarity threshold:  0.25
Maximum context:       12000 characters
6. Grounded Generation

Retrieved document context is passed to the local LLM through a grounded prompt.

RAGForge instructs the model to answer using the supplied context.

If the retrieved documents do not contain enough information, the system is designed to explicitly communicate that limitation rather than pretending unsupported information is present.

🤖 Local LLM

RAGForge uses Ollama for local LLM inference.

Current model:

qwen3:4b

The application communicates with the local Ollama HTTP API.

Default endpoint:

http://localhost:11434

This architecture keeps the generation layer local and avoids requiring a hosted LLM API for development.

🛠️ Tech Stack
Layer	Technology
Language	Python 3.14+
API	FastAPI
Server	Uvicorn
Validation	Pydantic
Configuration	pydantic-settings
Database	SQLite
ORM	SQLAlchemy
PDF Processing	pypdf
Embeddings	Sentence-Transformers
Embedding Model	all-MiniLM-L6-v2
LLM Runtime	Ollama
LLM	Qwen3 4B
Testing	pytest
Static Analysis	Ruff
Containerization	Docker
Version Control	Git
📁 Project Structure
RAGForge/
│
├── app/
│   ├── api/
│   │   └── routes.py
│   │
│   ├── core/
│   │   └── config.py
│   │
│   ├── db/
│   │   ├── database.py
│   │   ├── init_db.py
│   │   └── models.py
│   │
│   ├── ingestion/
│   │   ├── chunker.py
│   │   └── parsers.py
│   │
│   ├── rag/
│   │   ├── embeddings.py
│   │   ├── generator.py
│   │   └── retriever.py
│   │
│   ├── services/
│   │   └── documents.py
│   │
│   └── main.py
│
├── data/
│   └── documents/
│
├── docs/
│
├── evals/
│
├── scripts/
│
├── tests/
│
├── .dockerignore
├── .env.example
├── .gitignore
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
└── README.md
🌐 API

Base API prefix:

/api/v1
Health Check
GET /api/v1/health

Example:

{
  "status": "ok"
}
Upload Document
POST /api/v1/documents

Upload a PDF or TXT document.

The ingestion pipeline:

Upload
  ↓
Hash
  ↓
Duplicate Check
  ↓
Parse
  ↓
Chunk
  ↓
Embed
  ↓
Persist
Query
POST /api/v1/query

The query endpoint performs:

User Question
      ↓
Query Embedding
      ↓
Semantic Retrieval
      ↓
Context Selection
      ↓
Grounded Prompt
      ↓
Ollama / Qwen3
      ↓
Answer + Sources
🔬 Verified End-to-End Flow

RAGForge has been tested through the actual application pipeline.

Verified flow:

Document Upload
      ↓
Document Parsing
      ↓
Chunk Creation
      ↓
Embedding Generation
      ↓
SQLite Persistence
      ↓
Semantic Retrieval
      ↓
Ollama HTTP API
      ↓
Qwen3 4B
      ↓
Grounded Response
      ↓
Source Metadata

The end-to-end query path has been manually verified to retrieve relevant indexed content and generate a grounded response through the local Qwen3 model.

🧪 Testing

Run the complete test suite:

python -m pytest -q

Current verified result:

6 passed
🔍 Code Quality

Ruff is used for static analysis.

Run:

ruff check .

Compile validation:

python -m compileall app

The project has been verified with:

Compile:  PASSED
Ruff:     PASSED
Pytest:   PASSED

Quality gate:

RAGFORGE QUALITY GATE: PASSED
📊 Evaluation

RAGForge includes an isolated evaluation suite covering retrieval, answer evidence, and unsupported-question abstention.

The evaluation corpus is loaded into a temporary SQLite database so the evaluation does not depend on the application's persistent development data.

Verified Evaluation Results
Retrieval evaluation:       4/4 passed
Answer evidence evaluation: 4/4 passed
Abstention evaluation:      1/1 passed

The evaluation dataset contains four supported factual cases and one unsupported-question case.

The supported cases verify that retrieved context contains the expected source evidence and that generated or fallback answers contain the expected answer terms.

The unsupported case is evaluated separately as an abstention test. It is intentionally not counted as a retrieval failure because semantic retrieval can return related context even when the requested information is absent.

The fast evaluation suite does not require the Ollama service for every run. When Ollama is unavailable, RAGForge's grounded fallback behavior is exercised instead.

The latest fast evaluation run therefore verifies retrieval, answer evidence against the available generator output, and deterministic abstention behavior. It should not be interpreted as a live LLM generation benchmark when Ollama is offline.

Run the evaluation suite with:

python evals/run.py
📦 Installation

Clone the repository and enter the project:

git clone https://github.com/syed-ashar-raza/RAGForge.git
cd RAGForge

Create a virtual environment:

python -m venv .venv

Activate it:

.\.venv\Scripts\Activate.ps1

Install the project:

python -m pip install -e ".[dev]"
🤖 Install Ollama

Install Ollama separately and make sure the local service is running.

Then pull the configured model:

ollama pull qwen3:4b

Verify:

ollama list

The application expects Ollama at:

http://localhost:11434
⚙️ Configuration

RAGForge uses environment-based configuration.

Copy:

.env.example

to:

.env

Example configuration:

DATABASE_URL=sqlite:///./data/ragforge.db

OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen3:4b

EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
EMBEDDING_DIMENSION=384

CHUNK_SIZE=800
CHUNK_OVERLAP=120

TOP_K=5
MAX_CONTEXT_CHARS=12000
SIMILARITY_THRESHOLD=0.25

UPLOAD_DIR=./data/documents
▶️ Run the Application

Start the FastAPI server:

uvicorn app.main:app --reload

The API will be available locally through the configured Uvicorn server.

FastAPI automatically exposes interactive API documentation.

🔐 Duplicate Detection

RAGForge calculates a SHA-256 hash for uploaded documents.

Example workflow:

Document A
   ↓
SHA-256
   ↓
Hash stored

Document A uploaded again
   ↓
SHA-256
   ↓
Existing hash detected
   ↓
Duplicate response

This prevents unnecessary repeated ingestion of identical documents.

🗄️ Data Model

RAGForge currently uses two main database entities:

Document

Stores document-level metadata including:

document ID
filename
content hash
upload timestamp
metadata
Chunk

Stores chunk-level information including:

chunk ID
document relationship
chunk text
embedding
source locator
timestamps

Embeddings are currently persisted as JSON text for the local SQLite implementation.

🏗️ Engineering Decisions
Local-first architecture

The project intentionally uses local infrastructure for development:

FastAPI
+
SQLite
+
Sentence Transformers
+
Ollama
+
Qwen3

This provides a reproducible development environment without requiring paid hosted inference APIs.

SQLite Runtime

SQLite was selected for the current local runtime because it provides:

zero configuration
fast local development
easy portability
simple persistence
minimal infrastructure overhead

The codebase also includes PostgreSQL/pgvector-related dependencies and Docker configuration for future deployment-oriented evolution.

Separate RAG Components

The application separates major responsibilities:

Ingestion
    ↓
Chunking
    ↓
Embeddings
    ↓
Retrieval
    ↓
Generation
    ↓
API

This makes individual components easier to test, replace, and evolve.

🐳 Docker

Docker configuration is included for future containerized deployment.

Files:

Dockerfile
docker-compose.yml
.dockerignore

The current development workflow is optimized for local Windows execution.

🔄 Future Production Extensions

Potential future improvements include:

PostgreSQL + pgvector production deployment
Hybrid keyword + semantic retrieval
Cross-encoder reranking
Streaming LLM responses
Background document ingestion
Authentication and authorization
Rate limiting
Observability and tracing
Structured evaluation datasets
Retrieval metrics
Answer-quality metrics
Document versioning
Multi-user isolation
Cloud deployment
CI/CD pipeline
Production monitoring
More advanced chunking strategies
Metadata filtering
Conversation-aware retrieval

These are planned extensions rather than claims about the current implementation.

📈 Current Project Status

RAGForge currently represents a working local RAG MVP with:

document ingestion
PDF/TXT parsing
chunking
semantic embeddings
persistent storage
semantic retrieval
local LLM generation
grounded prompting
duplicate detection
FastAPI endpoints
automated tests
static analysis
evaluation coverage
Docker configuration
Git/GitHub version control

The project has been tested through the complete local RAG workflow.

🎯 What This Project Demonstrates

RAGForge demonstrates practical AI engineering skills across multiple layers:

Python
  ↓
Software Architecture
  ↓
FastAPI
  ↓
Data Persistence
  ↓
Document Processing
  ↓
Embeddings
  ↓
Vector Retrieval
  ↓
LLM Integration
  ↓
RAG Architecture
  ↓
Evaluation
  ↓
Testing
  ↓
Code Quality
  ↓
Git/GitHub

Rather than being only an LLM API wrapper, RAGForge implements the complete retrieval pipeline required for a functional document-grounded AI application.

👨‍💻 Author

Syed Ashar Raza

AI Engineer | Machine Learning | Generative AI | LLMs | RAG | AI Agents

Building practical AI systems focused on:

AI Engineering
RAG Systems
LLM Applications
Generative AI
Machine Learning
Python
Backend Development
Production AI Systems
📄 License

This project is currently intended as a portfolio and educational engineering project.

See the repository for the latest project status and licensing information.

⭐ Project

If you find the project useful or interesting, consider giving the repository a ⭐ on GitHub.

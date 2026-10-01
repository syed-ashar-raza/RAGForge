# RAGForge

> Production-oriented local Retrieval-Augmented Generation system built with Python, FastAPI, embeddings, semantic retrieval, grounded generation, and evaluation.

RAGForge is an end-to-end Retrieval-Augmented Generation (RAG) system designed to demonstrate the engineering principles required to build reliable document-grounded AI applications.

The system ingests documents, creates overlapping text chunks, generates semantic embeddings, retrieves relevant context, generates grounded answers through a local LLM, and returns source information with the response.

The project focuses on practical AI engineering rather than a simple LLM API wrapper: ingestion, retrieval, grounding, attribution, evaluation, testing, configuration, API design, and reproducible local execution.

---

## 🚀 Overview

RAGForge implements the following pipeline:

```text
                    ┌─────────────────────┐
                    │     User Query      │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │     FastAPI API     │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │       Query         │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Semantic Retrieval  │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Relevant Chunks     │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Grounded Generation │
                    │      Ollama         │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Answer + Sources    │
                    └─────────────────────┘

Document ingestion follows:

PDF / TXT / Markdown
        │
        ▼
   Text Extraction
        │
        ▼
   Text Chunking
        │
        ▼
 Semantic Embeddings
        │
        ▼
 Persistent Storage
✨ Key Features
PDF, TXT, and Markdown document ingestion
SHA-256 duplicate detection
Text extraction with pypdf
Overlapping text chunking
Semantic embeddings
Local vector representation
Cosine-similarity retrieval
Configurable retrieval threshold
Configurable top-k retrieval
Context-size limits
Grounded LLM generation
Source attribution
Explicit unsupported-question abstention
FastAPI REST API
SQLite persistence
Local Ollama inference
Qwen3:4b development model
Automated testing
Evaluation dataset
Isolated evaluation environment
Ruff code-quality checks
Docker support
Configuration through environment variables
🧠 RAG Pipeline

RAGForge follows a standard retrieval-augmented generation architecture.

1. Document Ingestion

Supported document types:

PDF
TXT
Markdown

PDF text extraction is performed with pypdf.

Documents are processed into normalized text before chunking.

2. Duplicate Detection

RAGForge calculates a SHA-256 hash for uploaded documents.

This allows the system to detect previously indexed documents and avoid unnecessary duplicate ingestion.

Document
   │
   ▼
SHA-256
   │
   ├── Existing → Skip
   │
   └── New      → Continue ingestion
3. Chunking

Documents are divided into overlapping chunks.

Current configuration:

Chunk size:       800 characters
Chunk overlap:    120 characters

The overlap helps preserve context across chunk boundaries.

4. Embeddings

RAGForge uses:

sentence-transformers/all-MiniLM-L6-v2

The embedding dimension is:

384

Embeddings represent document chunks in semantic vector space.

5. Retrieval

For a user query, RAGForge:

User Query
    │
    ▼
Query Embedding
    │
    ▼
Cosine Similarity
    │
    ▼
Ranked Chunks
    │
    ▼
Top-k Context

Current retrieval configuration:

Top-k:                 5
Similarity threshold:  0.25
Maximum context:       12000 characters

Semantic similarity is calculated using cosine similarity.

🤖 Grounded Generation

Retrieved context is passed to the local language model with an explicit grounding instruction:

Use ONLY the supplied context.
Do not invent facts.
If the answer is not contained in the context,
clearly state that the indexed documents do not
contain enough information.

This creates a deliberate separation:

Retrieval
    ↓
Evidence
    ↓
Grounded Generation
    ↓
Answer + Sources

The system is designed to reduce unsupported generation by requiring the model to answer from retrieved evidence.

🛑 Unsupported Questions and Abstention

RAGForge explicitly handles questions that are not supported by the indexed evidence.

For unsupported questions, the expected behavior is to abstain rather than fabricate an answer.

Example:

Question:
What database does RAGForge use for production user authentication?

Result:
The indexed documents do not contain enough information
to answer the question.

This behavior is tested separately from retrieval quality.

An unsupported question is not automatically treated as a retrieval failure because a semantically similar chunk can still be retrieved while the correct answer is that the available evidence is insufficient.

🔬 Evaluation

RAGForge includes a dedicated evaluation suite under:

evals/

The evaluation corpus is isolated from the normal application database using a temporary SQLite database.

This prevents unrelated application data from influencing evaluation results.

Evaluation Coverage

The current dataset contains:

4 supported questions
1 unsupported question

The supported questions test:

System description
Storage architecture
Similarity calculation
Local LLM runtime

The unsupported question tests abstention behavior.

Verified Evaluation Results
Retrieval evaluation:        4/4 passed
Answer evidence evaluation:  4/4 passed
Abstention evaluation:       1/1 passed

The evaluation therefore provides separate evidence for:

Retrieval
   ↓
Answer Evidence
   ↓
Abstention
Evaluation Design

The evaluation runner:

Loads the evaluation dataset
Uses an isolated temporary SQLite database
Ingests only the evaluation corpus
Evaluates supported retrieval cases
Checks generated/fallback answer evidence
Tests deterministic abstention behavior
Returns a non-zero exit code when the required evaluation checks fail
⚠️ Evaluation Runtime Note

The latest fast evaluation run was performed while the local Ollama service was offline.

In that run, the generator correctly used RAGForge's deterministic fallback behavior based on retrieved context.

Therefore:

Retrieval evaluation       → exercised
Answer evidence evaluation → exercised against fallback output
Abstention evaluation      → deterministic test
Live Ollama generation     → not exercised in that specific run

Earlier manual verification with Ollama/Qwen3:4b demonstrated the grounded generation and unsupported-question abstention behavior.

This distinction is intentional: evaluation results are reported according to what was actually executed rather than being presented as a live LLM benchmark when the model service was unavailable.

🧪 Testing

Run the automated test suite:

pytest -q

The project has verified automated coverage for the implemented RAG pipeline and application components.

The current repository test suite includes:

6 tests passed

The evaluation suite is separate from the normal unit/integration test suite.

🔍 Code Quality

RAGForge uses Ruff for static analysis.

Run:

ruff check .

Python compilation can be verified with:

python -m compileall -q app evals

The project uses a quality-oriented workflow:

Code
 ↓
Static Analysis
 ↓
Compilation
 ↓
Automated Tests
 ↓
Evaluation
🛠️ Tech Stack
Technology	Purpose
Python	Core application
FastAPI	REST API
Pydantic	Configuration and validation
SQLite	Local persistence
sentence-transformers	Semantic embeddings
all-MiniLM-L6-v2	Embedding model
NumPy	Vector operations
pypdf	PDF text extraction
Ollama	Local LLM inference
Qwen3:4b	Local development model
pytest	Automated testing
Ruff	Static analysis
Docker	Containerized execution
GitHub Actions	CI
📁 Project Structure
RAGForge/
│
├── app/
│   ├── api/
│   ├── core/
│   ├── db/
│   ├── models/
│   ├── rag/
│   └── services/
│
├── evals/
│   ├── dataset.jsonl
│   ├── evaluation_document.txt
│   └── run.py
│
├── tests/
│
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
├── .env.example
└── README.md
🌐 API

The application exposes a versioned API under:

/api/v1

Core functionality includes:

Health
GET /api/v1/health
Document Upload
POST /api/v1/documents/upload
Query
POST /api/v1/query

The query response contains the generated answer together with retrieved source metadata.

⚙️ Configuration

RAGForge uses environment-based configuration.

Important settings include:

DATABASE_URL
OLLAMA_BASE_URL
OLLAMA_MODEL
EMBEDDING_MODEL
CHUNK_SIZE
CHUNK_OVERLAP
TOP_K
SIMILARITY_THRESHOLD
MAX_CONTEXT_CHARS

Current local defaults include:

Embedding model:
sentence-transformers/all-MiniLM-L6-v2

LLM:
qwen3:4b

Chunk size:
800

Chunk overlap:
120

Top-k:
5

Similarity threshold:
0.25

Maximum context:
12000 characters
🗄️ Data Model

The local application stores document and chunk information in SQLite.

Conceptually:

Document
   │
   ├── Metadata
   ├── SHA-256 hash
   │
   └── Chunks
          │
          ├── Text
          └── Embedding

The current local runtime stores embeddings as JSON text and performs semantic similarity calculations in Python using cosine similarity.

This is intentionally simple and transparent for the local implementation.

🧭 Engineering Decisions
Local-First Architecture

The current implementation is designed to run locally using:

FastAPI
+
SQLite
+
Sentence Transformers
+
Ollama

This provides a reproducible development environment without requiring a hosted vector database or hosted LLM API.

Explicit Retrieval Controls

Retrieval uses configurable:

top_k
similarity_threshold
max_context_chars

These controls make retrieval behavior explicit rather than relying on hidden defaults.

Grounded Generation

The generator receives retrieved context explicitly and is instructed not to invent information outside that context.

This establishes a clear boundary between:

Evidence
   ↓
Generation
Separate Evaluation Environment

The evaluation runner uses a temporary database and dedicated evaluation corpus.

This reduces contamination from unrelated application data and makes the evaluation workflow more reproducible.

Abstention as a Separate Behavior

The project treats unsupported questions differently from retrieval failures.

A semantically similar chunk may still be retrieved for an unsupported question.

Therefore, the evaluation checks whether the final answer appropriately recognizes insufficient evidence instead of requiring the retriever itself to reject the query.

🐳 Docker

RAGForge includes Docker support for reproducible local execution.

Build and run using the provided Docker configuration:

docker compose up --build

The application can then be accessed through the configured FastAPI service.

📦 Installation
1. Clone the Repository
git clone https://github.com/syed-ashar-raza/RAGForge.git
cd RAGForge
2. Create a Virtual Environment
python -m venv .venv
3. Activate the Environment

Windows PowerShell:

.venv\Scripts\Activate.ps1

Linux/macOS:

source .venv/bin/activate
4. Install Dependencies
pip install -e .
5. Configure Environment

Windows PowerShell:

Copy-Item .env.example .env

Review the environment configuration before running the application.

🤖 Ollama Setup

RAGForge uses Ollama for local language-model generation.

The verified development model is:

qwen3:4b

Make sure Ollama is installed and running before using live generation.

The application communicates with the local Ollama service.

▶️ Run the Application

Start the FastAPI server:

uvicorn app.main:app --reload

The local application is available at:

http://127.0.0.1:8000

FastAPI documentation:

http://127.0.0.1:8000/docs
🔄 Verified End-to-End Flow

The implementation has been manually verified through the complete local RAG workflow:

Document
   ↓
Ingestion
   ↓
Text Extraction
   ↓
Chunking
   ↓
Embedding
   ↓
Storage
   ↓
Query Embedding
   ↓
Semantic Retrieval
   ↓
Context Construction
   ↓
Ollama / Qwen3:4b
   ↓
Grounded Answer
   ↓
Source Attribution

The system has also been verified for unsupported questions, where the grounded generation behavior recognizes insufficient evidence rather than fabricating an answer.

📊 Current Project Status

Status: MVP complete

Implemented capabilities:

Document ingestion
PDF/TXT/Markdown processing
Duplicate detection
Chunking with overlap
Semantic embeddings
Semantic retrieval
Grounded generation
Source attribution
Unsupported-question abstention
FastAPI API
SQLite persistence
Local Ollama inference
Automated testing
Evaluation suite
Static analysis
Docker support
CI configuration

Current verified evidence includes:

6 automated tests passed
4/4 retrieval evaluation
4/4 answer evidence evaluation
1/1 abstention evaluation
Local RAG pipeline verification
Ollama/Qwen3:4b verification
Source attribution
Unsupported-question handling
🎯 What This Project Demonstrates

RAGForge demonstrates practical AI engineering across multiple layers:

Python
   ↓
Backend Engineering
   ↓
FastAPI
   ↓
Document Processing
   ↓
Embeddings
   ↓
Semantic Retrieval
   ↓
RAG
   ↓
LLM Integration
   ↓
Grounded Generation
   ↓
Source Attribution
   ↓
Evaluation
   ↓
Testing
   ↓
Docker / CI

The project demonstrates more than simply connecting an LLM to a prompt.

It implements the major components required to build a document-grounded AI application:

Ingest
  ↓
Represent
  ↓
Retrieve
  ↓
Ground
  ↓
Generate
  ↓
Evaluate
🔮 Future Production Extensions

Potential future improvements include:

PostgreSQL + pgvector at larger scale
Dedicated vector database infrastructure
Hybrid lexical + semantic retrieval
Reranking
Advanced retrieval evaluation
Distributed ingestion workers
Background processing
Authentication and authorization
Advanced observability
Hosted model providers
GPU inference
Production deployment infrastructure

These are future extensions and are not presented as current implementation capabilities.

👨‍💻 Author

Syed Ashar Raza

AI Engineer | Machine Learning | Generative AI | LLMs | RAG | AI Agents

Building practical AI systems focused on:

AI Engineering
Machine Learning
Generative AI
LLM Applications
Retrieval-Augmented Generation
Agentic AI
Production AI Systems
Python
Backend Engineering
Reliable AI Infrastructure
📄 License

Apache-2.0

⭐ Project

If you find RAGForge useful or interesting, consider giving the repository a ⭐ on GitHub.
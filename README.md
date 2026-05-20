<div align="center">

# AtlasRAG

### Advanced RAG Architecture for Educational AI

<br/>

> **AtlasRAG** is a modular, production-oriented AI system that transforms static study documents into an interactive tutoring experience. Built on a full Retrieval-Augmented Generation pipeline, it grounds every response in source-verified context — eliminating hallucinations, enforcing citations, and adapting dynamically to each learner.

<br/>

</div>

---

## Overview

AtlasRAG is not a wrapper around a chatbot API. It is a **complete, layered AI engineering system** built around the RAG paradigm — combining semantic document retrieval, dense vector search, and grounded language generation into a coherent orchestration architecture.

The system ingests raw documents (PDF, DOCX), transforms them through a recursive chunking and embedding pipeline, indexes them in a FAISS vector store, and retrieves semantically relevant context at query time using a combination of cosine similarity and Maximum Marginal Relevance (MMR). Retrieved context is injected into a structured prompt and routed through OpenRouter's model-agnostic LLM gateway, producing citation-aware, source-grounded answers.

All components are independently testable, loosely coupled, and designed for extensibility. The entire ingestion-to-generation pipeline can be swapped, upgraded, or replaced at the component level without touching the orchestration layer.

---

## Features

### Document Ingestion & Processing
- Multi-format document ingestion — **PDF**, **DOCX**, and web URLs via LangChain loaders
- Semantic text preprocessing with Unicode normalization, whitespace collapsing, and near-empty page filtering
- **Recursive character-aware text splitting** that respects paragraph → sentence → word boundaries, with configurable chunk size and overlap
- Chunk-level metadata enrichment: source filename, page number, character count, chunk index

### Retrieval & Vector Search
- **Dense vector embeddings** via `sentence-transformers/all-MiniLM-L6-v2` — 384-dimensional, L2-normalized
- **FAISS IndexFlatIP** for exact inner-product search over normalized vectors (equivalent to cosine similarity)
- **Top-K retrieval** as a low-latency baseline for high-precision queries
- **Maximum Marginal Relevance (MMR)** retrieval for diversity-aware context selection, preventing redundant chunks from saturating the context window
- Persistent index storage: FAISS binary index + pickled document metadata for stateless restarts

### Generation & Orchestration
- **Model-agnostic LLM interface** via abstract base class — swap between Mixtral, LLaMA-3, Claude, or GPT-4 without modifying orchestration logic
- **OpenRouter API** as the unified model gateway, compatible with the OpenAI Python SDK
- **Citation-aware RAG prompting** — every response references source chunks with `[Source N]` notation
- **Structured JSON quiz generation** using temperature-controlled LLM output for deterministic question formatting
- Conversational memory with configurable turn window (default: last 3 exchanges)
- Grounded generation: the LLM is explicitly instructed to refuse answering outside the provided context, preventing hallucination

### Application Layer
- Streamlit-based conversational UI with session state management, chat history, and source citation expander
- Multi-document session support — index multiple files per session
- **SQLite persistence** via SQLAlchemy ORM for chat history, user sessions, and quiz results
- **bcrypt-secured authentication** with hashed password storage
- **Adaptive quiz generation pipeline** with structured output validation and difficulty scaling
- Docker-ready deployment configuration

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        ATLASRAG SYSTEM                              │
│                                                                     │
│   ┌──────────────┐        ┌────────────────────────────────────┐   │
│   │  Streamlit   │        │         INGESTION PIPELINE         │   │
│   │  Frontend    │◄──────►│  Loader → Preprocessor → Chunker  │   │
│   │  (app/)      │        └──────────────┬─────────────────────┘   │
│   └──────┬───────┘                       │                         │
│          │                               ▼                         │
│          │                    ┌─────────────────────┐              │
│          │                    │  EmbeddingModel      │              │
│          │                    │  SentenceTransformer │              │
│          │                    │  all-MiniLM-L6-v2    │              │
│          │                    └──────────┬──────────┘              │
│          │                               │                         │
│          │                               ▼                         │
│          │                    ┌─────────────────────┐              │
│          │                    │  FAISSVectorStore    │              │
│          │                    │  IndexFlatIP (cosine)│              │
│          │                    │  Persistent to disk  │              │
│          │                    └──────────┬──────────┘              │
│          │                               │                         │
│          │              ┌────────────────▼──────────────────┐      │
│          │              │         RETRIEVAL LAYER            │      │
│          │              │   Top-K  │  MMR (fetch_k → k)     │      │
│          │              └────────────────┬──────────────────┘      │
│          │                               │                         │
│          │              ┌────────────────▼──────────────────┐      │
│          │              │        PROMPT BUILDER              │      │
│          │              │  System  │  Context  │  History    │      │
│          │              └────────────────┬──────────────────┘      │
│          │                               │                         │
│          │              ┌────────────────▼──────────────────┐      │
│          └─────────────►│      OpenRouter LLM Gateway        │      │
│                         │  Mixtral │ LLaMA-3 │ Claude │ GPT  │      │
│                         └───────────────────────────────────┘      │
│                                                                     │
│   ┌─────────────────────────────────────────────────────────────┐  │
│   │  PERSISTENCE LAYER                                          │  │
│   │  SQLite (SQLAlchemy ORM)  │  FAISS Index  │  bcrypt Auth   │  │
│   └─────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

### Design Principles

| Principle | Implementation |
|---|---|
| **Separation of concerns** | `core/` has zero imports from `app/`. Business logic is fully UI-agnostic. |
| **Dependency inversion** | `RAGChain` depends on `BaseLLM` (abstract), not `OpenRouterLLM` (concrete). |
| **Single responsibility** | Each module has one job: `loader.py` loads, `chunker.py` splits, `embedder.py` embeds. |
| **Fail-fast configuration** | `pydantic-settings` validates all environment variables at startup, not at runtime. |
| **Stateless retrieval** | FAISS index + metadata pickle enables full stateless restart without re-indexing. |

---

## Retrieval Pipeline Flow

```
  User uploads document
          │
          ▼
  ┌───────────────────┐
  │  DocumentLoader   │  ← PyPDFLoader / Docx2txtLoader / WebBaseLoader
  └────────┬──────────┘
           │  List[LangChain Document]
           ▼
  ┌───────────────────┐
  │  TextPreprocessor │  ← Unicode normalization, whitespace collapse,
  └────────┬──────────┘    near-empty page filtering (< 50 chars dropped)
           │
           ▼
  ┌───────────────────┐
  │   TextChunker     │  ← RecursiveCharacterTextSplitter
  └────────┬──────────┘    separators: ["\n\n", "\n", ". ", " ", ""]
           │               chunk_size: 512, overlap: 64
           │  List[Chunk] with chunk_id, char_count metadata
           ▼
  ┌───────────────────┐
  │  EmbeddingModel   │  ← SentenceTransformer("all-MiniLM-L6-v2")
  └────────┬──────────┘    normalize_embeddings=True → cosine via dot product
           │  float32 numpy array [N × 384]
           ▼
  ┌───────────────────┐
  │ FAISSVectorStore  │  ← IndexFlatIP.add(vectors)
  └────────┬──────────┘    Parallel document list for metadata retrieval
           │               Persisted: .index + .docs pickle
           │
           │  ── QUERY TIME ──────────────────────────────────
           │
           ▼
  ┌───────────────────┐
  │  Query Embedder   │  ← Same model, same normalization (critical)
  └────────┬──────────┘
           │  float32 [1 × 384]
           ▼
  ┌───────────────────────────────────────────┐
  │  Retriever                                │
  │                                           │
  │  top_k()  → IndexFlatIP.search(q, k)      │
  │                                           │
  │  mmr()    → fetch_k candidates            │
  │             → iterative selection:        │
  │               score = λ·relevance         │
  │                      - (1-λ)·redundancy   │
  └────────┬──────────────────────────────────┘
           │  List[Document] — top-k diverse, relevant chunks
           ▼
  ┌───────────────────┐
  │  Prompt Builder   │  ← Formats: System | Context[N] | History | Question
  └────────┬──────────┘
           ▼
  ┌───────────────────┐
  │  OpenRouter LLM   │  ← Returns grounded, citation-aware answer
  └───────────────────┘
```

### Why MMR Over Naive Top-K?

Top-K retrieval has a well-known failure mode: when the same concept appears across multiple adjacent chunks, all K slots are consumed by near-duplicate content. The context window is wasted, and the model receives no broader coverage of the document.

**Maximum Marginal Relevance** balances two competing objectives at each selection step:

```
MMR(d) = λ · sim(d, query) − (1 − λ) · max sim(d, selected)
```

Where `λ = 0.5` equally weights relevance against diversity. The result is a context block that is both topically relevant and informationally distinct — maximizing the information density delivered to the language model per token of context.

---

## Tech Stack

| Layer | Technology | Role |
|---|---|---|
| **Frontend** | Streamlit 1.38 | Conversational UI, session state, file upload |
| **Orchestration** | LangChain 0.2.x | Document loaders, text splitters, schema types |
| **Embeddings** | SentenceTransformers 3.x | Dense vector generation (`all-MiniLM-L6-v2`) |
| **Vector Store** | FAISS (Meta AI) | Exact inner-product nearest-neighbour search |
| **LLM Gateway** | OpenRouter API | Model-agnostic inference (Mixtral, LLaMA-3, Claude) |
| **LLM SDK** | OpenAI Python SDK | OpenRouter uses the OpenAI-compatible API spec |
| **Database** | SQLite + SQLAlchemy | Chat history, user accounts, quiz results |
| **Auth** | bcrypt | Password hashing with salt rounds |
| **Config** | pydantic-settings | Type-safe environment variable management |
| **Containerisation** | Docker + Compose | Reproducible deployment |
| **Language** | Python 3.11+ | Core implementation language |

---

## Project Structure

```
atlasrag/
│
├── app/                          # Streamlit application layer
│   ├── components/
│   │   ├── citation_card.py      # Source citation UI component
│   │   └── sidebar.py            # Navigation and auth controls
|   |   └── __init__.py 
│   ├── pages/
│   │   ├── chat.py               # Main conversational interface
│   │   ├── history.py            # Session history viewer
│   │   ├── quiz.py               # Adaptive quiz interface
│   │   └── upload.py             # Document upload and indexing
|   |   └── __init__.py 
│   └── main.py                   # Application entry point
|   └── __init__.py 
│
├── auth/
│   └── auth_handler.py           # bcrypt registration and login
|   └── __init__.py 
│
├── config/
│   └── settings.py               # pydantic-settings config (singleton)
|   └── __init__.py 
│
├── core/                         # Business logic — zero UI dependencies
│   ├── embeddings/
│   │   └── embedder.py           # SentenceTransformer singleton wrapper
│   ├── ingestion/
│   │   ├── chunker.py            # RecursiveCharacterTextSplitter
│   │   ├── loader.py             # PDF / DOCX / URL document loader
│   │   └── preprocessor.py       # Text cleaning and normalization
│   ├── llm/
│   │   ├── base.py               # Abstract LLM interface (BaseLLM)
│   │   └── openrouter.py         # OpenRouter implementation
|   |   └── __init__.py 
│   ├── memory/
│   │   └── conversation.py       # Sliding window chat history
|   |   └── __init__.py 
│   ├── pipelines/
│   │   ├── quiz_chain.py         # Structured quiz generation pipeline
│   │   └── rag_chain.py          # RAG orchestration pipeline
|   |   └── __init__.py 
│   ├── prompts/
│   │   ├── quiz.py               # Quiz generation prompt templates
│   │   └── tutor.py              # Citation-aware RAG system prompts
│   ├── retrieval/
│   │   ├── reranker.py           # Cross-encoder reranking (optional)
│   │   └── retriever.py          # Top-K and MMR retrieval logic
|   |   └── __init__.py 
│   └── vectorstore/
│   |   └── faiss_store.py        # FAISS index CRUD and persistence
|   |   └── __init__.py 
|   └── __init__.py 
│
├── data/
│   ├── faiss_indexes/            # Persisted FAISS binary indexes (gitignored)
│   └── uploads/                  # Temporary document storage (gitignored)
│
├── db/
│   ├── chat_store.py             # Chat message read/write operations
│   ├── init_db.py                # Schema initialisation script
│   ├── models.py                 # SQLAlchemy ORM models
│   └── session.py                # Database session factory
|   └── migration.py 
│
├── docker/
│   ├── Dockerfile
│   └── docker-compose.yml
│
├── scripts/
│   └── test_llm.py               # LLM connectivity smoke test
│   └── all test files
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

---

## Installation

### Prerequisites

- Python 3.11+
- Git
- An [OpenRouter API key](https://openrouter.ai) (free tier supports Mixtral-8x7B)
- Docker (optional, for containerised deployment)

### Local Setup

```bash
# 1. Clone the repository
git clone https://github.com/ashmita473/atlasrag.git
cd atlasrag

# 2. Create and activate virtual environment
python -m venv venv
source venv/bin/activate        # macOS / Linux
# venv\Scripts\activate         # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env with your API key and settings (see below)

# 5. Initialise the database
python db/init_db.py

# 6. Launch the application
streamlit run app/main.py
```

### Docker Deployment

```bash
# Build and run with Docker Compose
docker compose -f docker/docker-compose.yml up --build

# Application available at http://localhost:8501
```

---

## Environment Variables

```bash
# .env.example

# ── LLM Configuration ────────────────────────────────────────────────
OPENROUTER_API_KEY=your_openrouter_api_key_here
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1

# Model selection — swap without changing any application code
DEFAULT_MODEL=mistralai/mixtral-8x7b-instruct
# Alternatives: meta-llama/llama-3-8b-instruct
#               anthropic/claude-3-haiku
#               openai/gpt-4o-mini

# ── Embedding Configuration ──────────────────────────────────────────
EMBEDDING_MODEL=all-MiniLM-L6-v2

# ── Retrieval Configuration ──────────────────────────────────────────
CHUNK_SIZE=512
CHUNK_OVERLAP=64
TOP_K_RETRIEVAL=5

# ── Database ─────────────────────────────────────────────────────────
DB_URL=sqlite:///./atlasrag.db

# ── Security ─────────────────────────────────────────────────────────
# Generate with: python -c "import secrets; print(secrets.token_hex(32))"
SECRET_KEY=your_32_character_secret_key_here
```

> **Security note:** Never commit `.env` to version control. The `.gitignore` excludes it by default. Rotate your API key immediately if accidentally exposed.

---

## Running the Application

### Development

```bash
# Start Streamlit with hot-reload
streamlit run app/main.py

# Run the test suite
pytest tests/ -v

# Verify LLM connectivity
python scripts/test_llm.py

# Code formatting and linting
black core/ app/ db/ auth/
ruff check core/ app/ db/ auth/
```

### Production (Docker)

```bash
docker compose -f docker/docker-compose.yml up -d

# View logs
docker compose logs -f atlasrag

# Stop
docker compose down
```

---

## Example Workflow

### 1. Ingest a Document

```python
from core.ingestion.loader import DocumentLoader
from core.ingestion.preprocessor import TextPreprocessor
from core.ingestion.chunker import TextChunker
from core.vectorstore.faiss_store import FAISSVectorStore

loader       = DocumentLoader()
preprocessor = TextPreprocessor()
chunker      = TextChunker()
store        = FAISSVectorStore(index_path="data/faiss_indexes/session_01")

loaded  = loader.load_file("data/uploads/calculus_notes.pdf")
cleaned = preprocessor.process_documents(loaded.pages)
chunks  = chunker.split(cleaned)

store.add_documents(chunks)
store.save()

print(f"Indexed {store.index.ntotal} vectors from {len(chunks)} chunks")
# → Indexed 247 vectors from 247 chunks
```

### 2. Query with Source-Aware RAG

```python
from core.pipeline.rag_chain import RAGChain

chain = RAGChain(store)
result = chain.query(
    question="Explain the chain rule with an example.",
    history=[]
)

print(result.answer)
# → "The chain rule states that for a composite function f(g(x)),
#    the derivative is f'(g(x)) · g'(x). [Source 1]
#    For example, if h(x) = sin(x²), then h'(x) = cos(x²) · 2x. [Source 2]"

for i, source in enumerate(result.sources):
    print(f"[Source {i+1}] {source.metadata['filename']} — page {source.metadata.get('page', 'N/A')}")
```

### 3. Generate an Adaptive Quiz

```python
from core.pipeline.quiz_chain import QuizChain

quiz = QuizChain()
questions = quiz.generate(
    docs=result.sources,
    n=5,
    difficulty="hard"
)

for q in questions:
    print(f"Q: {q['question']}")
    print(f"   Options: {q['options']}")
    print(f"   Answer: {q['answer']}")
    print(f"   Explanation: {q['explanation']}\n")
```

---

## Quiz Generation Pipeline

AtlasRAG's quiz engine uses **temperature-controlled structured generation** to produce deterministic, well-formed quiz output. Rather than asking the LLM to generate free-form questions, the pipeline enforces a strict JSON schema at the prompt level, reducing output variance and enabling downstream validation.

```
Retrieved Context (top-5 MMR chunks)
              │
              ▼
    ┌─────────────────────┐
    │   Quiz Prompt       │   Difficulty: easy | medium | hard
    │   Template Builder  │   N questions, strict JSON schema
    └──────────┬──────────┘
               │
               ▼
    ┌─────────────────────┐
    │  OpenRouter LLM     │   temperature=0.3 (low, for consistency)
    │  Structured Output  │   max_tokens=2048
    └──────────┬──────────┘
               │
               ▼
    ┌─────────────────────┐
    │  JSON Validator     │   Parses and validates schema
    │  + Error Recovery   │   Strips markdown fences if present
    └──────────┬──────────┘
               │
               ▼
    List[QuizQuestion] → Streamlit Quiz UI → Score → SQLite
```

**Why structured JSON generation matters:** Free-form LLM output is non-deterministic and difficult to parse reliably at scale. By constraining the output schema in the prompt and using a low temperature, AtlasRAG achieves consistent, machine-readable quiz objects that can be validated, stored, and scored programmatically — an approach directly applicable to production AI pipelines.

---

## AI Engineering Concepts Demonstrated

This project was built to demonstrate depth across the full AI engineering stack — not just LLM API calls.

| Concept | Where Demonstrated | Why It Matters |
|---|---|---|
| **RAG Architecture** | `core/pipelines/rag_chain.py` | Grounds generation in verified source content, reducing hallucination by constraining the model to indexed context |
| **Dense Vector Embeddings** | `core/embeddings/embedder.py` | Converts semantic meaning to geometric proximity; enables similarity-based retrieval without keyword matching |
| **Embedding Normalization** | `embedder.py` — `normalize_embeddings=True` | L2-normalized vectors make cosine similarity equivalent to inner product, the metric FAISS IndexFlatIP optimizes for |
| **FAISS Vector Indexing** | `core/vectorstore/faiss_store.py` | low-latency nearest-neighbour search over hundreds of thousands of vectors without a vector database server |
| **MMR Retrieval** | `core/retrieval/retriever.py` | Balances relevance and diversity in context selection; prevents redundant chunks from wasting the context window |
| **Model-Agnostic Design** | `core/llm/base.py` + `openrouter.py` | Strategy pattern — the orchestration layer is decoupled from any specific LLM provider |
| **Structured Output Generation** | `core/pipelines/quiz_chain.py` | Prompt-enforced JSON schema enables deterministic, validatable AI outputs |
| **Chunking Strategy** | `core/ingestion/chunker.py` | RecursiveCharacterTextSplitter respects semantic boundaries; chunk overlap prevents context loss at boundaries |
| **Prompt Engineering** | `core/prompts/tutor.py` | Source-grounding instructions, citation enforcement, and knowledge-boundary prompts directly reduce hallucination |
| **Persistent Vector Store** | `faiss_store.save()` / `.load()` | Stateless application restarts without re-indexing — a production deployment requirement |
| **Type-Safe Configuration** | `config/settings.py` | pydantic-settings fails at startup on misconfiguration, not silently at runtime |
| **ORM Data Modelling** | `db/models.py` | SQLAlchemy models with UUID primary keys, timestamped records, and a clear migration path to PostgreSQL |

---

## Future Improvements

The following extensions represent concrete paths toward a more scalable and advanced systems or production-deployed system.

### Retrieval Quality
- **Cross-encoder reranking** — Add a second-stage `ms-marco-MiniLM` cross-encoder to rerank Top-K candidates before prompt injection. Measure NDCG improvement over MMR baseline.
- **Hybrid search** — Combine dense vector search with BM25 sparse retrieval. Use Reciprocal Rank Fusion (RRF) to merge result lists. Hybrid search consistently outperforms either approach alone on domain-specific corpora.
- **Hierarchical indexing** — Embed document-level summaries as a coarse index; chunk-level embeddings as a fine index. Retrieve at the document level first, then re-rank within the document.

### Generation Quality
- **RAGAs evaluation framework** — Implement automated evaluation: faithfulness, answer relevancy, context precision, and context recall. Run ablation studies across chunk sizes and retrieval strategies.
- **Self-RAG** — Implement retrieval-on-demand: the model decides whether to retrieve based on the query, rather than always retrieving. Reduces latency on simple factual queries.
- **Streaming responses** — Enable token-by-token streaming to the Streamlit UI using OpenRouter's streaming API for lower perceived latency.

### Adaptive Learning
- **Bayesian knowledge tracing** — Model per-concept mastery over time using student quiz performance. Dynamically adjust question difficulty toward the student's Zone of Proximal Development.
- **Spaced repetition scheduler** — Integrate SM-2 algorithm to schedule quiz reviews based on recall probability decay. Publishable in EDM or AIED conference proceedings.
- **Learning objective tagging** — Classify each chunk against Bloom's taxonomy levels. Generate questions targeting specific cognitive levels (recall → synthesis → evaluation).

### Infrastructure
- **PostgreSQL migration** — Replace SQLite with PostgreSQL via a single connection string change. Add Alembic migrations for schema versioning.
- **Async ingestion pipeline** — Move document processing to a Celery + Redis task queue for non-blocking uploads and real-time progress tracking.
- **Observability** — Instrument retrieval quality metrics (MRR, NDCG), LLM latency, and token cost per query using OpenTelemetry + Grafana.
- **Multi-tenancy** — Namespace FAISS indexes per user. Each user's documents are isolated at the index level, not filtered at query time.

---

## Resume-Worthy Highlights

> The following bullet points are formatted for direct use in a technical resume or portfolio.

- Designed and implemented a **Advanced RAG pipeline** from scratch — document ingestion through grounded LLM generation — using LangChain, FAISS, and Sentence Transformers.
- Implemented **Maximum Marginal Relevance (MMR) retrieval** from first principles, balancing relevance and diversity in context selection to maximize information density within the LLM context window
- Built a **model-agnostic LLM gateway** using the Strategy design pattern (abstract `BaseLLM` interface), enabling zero-code model swapping between Mixtral, LLaMA-3, and Claude via OpenRouter
- Engineered **citation-aware prompt templates** that ground every generated response in indexed source chunks with `[Source N]` notation, reducing hallucination at the prompt architecture level
- Developed a **structured JSON quiz generation pipeline** using temperature-controlled LLM output with schema-enforced prompting and downstream validation — demonstrating advanced structured AI output design
- Architected a fully **modular codebase** where `core/` has zero dependencies on the UI layer — enabling independent unit testing of every pipeline component and straightforward frontend substitution
- Implemented **FAISS IndexFlatIP** with L2-normalized embeddings, enabling cosine-equivalent similarity search with stateless index persistence across application restarts
- Deployed the full system as a **Dockerised multi-service application** with environment-variable-driven configuration, bcrypt-secured authentication, and SQLAlchemy ORM persistence

---

<div align="center">

Built with deliberate engineering decisions, not tutorial shortcuts.

**[View on GitHub](https://github.com/ashmita473/atlasrag)** · **[Report an Issue](https://github.com/ashmita473/atlasrag/issues)** · **[Suggest a Feature](https://github.com/ashmita473/atlasrag/issues)**

</div>

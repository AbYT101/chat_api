# Chat API

FastAPI backend for a chat application with multi-provider LLM support, RAG over a unified vector store, and vision-based image ingestion. Built for portfolio use and as a reference for async Python APIs.

## Tech Stack

- **API:** FastAPI, Pydantic, Uvicorn  
- **Database:** PostgreSQL with SQLAlchemy 2 (async via `asyncpg`), Alembic migrations  
- **Auth:** JWT (python-jose), bcrypt password hashing, Bearer token dependency  
- **AI / RAG:** LangChain (LCEL, prompts, message history), ChromaDB (persistent vector store), configurable embeddings (OpenAI / Ollama)  
- **LLM providers:** OpenAI, Groq, Ollama — text and vision models selected via a registry pattern  

## Capabilities

### Auth
- Signup and login with hashed passwords; JWT access tokens with configurable expiry.  
- Protected routes use a `get_current_user` dependency that validates the Bearer token and loads the user from the DB.

### Chat
- **Conversations:** Create, list, and manage conversations; send, edit, and delete messages.  
- **AI chat:** Send messages to a chosen text model; responses use LangChain with conversation memory (session-scoped history).  
- **Streaming:** Optional streaming endpoint for token-by-token responses.  
- **Models:** Registry-backed selection (e.g. GPT-3.5/4o-mini, Groq LLaMA/Mixtral, Ollama LLaMA/Mistral).

### RAG (Retrieval-Augmented Generation)
- Query a **unified** vector collection with optional filters (e.g. by ingestion type: file, text, image).  
- Retrieval is user-scoped; context is built from top-k similar chunks and passed to a configurable LLM.  
- Same embedding and collection configuration as the rest of the app (ChromaDB, OpenAI or Ollama embeddings).

### Vector store & ingest
- **Unified collection:** One ChromaDB collection (`unified_docs`) for all ingested content; metadata includes `user_id`, `ingestion_type`, and `source`.  
- **File ingest:** Upload a text file; content is chunked and embedded into the vector store.  
- **Text ingest:** Submit raw text; same chunking and upsert pipeline.  
- **Image ingest (vision):** Upload an image; a vision model (e.g. GPT-4o-mini or LLaVA) describes it, and the description is embedded and stored so it can be retrieved by RAG.

### Vision
- **Image upload:** Accepts an image, runs it through the vision pipeline (describe + store in vector DB), and returns the description.  
- Vision models are selected via the same registry (OpenAI and Ollama vision models).

### Vector search API
- Endpoints for similarity search and semantic search with scores over the unified collection, with optional metadata filters (e.g. by user).

## Practices Implemented

- **Async throughout:** AsyncSession for DB, async route handlers and services where I/O is involved.  
- **Structured app layout:** Routes, services, models, schemas, core (config, DB, security), and deps (DB session, auth) separated.  
- **Configuration:** Pydantic Settings with `.env`; single `Settings` class for DB, JWT, API keys, CORS.  
- **Security:** Passwords hashed with bcrypt; JWT creation/validation in a dedicated module; protected routes via FastAPI `Depends` and `Security(HTTPBearer)`.  
- **Dependency injection:** `get_db` for async sessions, `get_current_user` for auth; services receive DB or user where needed.  
- **Migrations:** Alembic for schema changes.  
- **CORS:** Configurable allowed origins via settings.  
- **Global exception handler:** 500s return a consistent JSON shape.  
- **Health check:** `/health` for basic liveness.  

## API Overview

| Area        | Prefix   | Notes                                      |
|------------|----------|--------------------------------------------|
| Auth       | `/auth`  | Signup, login, read current user           |
| Chat       | `/chat`  | Conversations, messages, AI chat (sync/stream) |
| Ingest     | `/ingest`| File and text ingest (auth required)       |
| Vector     | `/vector`| Similarity / semantic search               |
| RAG        | `/rag`   | RAG query with optional filters            |
| Vision     | `/vision`| Image upload → describe + store            |
| Health     | —        | `GET /health`                              |

Interactive docs: **`/docs`** (Swagger), **`/redoc`** (ReDoc).

## Requirements

- Python 3.13+  
- PostgreSQL (for auth and chat data)  
- Optional: Ollama (for local text/vision models and embeddings)  
- API keys: OpenAI; Groq (if using Groq models)  

## Setup

```bash
uv sync
# or: pip install -e .
```

Copy `.env.example` to `.env` (or create `.env`) and set at least:

- `DB_*` (user, password, host, port, name)  
- `JWT_SECRET_KEY`  
- `OPENAI_API_KEY`  
- `GROQ_API_KEY` (if using Groq)  
- `OLLAMA_ENABLED` (e.g. `1` or `0`)  

Run migrations:

```bash
alembic upgrade head
```

## Run

```bash
uvicorn main:app --reload
```

API: **http://localhost:8000** — Docs: **http://localhost:8000/docs**.

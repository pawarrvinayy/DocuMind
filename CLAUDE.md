# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Stack

- **Backend**: FastAPI (Python 3.12), SQLAlchemy 2 async, Alembic, pgvector
- **Frontend**: React 18 + TypeScript + Tailwind CSS, Vite, TanStack Query, Zustand
- **Database**: PostgreSQL 16 with pgvector extension
- **AI**: OpenAI `text-embedding-3-small` (embeddings) + `gpt-4o` (Q&A)
- **Billing**: Stripe
- **Local dev**: Docker Compose

## Commands

### Docker (recommended)
```bash
cp .env.example .env          # fill in API keys
docker compose up --build     # starts db + backend (8000) + frontend (5173)
```

### Backend (local)
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload  # http://localhost:8000
alembic upgrade head           # run migrations
```

### Frontend (local)
```bash
cd frontend
npm install
npm run dev     # http://localhost:5173
npm run build
npm run lint
npm test        # vitest
```

### Single backend test
```bash
cd backend && pytest tests/path/to/test_file.py::test_function_name -v
```

## Architecture

### Backend (`backend/app/`)
- `main.py` — FastAPI app, CORS middleware, router registration, `lifespan` runs `init_db()`
- `config.py` — `pydantic-settings` `Settings` singleton; all env vars live here
- `database.py` — async SQLAlchemy engine, `Base` declarative class, `init_db()` creates pgvector extension + tables
- `dependencies.py` — `get_db` (session injection), `get_current_user_id` (JWT bearer → user ID)
- `models/` — SQLAlchemy ORM: `User`, `Document`, `DocumentChunk` (stores `Vector(1536)`), `Subscription`
- `schemas/` — Pydantic request/response models
- `routers/` — thin HTTP layer: `auth`, `documents`, `qa`, `billing`
- `services/` — business logic:
  - `pdf_processor.py` — PDF → tiktoken chunks → embeddings → DB rows
  - `embeddings.py` — OpenAI `text-embedding-3-small` batch calls
  - `vector_store.py` — pgvector cosine-distance similarity search
  - `llm.py` — GPT-4o with retrieved chunks as context, returns `(answer, sources)`
- `utils/security.py` — bcrypt password hashing, JWT encode/decode

### Frontend (`frontend/src/`)
- `main.tsx` — React root, wraps app in `QueryClientProvider` + `BrowserRouter`
- `services/api.ts` — axios instance with `/api` base URL (Vite proxies to `localhost:8000`) and JWT interceptor
- `components/` — reusable UI atoms
- `pages/` — route-level views
- `hooks/` — custom React hooks
- `types/` — shared TypeScript interfaces

### Data flow for Q&A
1. User uploads PDF → `POST /documents` → `pdf_processor` chunks + embeds → stored in `document_chunks` with pgvector column
2. User asks question → `POST /qa/ask` → `vector_store` cosine search → top-5 chunks → `llm` sends to GPT-4o → cited answer returned

## Git Workflow
After every completed feature: `git add`, conventional commit (`feat:`, `fix:`, `chore:`), push to `main`.

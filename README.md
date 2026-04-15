# GenReader

> AI-driven PDF / image text recognition & coordinate localization, powered by vision-language models (Qwen-VL).

Full-stack implementation of the plan in [PLAN.md](./PLAN.md).

## Stack

- **Backend**: FastAPI + SQLAlchemy (async) + arq + PostgreSQL + Redis + MinIO
- **Frontend**: Next.js 16 (App Router) + React 19 + Tailwind v4 + shadcn/ui
- **ML**: Local Qwen-VL via `transformers`, PaddleOCR fallback
- **Infra**: Docker Compose (dev + prod)

## Quick start

```bash
# 1. Copy env files
cp backend/.env.example backend/.env
cp frontend/.env.local.example frontend/.env.local

# 2. Start full stack
docker compose up -d --build

# 3. Open
# Frontend:  http://localhost:3000
# Backend:   http://localhost:8000/docs
# MinIO:     http://localhost:9001  (minioadmin/minioadmin)
```

## Local dev

```bash
# Backend (uv)
cd backend
uv sync
uv run uvicorn app.main:app --reload
uv run arq app.workers.arq_worker.WorkerSettings

# Frontend
cd frontend
pnpm install
pnpm dev
```

## Auth (MVP)

The MVP ships with a single fake user (`demo@genreader.local` / password `demo`) seeded on startup. Login issues a JWT that the frontend stores and sends with every request. Real signup is not wired — see `PLAN.md` §7.3.

## Layout

See [PLAN.md §4](./PLAN.md) for the full directory tree.

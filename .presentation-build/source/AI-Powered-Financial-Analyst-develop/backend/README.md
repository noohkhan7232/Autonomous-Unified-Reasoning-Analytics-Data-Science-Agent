# Backend

FastAPI service. Owns authentication, persistence, request orchestration, and
exposes the REST API the frontend consumes. Contains **no model training
code** — it imports and calls functions from `ai/` for inference only.

| Folder | Purpose |
|---|---|
| `app/api/v1/endpoints/` | One file per resource (health, auth, tickers, predictions, decisions, chat, reports) |
| `app/core/` | Config, security (JWT), settings |
| `app/models/` | SQLAlchemy ORM models |
| `app/schemas/` | Pydantic request/response schemas |
| `app/services/` | Business logic, orchestrates `ai/` module calls |
| `app/db/` | Session management, Alembic migrations |
| `app/utils/` | Shared helpers |
| `tests/` | Pytest suite (mirrors `app/` structure) |

Run locally: `pip install -r requirements.txt && uvicorn app.main:app --reload`
(or via `docker compose up backend`).

API docs (Swagger) available at `/docs` once running.

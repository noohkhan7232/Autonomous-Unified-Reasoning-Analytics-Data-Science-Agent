# AI-Powered Financial Analyst & Investment Decision Support System

An AI-powered platform that combines Machine Learning, Deep Learning, Time
Series Forecasting, NLP, and LLMs to analyze historical market data and
financial news, and generate explainable investment insights.

> **Educational & research use only. Nothing in this system constitutes
> financial advice.** Every prediction and every AI-generated explanation
> carries an explicit disclaimer, enforced at the API level.

## Status

**Phase 1 — Architecture & Scaffolding.** See
[`docs/architecture/ARCHITECTURE.md`](docs/architecture/ARCHITECTURE.md) for
the full system design. No feature modules are implemented yet — this repo
currently contains the project skeleton only.

## Architecture at a glance

```
Historical Data → Feature Engineering → [ML | Time Series | Deep Learning]
   → Prediction Engine → News Sentiment (FinBERT) → Decision Support Engine
   → LLM Explanation Layer → React Dashboard
```

Full diagram and rationale: [`docs/architecture/ARCHITECTURE.md`](docs/architecture/ARCHITECTURE.md)

## Repository structure

```
frontend/     React + Tailwind dashboard
backend/      FastAPI service (auth, REST API, orchestration)
ai/           ML / DL / time-series / NLP / decision-engine / LLM modules
datasets/     Raw / processed / external data (not committed)
docs/         Architecture, API, and research documentation
tests/        Cross-cutting integration tests
deployment/   Docker, Nginx, CI reference configs
scripts/      One-off operational scripts
storage/      Runtime artifacts — trained models, logs, reports (not committed)
```

Each top-level folder has its own `README.md` explaining its contents.

## Tech stack

| Layer | Stack |
|---|---|
| Frontend | React, Tailwind CSS, React Router, Axios, Chart.js, Recharts |
| Backend | FastAPI, Pydantic, SQLAlchemy, JWT auth |
| Database | PostgreSQL (+ Redis, optional) |
| ML | scikit-learn, XGBoost |
| Deep Learning | TensorFlow / PyTorch |
| Time Series | statsmodels, Prophet |
| NLP | HuggingFace Transformers, FinBERT |
| LLM | Gemini / Groq / OpenRouter (explanation layer only) |
| Deployment | Docker, GitHub Actions, Nginx |

## Getting started (local dev)

```bash
cp .env.example .env        # fill in secrets / API keys
docker compose up --build   # postgres + redis + backend + frontend
```

- Backend: http://localhost:8000/docs
- Frontend: http://localhost:5173

Run tests:

```bash
pytest backend/tests
pytest ai/tests
cd frontend && npm test
```

## Git workflow

`feature/*` → `develop` → CI → `main`. Never push directly to `main`. See
[`CONTRIBUTING.md`](CONTRIBUTING.md) for full branching and commit conventions.

## Roadmap

1. ✅ Architecture & repo scaffolding
2. Database schema design (PostgreSQL, Alembic migrations)
3. Backend API implementation (auth, tickers, predictions)
4. Frontend implementation (dashboard, auth, chat)
5. Data collection (Module 1 — Yahoo Finance default)
6. Feature engineering (Module 2)
7. ML / Time Series / Deep Learning models (Modules 3–5)
8. News sentiment (Module 6 — FinBERT)
9. Decision Support Engine (Module 7)
10. LLM explanation layer (Module 8)
11. Testing, deployment, documentation

# System Architecture — AI-Powered Financial Analyst & Investment Decision Support System

Status: **Phase 1 — Architecture & Scaffolding**
Owner: shdbfrz
Last updated: 2026-07-10

---

## 1. Purpose

Define the target system architecture, module boundaries, data flow, and repository layout
before any feature code is written, so that every subsequent module (data collection,
feature engineering, ML/DL/time-series models, sentiment analysis, decision engine, LLM
explanation layer, dashboard) is built against a stable contract instead of being retrofitted.

This document is the single source of truth for architectural decisions. Any change to
module boundaries, data contracts, or the tech stack must be reflected here first.

---

## 2. Guiding Principles

1. **Separation of concerns** — `ai/` (models & research code) is fully decoupled from
   `backend/` (serving layer). The backend never contains model training logic; it only
   loads trained artifacts and calls inference functions.
2. **LLM only explains, never predicts.** The LLM layer (Module 8) is never allowed to
   output a price, a probability, or a buy/sell signal on its own — it consumes the
   Decision Support Engine's output and turns it into natural language.
3. **Reproducibility** — every model run is versioned (data snapshot + code commit + model
   artifact) so predictions can be traced back to the exact pipeline that produced them.
4. **Educational-use guardrails** — every prediction and every LLM response must carry an
   explicit "not financial advice" disclaimer end-to-end (enforced in the Decision Support
   Engine, not just the frontend).
5. **Swap-ability** — data providers (Module 1) and LLM providers (Module 8) are behind
   thin adapter interfaces so the underlying vendor can change without touching consumers.

---

## 3. High-Level Architecture

```
                         ┌───────────────────────┐
                         │   Historical Data      │  Module 1
                         │ (Yahoo/AlphaVantage/   │
                         │  Polygon/TwelveData)   │
                         └───────────┬────────────┘
                                     ▼
                         ┌───────────────────────┐
                         │  Feature Engineering   │  Module 2
                         │ (MA, EMA, RSI, MACD,   │
                         │  Bollinger, ATR, etc.) │
                         └───────────┬────────────┘
              ┌──────────────────────┼──────────────────────┐
              ▼                      ▼                      ▼
   ┌────────────────────┐ ┌────────────────────┐ ┌────────────────────┐
   │  Machine Learning   │ │    Time Series      │ │   Deep Learning     │  Module 3/4/5
   │  (RF / XGB / etc.)  │ │  (ARIMA/SARIMA/     │ │   (LSTM/GRU/        │
   │                     │ │   Prophet)          │ │    Transformer)     │
   └──────────┬──────────┘ └──────────┬──────────┘ └──────────┬──────────┘
              └──────────────────────┼──────────────────────┘
                                     ▼
                         ┌───────────────────────┐
                         │   Prediction Engine    │
                         │ (ensembling & storage) │
                         └───────────┬────────────┘
                                     ▼
                         ┌───────────────────────┐
                         │   Financial News       │
                         └───────────┬────────────┘
                                     ▼
                         ┌───────────────────────┐
                         │  FinBERT Sentiment     │  Module 6
                         └───────────┬────────────┘
                                     ▼
                         ┌───────────────────────┐
                         │ Decision Support Engine│  Module 7
                         │ (confidence, risk,     │
                         │  buy/hold/sell)        │
                         └───────────┬────────────┘
                                     ▼
                         ┌───────────────────────┐
                         │  LLM Explanation Layer │  Module 8
                         │ (Gemini/Groq/OpenRtr)  │
                         │  — explains only —     │
                         └───────────┬────────────┘
                                     ▼
                         ┌───────────────────────┐
                         │   FastAPI Backend      │
                         │  (auth, REST API,      │
                         │   orchestration)       │
                         └───────────┬────────────┘
                                     ▼
                         ┌───────────────────────┐
                         │   React Dashboard      │
                         └───────────────────────┘
```

---

## 4. Component Responsibilities

| Layer | Responsibility | Lives in | Talks to |
|---|---|---|---|
| Data Collection | Pull OHLCV + fundamentals from providers, normalize schema | `ai/data_collection/` | External APIs → `datasets/raw/` |
| Feature Engineering | Compute indicators, lag features, rolling stats | `ai/feature_engineering/` | `datasets/raw/` → `datasets/processed/` |
| ML / Time Series / DL | Train & serve predictive models | `ai/models/{ml,time_series,deep_learning}/` | `datasets/processed/` → `storage/models/` |
| NLP / Sentiment | News classification, summarization, FinBERT scoring | `ai/nlp/` | News API → sentiment scores |
| Decision Engine | Aggregate predictions + sentiment into confidence/risk/signal | `ai/decision_engine/` | model outputs + sentiment → structured decision object |
| LLM Layer | Turn structured decision objects into natural language | `ai/llm/` | Decision Engine output → text |
| Backend API | Auth, request orchestration, persistence, rate limiting | `backend/app/` | PostgreSQL, Redis, `ai/` modules |
| Frontend | Dashboard, auth UI, chat interface, reports | `frontend/src/` | Backend REST API |

---

## 5. Data Flow (Request Lifecycle Example: "Analyze AAPL")

1. User requests analysis for `AAPL` via React dashboard.
2. Backend `/api/v1/analysis/{ticker}` endpoint receives request, checks Redis cache.
3. If cache miss: backend triggers the AI pipeline (data collection → feature engineering →
   ML/TS/DL inference) either synchronously (for cached/recent data) or via a background job.
4. Prediction Engine ensembles outputs from the three model families into a single
   probabilistic forecast + confidence interval.
5. Latest news for the ticker is pulled, scored with FinBERT.
6. Decision Support Engine combines forecast + sentiment + risk metrics into a structured
   decision object: `{ signal, confidence_score, risk_score, disclaimer, drivers[] }`.
7. LLM Layer receives that structured object (not raw data) and generates a plain-English
   explanation — it cannot alter the signal, only narrate it.
8. Backend persists the result, returns JSON to frontend.
9. Frontend renders charts (Recharts/Chart.js), the decision card, and makes the explanation
   available in the AI Chatbot panel.

---

## 6. Database Design (Phase 2 preview — not yet implemented)

Core entities to be formalized in Phase 2 (Database Design):
`User`, `Ticker`, `PricePoint`, `FeatureSnapshot`, `ModelRun`, `Prediction`,
`NewsArticle`, `SentimentScore`, `Decision`, `PortfolioHolding`, `Report`, `ChatSession`.

This file will be superseded by `docs/architecture/DATABASE_SCHEMA.md` once Phase 2 begins.

---

## 7. Technology Stack (confirmed)

| Concern | Choice |
|---|---|
| Frontend | React, Tailwind CSS, React Router, Axios, Chart.js, Recharts |
| Backend | FastAPI, Pydantic, SQLAlchemy (async) |
| Auth | JWT (access + refresh tokens) |
| Database | PostgreSQL |
| Cache/Queue | Redis (optional in dev, recommended in prod) |
| ML | scikit-learn, XGBoost |
| DL | TensorFlow or PyTorch (pick one per model, documented per-module) |
| Time Series | statsmodels, Prophet |
| NLP | HuggingFace Transformers, FinBERT |
| LLM | Gemini / Groq / OpenRouter (adapter pattern, swappable) |
| Deployment | Docker, Docker Compose, GitHub Actions, Nginx |

---

## 8. Environments

- **development** — Docker Compose (Postgres + Redis + backend + frontend locally).
- **staging** — mirrors production, used for pre-release testing on `develop` branch merges.
- **production** — deployed from `main` only, behind Nginx reverse proxy.

---

## 9. Non-Functional Requirements

- **Scalability**: stateless backend containers behind a load balancer; model inference can
  be moved to a separate worker service later without changing the API contract.
- **Security**: secrets via environment variables / secret manager, never committed. JWT
  short-lived access tokens + refresh rotation. Input validation via Pydantic everywhere.
- **Observability**: structured logging to `storage/logs/` in dev, shipped to a log
  aggregator in prod (to be selected in the deployment phase).
- **Compliance / Disclaimer**: every prediction-bearing API response must include an
  `educational_disclaimer` field; this is enforced at the schema level, not just in the UI.

---

## 10. Open Decisions (to revisit)

- TensorFlow vs PyTorch for the deep learning module — decide when Module 5 is scheduled.
- Redis: optional for MVP, but recommended once background jobs (Celery/RQ) are introduced.
- Task queue for long-running model training (Celery vs RQ vs FastAPI `BackgroundTasks`) —
  decide when Decision Engine needs async retraining.

---

## 11. Next Steps (Phase 1 remainder)

1. Database schema design (PostgreSQL) — entities above, ERD, migrations via Alembic.
2. Backend skeleton — FastAPI app factory, config, health check, auth scaffolding.
3. Frontend skeleton — Vite + React + Tailwind, routing shell, auth pages.
4. Module 1 (Data Collection) implementation — starting with Yahoo Finance (`yfinance`) as
   the default free provider, with the adapter interface ready for Alpha Vantage / Polygon /
   Twelve Data.

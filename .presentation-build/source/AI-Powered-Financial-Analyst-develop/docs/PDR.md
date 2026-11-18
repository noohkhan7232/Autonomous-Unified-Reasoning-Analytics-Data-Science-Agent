# Project Definition & Design Report (PDR)

**Project Title:** AI-Powered Financial Analyst and Investment Decision Support System
**Degree:** Bachelor of Technology (B.Tech), Computer Science Engineering — Artificial Intelligence and Machine Learning
**Project Type:** Final Year Major Project
**Duration:** Approximately 6–8 months
**Repository:** https://github.com/shdbfrz/AI-Powered-Financial-Analyst
**Document Status:** Draft v1.0 — for professor review and team alignment

---

## 1. Introduction

### 1.1 Problem Statement

Individual investors and students of finance frequently lack access to the kind of
multi-signal, explainable analysis that institutional trading desks use. Existing
retail tools either give raw charts with no interpretation, or paid "black box"
tips with no reasoning shown. There is a gap for a platform that:

- combines classical ML, time-series, and deep-learning forecasts,
- factors in real news sentiment,
- and — critically — **explains its reasoning in plain language** rather than just
  emitting a number.

### 1.2 Proposed Solution

An AI-powered financial analysis and investment decision-support platform that
ingests historical market data and financial news, runs an ensemble of predictive
models, scores news sentiment with FinBERT, aggregates everything into a
confidence-scored Buy/Hold/Sell signal with a risk score, and uses an LLM purely
as an **explanation layer** (never as the predictor) to make the reasoning
understandable to a non-expert user through a chatbot and dashboard.

### 1.3 Intended Use

**Educational and research purposes only.** The system explicitly does not provide
licensed financial advice; every prediction-bearing response carries a disclaimer,
enforced at the API schema level, not just in the UI copy.

---

## 2. Objectives

1. Collect and clean historical stock market data from multiple providers.
2. Engineer a robust technical-indicator feature set.
3. Train and compare Machine Learning, Time Series, and Deep Learning forecasting
   models.
4. Collect and classify financial news, scoring sentiment with FinBERT.
5. Build a Decision Support Engine that aggregates forecasts + sentiment into a
   confidence score, risk score, and Buy/Hold/Sell signal.
6. Build an LLM explanation layer that narrates decisions, answers financial
   questions, and generates reports — without ever generating its own predictions.
7. Build an interactive React dashboard with authentication, portfolio views,
   and an AI chatbot.
8. Deliver the system as a scalable, containerized, CI/CD-tested application
   suitable for a GitHub portfolio, technical interviews, and potential extension
   into a SaaS product or research paper.

---

## 3. Scope

### 3.1 In Scope

- Historical data ingestion (Yahoo Finance default; Alpha Vantage, Polygon,
  Twelve Data as pluggable alternatives).
- Technical indicator feature engineering.
- ML models: Linear Regression, Random Forest, XGBoost (LightGBM/CatBoost optional).
- Time series models: ARIMA, SARIMA, Prophet.
- Deep learning models: LSTM, GRU (Transformer optional).
- News sentiment via FinBERT; news classification and summarization.
- Decision Support Engine: prediction aggregation, confidence score, risk score,
  Buy/Hold/Sell signal, portfolio suggestions, disclaimer.
- LLM explanation layer (Gemini / Groq / OpenRouter, swappable).
- React dashboard: auth, ticker analysis views, portfolio risk view, AI chat,
  report generation/export.
- Dockerized deployment with GitHub Actions CI and Nginx reverse proxy.

### 3.2 Out of Scope

- Real brokerage integration / live order execution.
- Licensed financial advisory features (regulatory compliance beyond the
  educational disclaimer).
- High-frequency / intraday trading (system targets daily-and-above timeframes).
- Mobile native apps (web dashboard only, for this project's timeline).

See `MVP.md` for what ships in the first functional milestone versus the full
vision above.

---

## 4. System Architecture

```
Historical Data → Feature Engineering → [ML | Time Series | Deep Learning]
   → Prediction Engine → News Sentiment (FinBERT) → Decision Support Engine
   → LLM Explanation Layer → React Dashboard
```

Full component breakdown, data flow, and design rationale:
[`docs/architecture/ARCHITECTURE.md`](architecture/ARCHITECTURE.md).

### 4.1 Guiding Design Principles

- **Separation of concerns** — `ai/` (research/modeling) is fully decoupled from
  `backend/` (serving layer); the backend never trains models, only invokes
  inference.
- **LLM explains, never predicts** — structurally enforced: the LLM layer only
  ever receives an already-computed decision object, never raw price data.
- **Reproducibility** — every model run is traceable to a data snapshot + code
  commit + model artifact.
- **Provider swap-ability** — data providers and LLM providers sit behind thin
  adapter interfaces.

---

## 5. Technology Stack

| Layer | Technology |
|---|---|
| Frontend | React, Tailwind CSS, React Router, Axios, Chart.js, Recharts |
| Backend | FastAPI, Pydantic, SQLAlchemy (async) |
| Auth | JWT |
| Database | PostgreSQL (+ Redis, optional) |
| ML | scikit-learn, XGBoost |
| Deep Learning | TensorFlow / PyTorch |
| Time Series | statsmodels, Prophet |
| NLP | HuggingFace Transformers, FinBERT |
| LLM | Gemini, Groq, OpenRouter |
| Deployment | Docker, Docker Compose, GitHub Actions, Nginx |

---

## 6. Project Structure

```
frontend/     React + Tailwind dashboard
backend/      FastAPI service (auth, REST API, orchestration)
ai/           ML / DL / time-series / NLP / decision-engine / LLM modules
datasets/     Raw / processed / external data (not committed)
docs/         Architecture, API, and research documentation
tests/        Cross-cutting integration tests
deployment/   Docker, Nginx, CI configs
scripts/      One-off operational scripts
storage/      Runtime artifacts — trained models, logs, reports (not committed)
```

---

## 7. Team & Roles

| Role | Responsibility | Assigned to |
|---|---|---|
| Project Lead / Backend | Architecture, FastAPI, auth, DB, orchestration | *TBD* |
| AI/ML Engineer | Modules 1–5 (data, features, ML/TS/DL models) | *TBD* |
| NLP/LLM Engineer | Modules 6–8 (sentiment, decision engine, LLM layer) | *TBD* |
| Frontend Engineer | React dashboard, chat UI, reports | *TBD* |
| DevOps / QA | Docker, CI/CD, testing strategy | *TBD* |

*(Fill in names before submitting to professor / sharing with teammates.)*

### Git Workflow

`feature/*` → `develop` → CI tests → `main`. Never push directly to `main`,
never merge without passing tests. Full conventions in `CONTRIBUTING.md`.

---

## 8. Timeline (High-Level, 6–8 Months)

| Phase | Milestone | Approx. Duration |
|---|---|---|
| 1 | Architecture, DB design, repo scaffolding | 2 weeks |
| 2 | Backend API skeleton + auth | 2 weeks |
| 3 | Frontend skeleton + routing | 2 weeks |
| 4 | Data collection (Module 1) | 2 weeks |
| 5 | Feature engineering (Module 2) | 2 weeks |
| 6 | ML models (Module 3) | 3 weeks |
| 7 | Time series models (Module 4) | 2 weeks |
| 8 | Deep learning models (Module 5) | 3 weeks |
| 9 | Sentiment analysis (Module 6) | 2 weeks |
| 10 | Decision Support Engine (Module 7) | 2 weeks |
| 11 | LLM explanation layer (Module 8) | 2 weeks |
| 12 | Dashboard integration | 2 weeks |
| 13 | Testing, hardening, documentation | 2 weeks |
| 14 | Deployment, final report, demo prep | 2 weeks |

A detailed phase-by-phase task breakdown belongs in a shared tracker
(GitHub Projects / Jira) — this table is the milestone-level view for the
professor.

---

## 9. Expected Outcomes / Deliverables

- A working, containerized, publicly demoable web application.
- A GitHub repository with clean history, CI, and full documentation
  (this PDR, `SRS.md`, `MVP.md`, `ARCHITECTURE.md`, module READMEs).
- A final project report suitable for academic submission, extractable from
  this documentation set.
- A system that is portfolio-ready and technical-interview-ready.

---

## 10. Risks & Mitigations

| Risk | Mitigation |
|---|---|
| Free-tier data provider rate limits | Adapter pattern allows switching provider; cache responses in Redis |
| Model accuracy insufficient for a compelling demo | Ensemble multiple model families; be transparent about confidence intervals rather than overselling accuracy |
| LLM hallucinating predictions instead of explaining | Structurally pass only the pre-computed decision object to the LLM, never raw data — enforced in code, not just prompting |
| Scope too large for timeline | MVP document (`MVP.md`) defines the minimum slice that proves the concept end-to-end first |
| Team member availability / bus factor | Modular architecture (Modules 1–8) allows parallel, independent ownership |

---

## 11. References / Related Work

*(To be filled in during literature review — cite relevant papers on stock
prediction with ML/DL, FinBERT, and LLM-based financial explanation systems.)*

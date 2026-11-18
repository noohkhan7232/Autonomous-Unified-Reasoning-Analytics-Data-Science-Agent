# Software Requirements Specification (SRS)

**Project:** AI-Powered Financial Analyst and Investment Decision Support System
**Version:** 1.0
**Prepared for:** Academic submission (B.Tech Final Year Project) and project team
**Related documents:** `PDR.md` (project definition & design), `MVP.md` (MVP scope),
`architecture/ARCHITECTURE.md` (system architecture)

---

## 1. Introduction

### 1.1 Purpose

This document specifies the functional and non-functional requirements of the
AI-Powered Financial Analyst and Investment Decision Support System. It is
intended for the project supervisor (for evaluation) and the development team
(as the requirements baseline all modules are built against).

### 1.2 Scope

The system collects historical market data and financial news, applies ML/DL/
time-series forecasting and NLP sentiment analysis, aggregates results into an
explainable investment signal, and presents it through a web dashboard with an
AI chat interface. The system is for **educational and research use only** and
must not be presented as licensed financial advice.

### 1.3 Definitions, Acronyms, Abbreviations

| Term | Definition |
|---|---|
| OHLCV | Open, High, Low, Close, Volume — standard price bar data |
| ML | Machine Learning |
| DL | Deep Learning |
| NLP | Natural Language Processing |
| LLM | Large Language Model |
| FinBERT | BERT model fine-tuned for financial sentiment classification |
| MVP | Minimum Viable Product |
| JWT | JSON Web Token |
| API | Application Programming Interface |
| Signal | The system's Buy / Hold / Sell output for a ticker |
| Decision object | Structured output of the Decision Support Engine consumed by the LLM layer |

### 1.4 References

- Project brief (internal): role/scope/module definitions provided by project owner.
- `docs/PDR.md`, `docs/MVP.md`, `docs/architecture/ARCHITECTURE.md`.

### 1.5 Overview

Section 2 describes the product at a high level. Section 3 lists detailed
functional requirements per module. Section 4 covers external interface
requirements. Section 5 covers non-functional requirements. Section 6 lists
constraints and assumptions.

---

## 2. Overall Description

### 2.1 Product Perspective

A new, self-contained web application (not an extension of an existing
system), composed of a React frontend, a FastAPI backend, and a decoupled
`ai/` research/modeling layer, backed by PostgreSQL and optionally Redis.

### 2.2 Product Functions (Summary)

1. Collect and clean historical stock data.
2. Engineer technical-indicator features.
3. Train/serve ML, time-series, and DL forecasting models.
4. Collect and score financial news sentiment (FinBERT).
5. Aggregate forecasts + sentiment into a confidence-scored decision.
6. Explain the decision in natural language via an LLM (never predicts).
7. Present results, charts, and chat in a React dashboard.
8. Authenticate users via JWT.
9. Generate downloadable reports.

### 2.3 User Characteristics

| User type | Description | Technical level |
|---|---|---|
| Student / retail investor (end user) | Wants to understand a ticker's outlook and why | Non-technical |
| Project supervisor | Evaluates correctness, rigor, and documentation | Technical/academic |
| Teammate / developer | Builds and extends modules | Technical |

### 2.4 Constraints

- Must use the specified tech stack (see `PDR.md` §5) — no substitutions
  without documenting the trade-off first, per project rules.
- Must never let the LLM layer output a prediction — only explanations of a
  pre-computed decision object.
- Must carry an educational disclaimer on every prediction-bearing response.
- Free-tier API constraints (data providers, LLM providers) bound request
  volume and must be respected (caching, rate limiting).

### 2.5 Assumptions and Dependencies

- Yahoo Finance (`yfinance`) remains freely accessible without an API key.
- At least one of Gemini / Groq / OpenRouter offers a usable free tier for
  development and demo purposes.
- Team has access to a machine capable of running Docker Compose locally
  (Postgres + Redis + backend + frontend containers).

---

## 3. Functional Requirements

Each requirement is tagged `FR-<module>-<n>` for traceability into test cases
and code (mirrors the module numbering already used across `PDR.md` and the
architecture doc).

### 3.1 Module 1 — Historical Data Collection

- **FR-1.1**: The system shall retrieve historical OHLCV data for a given
  ticker and date range from a configurable provider (default: Yahoo Finance).
- **FR-1.2**: The system shall support switching providers (Alpha Vantage,
  Polygon, Twelve Data) via configuration without code changes to consumers,
  through a common provider interface.
- **FR-1.3**: The system shall persist raw pulled data to `datasets/raw/` for
  reproducibility, keyed by provider + ticker + date range.
- **FR-1.4**: The system shall handle provider errors/rate limits gracefully
  and surface a clear error to the caller rather than failing silently.

### 3.2 Module 2 — Feature Engineering

- **FR-2.1**: The system shall compute, at minimum: Moving Average, EMA, RSI,
  MACD, Bollinger Bands, ATR, Momentum, Volatility, Lag Features, and Rolling
  Statistics from raw OHLCV data.
- **FR-2.2**: The system shall output a clean, model-ready feature DataFrame
  with documented column names and no unhandled NaNs at the training window.
- **FR-2.3**: The system shall version processed datasets so a given model run
  can be traced back to the exact feature set used.

### 3.3 Module 3 — Machine Learning

- **FR-3.1**: The system shall train and evaluate at least: Linear Regression,
  Random Forest, and XGBoost on the engineered features.
- **FR-3.2**: The system shall report standard regression/classification
  metrics (e.g. RMSE, MAE, accuracy/F1 as applicable) per model.
- **FR-3.3**: The system shall persist trained model artifacts to
  `storage/models/` with a version identifier.

### 3.4 Module 4 — Time Series

- **FR-4.1**: The system shall support ARIMA and SARIMA forecasting.
- **FR-4.2**: The system shall support Facebook Prophet forecasting as an
  alternative/comparison model.
- **FR-4.3**: The system shall report forecast confidence intervals, not just
  point estimates.

### 3.5 Module 5 — Deep Learning

- **FR-5.1**: The system shall support LSTM and GRU sequence models for price
  forecasting.
- **FR-5.2**: The system shall support configurable lookback windows and
  forecast horizons.
- **FR-5.3**: The system shall persist trained DL model weights with
  versioning, mirroring FR-3.3.
- **FR-5.4**: The system shall reshape engineered features into fixed-length
  sequences `(samples, timesteps, features)` before training/inference — this
  windowing step is specific to Module 5 and is not part of Module 2's output.
- **FR-5.5**: The system shall scale sequence inputs (e.g. MinMax or Standard
  scaling) prior to feeding an LSTM/GRU, since — unlike the tree-based models
  in Module 3 — these architectures are sensitive to input scale.
- **FR-5.6**: The system shall train and report metrics for both LSTM and GRU
  on the same data split, so their performance can be directly compared rather
  than committing to one architecture without evidence.
- **FR-5.7 (optional)**: The system may support a Transformer-based sequence
  model, attempted only after LSTM/GRU are working and only if it demonstrably
  outperforms them on the same evaluation split — it is not a default
  requirement given the added data/tuning cost.

**Design note — framework choice (TensorFlow vs PyTorch):** Both are listed as
supported in the tech stack; the team should pick one per model and document
the choice here once made. TensorFlow/Keras trades off faster initial
implementation for less transparency; PyTorch trades off more boilerplate for
easier debugging and closer alignment with typical research code (relevant if
this project is later extended into a research paper). This decision is
tracked as an open item in `architecture/ARCHITECTURE.md` §10 and should be
resolved before FR-5.1 implementation begins.

### 3.6 Module 6 — NLP / News Sentiment

- **FR-6.1**: The system shall collect recent financial news articles relevant
  to a given ticker.
- **FR-6.2**: The system shall score each article's sentiment using FinBERT
  (positive/negative/neutral + confidence).
- **FR-6.3**: The system shall classify and (optionally) summarize news
  articles for display and for input to the Decision Support Engine.

### 3.7 Module 7 — Decision Support Engine

- **FR-7.1**: The system shall aggregate model predictions (ML + Time Series +
  DL) into a single ensembled forecast.
- **FR-7.2**: The system shall combine the ensembled forecast with sentiment
  score and a risk/volatility measure into: `signal` (Buy/Hold/Sell),
  `confidence_score`, `risk_score`.
- **FR-7.3**: The system shall attach an `educational_disclaimer` field to
  every decision object — this field is mandatory, not optional, at the schema
  level.
- **FR-7.4**: The system shall (post-MVP) generate simple portfolio-level
  suggestions from multiple ticker decisions.

### 3.8 Module 8 — LLM Explanation Layer

- **FR-8.1**: The system shall generate a natural-language explanation of a
  given decision object using a configurable LLM provider (Gemini / Groq /
  OpenRouter).
- **FR-8.2**: The LLM layer shall receive only the structured decision object
  (and supporting context such as the indicator values that drove it) — **it
  shall never receive raw historical data with an instruction to predict, and
  shall never be permitted to alter the signal, confidence, or risk score.**
- **FR-8.3**: The system shall support LLM-driven news summarization, technical
  indicator explanations, investment-risk explanations, and portfolio report
  generation as explanation-only capabilities.
- **FR-8.4**: The system shall support a conversational chat interface backed
  by the LLM layer, scoped to explaining already-computed system outputs.

### 3.9 Backend / Platform

- **FR-9.1**: The system shall support user registration and login via JWT
  (access + refresh tokens).
- **FR-9.2**: The system shall expose a versioned REST API (`/api/v1/...`)
  documented via FastAPI's automatic OpenAPI/Swagger UI.
- **FR-9.3**: The system shall persist users, predictions, and decisions in
  PostgreSQL.
- **FR-9.4**: The system shall cache expensive/rate-limited calls (data
  provider, LLM) in Redis where configured.

### 3.10 Frontend

- **FR-10.1**: The system shall provide login/registration pages.
- **FR-10.2**: The system shall provide a ticker analysis view showing a price
  chart, the decision card (signal/confidence/risk/disclaimer), and the LLM
  explanation.
- **FR-10.3**: The system shall provide an AI chat panel for follow-up
  questions about the displayed analysis.
- **FR-10.4**: The system shall (post-MVP) provide a portfolio view and report
  export/download.

---

## 4. External Interface Requirements

### 4.1 User Interfaces
- Responsive web UI (desktop-first, per React + Tailwind stack), accessible via
  modern browsers (Chrome, Firefox, Edge, Safari — latest two major versions).

### 4.2 Hardware Interfaces
- None beyond a standard client device with a browser and internet connection.

### 4.3 Software Interfaces
- **Data provider APIs**: Yahoo Finance (via `yfinance`), Alpha Vantage,
  Polygon, Twelve Data (REST, JSON).
- **News API**: TBD provider, REST/JSON.
- **LLM provider APIs**: Gemini, Groq, OpenRouter (REST, JSON, key-authenticated).
- **Database**: PostgreSQL via SQLAlchemy (async).
- **Cache**: Redis (optional).

### 4.4 Communication Interfaces
- HTTPS for all client-backend and backend-third-party communication in
  staging/production. HTTP acceptable only for local development.

---

## 5. Non-Functional Requirements

### 5.1 Performance
- **NFR-1**: A single-ticker analysis request (cache miss) should complete
  within a few seconds for MVP-scope models; longer-running training jobs
  should be handled asynchronously, not block the request thread.
- **NFR-2**: Cached (repeat) analysis requests should return in well under a
  second.

### 5.2 Security
- **NFR-3**: Passwords shall be hashed (bcrypt via passlib), never stored in
  plaintext.
- **NFR-4**: JWT access tokens shall be short-lived; refresh tokens shall
  support rotation.
- **NFR-5**: All secrets (API keys, DB credentials, JWT secret) shall be
  supplied via environment variables and never committed to version control.
- **NFR-6**: All request/response schemas shall be validated via Pydantic.

### 5.3 Reliability & Availability
- **NFR-7**: External provider failures (data or LLM) shall degrade gracefully
  (clear error message) rather than crash the request pipeline.

### 5.4 Maintainability
- **NFR-8**: Code shall follow SOLID principles, be modular, type-hinted, and
  independently testable per the project's coding standards.
- **NFR-9**: Every top-level module/folder shall have a `README.md` explaining
  its purpose (already satisfied by the current scaffold).

### 5.5 Scalability
- **NFR-10**: The backend shall be stateless so it can run as multiple
  container replicas behind a load balancer without code changes.

### 5.6 Compliance / Ethical Use
- **NFR-11**: Every prediction-bearing API response shall include an
  `educational_disclaimer` field; this is enforced at the schema level.
- **NFR-12**: The LLM layer shall be structurally prevented (not just
  prompt-instructed) from emitting its own price predictions or signals.

### 5.7 Testability
- **NFR-13**: Each module (`ai/`, `backend/`) shall have automated tests in its
  corresponding `tests/` folder, run in CI on every PR into `develop`.

---

## 6. Traceability Notes

- Requirements in this document map 1:1 to the module numbering in `PDR.md`
  and the "Core AI Modules" section of the original project brief.
- The MVP subset of these requirements (which ones ship first) is defined in
  `docs/MVP.md` — this SRS describes the **full target system**; MVP is a
  deliberate, documented slice of it, not a separate requirement set.

## 7. Appendix — Requirement Status Legend (for tracking, fill in as built)

| Status | Meaning |
|---|---|
| Not started | No code yet |
| In progress | Actively being implemented |
| Implemented | Code complete, untested |
| Tested | Covered by passing automated tests |
| Done | Tested + reviewed + merged to `develop` |

*(Maintain a requirements-status table — e.g. in GitHub Projects — using the
FR/NFR IDs above as the tracking key.)*

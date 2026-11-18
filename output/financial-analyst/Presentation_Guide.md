# Presentation guide

AI-Powered Financial Analyst & Investment Decision Support System

Source review: supplied develop ZIP and selected GitHub develop files, 18 November 2026.

Replace [Institution name] on the title slide before presenting. Scripts describe assigned responsibilities and avoid unverified authorship claims.

## Speaking division

Target duration: approximately 12-15 minutes plus Q&A. Allow about 2.5-3 minutes per person. Each slide has a suggested 45-60 seconds, with extra explanation time for the architecture and diagrams.

| Speaker | URN | Slides | Assigned responsibility |
|---|---|---|---|
| Shadab Firoz | 2305051530127 | 1–3 | AI/ML Development |
| Umar Forooque | 2305051530151 | 4–6 | Backend Development |
| Nooh Khan | 2305051530092 | 7–9 | Frontend Development |
| Salma Ali | 2305051530118 | 10–12 | Database Management and Design |
| Mohammad Arslala | 2305051530077 | 13–15 | UI/UX Design |

## Speaker handoffs

### Shadab Firoz - slides 1–3

Coverage: Project purpose, provider adapters, feature engineering and model roadmap.

Handoff: "Umar will now explain how the backend will expose these capabilities."

### Umar Forooque - slides 4–6

Coverage: Integration boundaries, high-level architecture and actual API surface.

Handoff: "Nooh will now cover the frontend and the planned client-server interaction."

### Nooh Khan - slides 7–9

Coverage: Stack status, React structure and client-server communication.

Handoff: "Salma will now explain persistence, workflow and technical reliability."

### Salma Ali - slides 10–12

Coverage: Conceptual persistence, data workflow and reliability requirements.

Handoff: "Mohammad will close with interface design and the roadmap."

### Mohammad Arslala - slides 13–15

Coverage: Proposed UX, development status and final synthesis.

Handoff: "Thank you. We welcome questions from the evaluators."

## Slide explanations and scripts

### Slide 1: AI-Powered Financial Analyst

Speaker: Shadab Firoz | Suggested time: 45-60 seconds

**Technical explanation:** Introduces the project, all five team members, their URNs and assigned technical areas. The institution name is intentionally a placeholder.

**Suggested script:**

Good morning. We are presenting the AI-Powered Financial Analyst and Investment Decision Support System. Our goal is to bring market data, model outputs and explanations into one educational research platform. Our five responsibilities cover AI and machine learning, backend, frontend, database, and UI/UX. This presentation distinguishes source code that already exists from the target architecture. Data collection and feature engineering contain substantive implementation. Most user-facing analysis and prediction capabilities remain future work.

**Source references:**

- [README.md](https://github.com/shdbfrz/AI-Powered-Financial-Analyst/blob/develop/README.md)

### Slide 2: Problem and project purpose

Speaker: Shadab Firoz | Suggested time: 45-60 seconds

**Technical explanation:** Connects the problem of fragmented price and news data to provider normalization and a shared feature vocabulary. Benefits are objectives rather than measured outcomes.

**Suggested script:**

The project addresses fragmentation in financial analysis. Historical prices, company information and news arrive through separate providers, and different teams can calculate the same indicator differently. The implemented foundation standardizes data collection and produces a shared feature vocabulary for later model development. The wider design adds forecasting, sentiment and explanations through a single dashboard. These are project objectives rather than measured benefits. We do not claim improved investment returns or predictive accuracy because the repository contains no trained forecasting system or validated performance benchmark.

**Source references:**

- [docs/SRS.md](https://github.com/shdbfrz/AI-Powered-Financial-Analyst/blob/develop/docs/SRS.md)
- [ai/feature_engineering/README.md](https://github.com/shdbfrz/AI-Powered-Financial-Analyst/blob/develop/ai/feature_engineering/README.md)

### Slide 3: AI/ML module and processing pipeline

Speaker: Shadab Firoz | Suggested time: 45-60 seconds

**Technical explanation:** Shows the implemented data-to-feature flow. Sixteen generator groups feed versioned CSV and metadata reports. Predictive models and language modules remain planned.

**Suggested script:**

My assigned responsibility is AI and machine learning. The existing pipeline loads OHLCV data, cleans it, profiles quality, runs sixteen feature generator groups, analyzes the feature set and saves versioned outputs. Indicators use pandas and NumPy. Metadata records formulas and intended use. Feature selection is currently report-only and does not automatically remove columns. The committed sample describes 205 generated features from synthetic data, not prediction accuracy. Random Forest, XGBoost, time-series models, deep learning, FinBERT and LLM explanations remain planned. Umar will now explain how the backend will expose these capabilities.

**Source references:**

- [ai/feature_engineering/pipeline.py](https://github.com/shdbfrz/AI-Powered-Financial-Analyst/blob/develop/ai/feature_engineering/pipeline.py)
- [ai/feature_engineering/features/__init__.py](https://github.com/shdbfrz/AI-Powered-Financial-Analyst/blob/develop/ai/feature_engineering/features/__init__.py)
- [docs/architecture/ARCHITECTURE.md](https://github.com/shdbfrz/AI-Powered-Financial-Analyst/blob/develop/docs/architecture/ARCHITECTURE.md)

### Slide 4: Objectives and integration contracts

Speaker: Umar Forooque | Suggested time: 45-60 seconds

**Technical explanation:** Defines the boundary between implemented adapters and the proposed inference, decision and explanation stages. Training belongs in AI modules rather than backend routes.

**Suggested script:**

My responsibility is backend development. The integration objective is to connect the implemented data pipeline to a serving layer without moving training logic into API routes. DataCollectionManager already hides provider-specific calls behind a common interface. The planned backend should orchestrate inference using trained artifacts. Later, the decision engine will combine predictions, sentiment and risk into a structured result. The architecture limits the LLM to explaining that result. It must not create an independent price prediction or trading signal. These are documented integration contracts, and most still require implementation.

**Source references:**

- [ai/data_collection/manager.py](https://github.com/shdbfrz/AI-Powered-Financial-Analyst/blob/develop/ai/data_collection/manager.py)
- [docs/architecture/ARCHITECTURE.md](https://github.com/shdbfrz/AI-Powered-Financial-Analyst/blob/develop/docs/architecture/ARCHITECTURE.md)

### Slide 5: High-level system architecture

Speaker: Umar Forooque | Suggested time: 45-60 seconds

**Technical explanation:** Explains the high-level architecture. Data preparation writes local artifacts. The target intelligence path adds models and FinBERT, then a decision engine and LLM narration. FastAPI serves results to React. PostgreSQL and Redis have configuration but await application integration.

**Suggested script:**

The architecture separates offline data preparation and model development from online serving. The solid data-preparation component already includes provider adapters and feature engineering. It writes local raw data, processed features and reports. Predictive models, FinBERT, the decision engine and the LLM layer remain planned. The backend should load versioned model artifacts and orchestrate inference, while the React client should only consume the API. PostgreSQL is intended for durable application records and Redis for optional caching. Both have infrastructure configuration, but application integration is absent. These boundaries support independent testing and later deployment without mixing model training into request handlers.

**Source references:**

- [docs/architecture/ARCHITECTURE.md](https://github.com/shdbfrz/AI-Powered-Financial-Analyst/blob/develop/docs/architecture/ARCHITECTURE.md)
- [ai/data_collection/manager.py](https://github.com/shdbfrz/AI-Powered-Financial-Analyst/blob/develop/ai/data_collection/manager.py)
- [backend/app/main.py](https://github.com/shdbfrz/AI-Powered-Financial-Analyst/blob/develop/backend/app/main.py)

### Slide 6: Backend module and API boundary

Speaker: Umar Forooque | Suggested time: 45-60 seconds

**Technical explanation:** Identifies the actual FastAPI surface: an app factory, versioned router, health endpoint and Pydantic Settings. Authentication, business schemas, ORM sessions and AI orchestration still need implementation.

**Suggested script:**

The FastAPI app uses an app factory and mounts a versioned router. Its only implemented endpoint is GET slash api slash v1 slash health, which returns status ok. Pydantic Settings centralizes configuration, including database and JWT settings. Configuration fields do not establish working authentication or database integration. The models, schemas, database and services directories are placeholders. Request validation, JWT verification, analysis routes and SQLAlchemy sessions still need implementation. The health route demonstrates liveness, not dependency readiness. Nooh will now cover the frontend and the planned client-server interaction.

**Source references:**

- [backend/app/main.py](https://github.com/shdbfrz/AI-Powered-Financial-Analyst/blob/develop/backend/app/main.py)
- [backend/app/api/v1/router.py](https://github.com/shdbfrz/AI-Powered-Financial-Analyst/blob/develop/backend/app/api/v1/router.py)
- [backend/app/api/v1/endpoints/health.py](https://github.com/shdbfrz/AI-Powered-Financial-Analyst/blob/develop/backend/app/api/v1/endpoints/health.py)
- [backend/app/core/config.py](https://github.com/shdbfrz/AI-Powered-Financial-Analyst/blob/develop/backend/app/core/config.py)

### Slide 7: Technology stack and implementation status

Speaker: Nooh Khan | Suggested time: 45-60 seconds

**Technical explanation:** Separates source implementation, scaffolds, dependency declarations and planned modules. A library in a requirements file is not proof of an integrated feature.

**Suggested script:**

My responsibility is frontend development. This stack slide separates active source code from installed or declared dependencies. React, Vite and Tailwind support the current placeholder application. Router, Axios and both chart libraries appear in package.json, but the current App component does not use them. FastAPI provides the app and health route. The substantial implemented analytical code uses pandas and NumPy. PostgreSQL, Redis and deployment tools have configuration, while the predictive and language-model modules remain planned. The deep learning framework is still an open architecture choice, so we should not claim that both frameworks are integrated.

**Source references:**

- [frontend/package.json](https://github.com/shdbfrz/AI-Powered-Financial-Analyst/blob/develop/frontend/package.json)
- [backend/requirements.txt](https://github.com/shdbfrz/AI-Powered-Financial-Analyst/blob/develop/backend/requirements.txt)
- [ai/requirements.txt](https://github.com/shdbfrz/AI-Powered-Financial-Analyst/blob/develop/ai/requirements.txt)
- [docker-compose.yml](https://github.com/shdbfrz/AI-Powered-Financial-Analyst/blob/develop/docker-compose.yml)
- [docs/architecture/ARCHITECTURE.md](https://github.com/shdbfrz/AI-Powered-Financial-Analyst/blob/develop/docs/architecture/ARCHITECTURE.md)

### Slide 8: Frontend module and component structure

Speaker: Nooh Khan | Suggested time: 45-60 seconds

**Technical explanation:** Explains the React entry point and current placeholder App. Reusable chart, page, API-service and authentication components are future work.

**Suggested script:**

The frontend starts in main.jsx and renders App.jsx. The current App displays the project name and a scaffold message. The source includes empty directories for components, pages, context, hooks, routes and services. A planned dashboard would separate ticker selection, chart rendering and analysis results into reusable components. Axios would handle API requests and React Router would manage page navigation. Chart.js and Recharts are available dependencies, but no financial chart component is implemented. We therefore present the interface structure as a development plan rather than a completed dashboard.

**Source references:**

- [frontend/src/main.jsx](https://github.com/shdbfrz/AI-Powered-Financial-Analyst/blob/develop/frontend/src/main.jsx)
- [frontend/src/App.jsx](https://github.com/shdbfrz/AI-Powered-Financial-Analyst/blob/develop/frontend/src/App.jsx)
- [frontend/package.json](https://github.com/shdbfrz/AI-Powered-Financial-Analyst/blob/develop/frontend/package.json)
- [docs/architecture/ARCHITECTURE.md](https://github.com/shdbfrz/AI-Powered-Financial-Analyst/blob/develop/docs/architecture/ARCHITECTURE.md)

### Slide 9: Frontend–backend communication

Speaker: Nooh Khan | Suggested time: 45-60 seconds

**Technical explanation:** Contrasts the existing health route with the proposed analysis contract. The latter would carry ticker requests and return structured analytical outputs with an educational disclaimer.

**Suggested script:**

The upper path shows the implemented backend route: an HTTP client can request the health endpoint and receive a small JSON response. The React App does not currently call it. The lower path describes the intended analysis interaction: a dashboard sends a ticker to the planned analysis endpoint, FastAPI invokes a service, and the service returns a structured decision with explanations and uncertainty. The client must eventually handle loading, empty results and provider errors. This is a proposed contract, not an existing endpoint. Salma will now explain persistence, workflow and technical reliability.

**Source references:**

- [frontend/src/App.jsx](https://github.com/shdbfrz/AI-Powered-Financial-Analyst/blob/develop/frontend/src/App.jsx)
- [backend/app/api/v1/router.py](https://github.com/shdbfrz/AI-Powered-Financial-Analyst/blob/develop/backend/app/api/v1/router.py)
- [docs/architecture/ARCHITECTURE.md](https://github.com/shdbfrz/AI-Powered-Financial-Analyst/blob/develop/docs/architecture/ARCHITECTURE.md)

### Slide 10: Database module and proposed data model

Speaker: Salma Ali | Suggested time: 45-60 seconds

**Technical explanation:** Shows a proposed subset of documented database entities and their associations. This is a conceptual model, not an implemented ERD or migration. Keys, constraints and cardinalities remain design work.

**Suggested script:**

My assigned responsibility is database management and design. Compose defines PostgreSQL 16 with a persistent volume and Redis 7. However, the database and models folders contain no implemented ORM classes, session factory or migrations. The diagram is a proposed subset of the documented entities. A ticker could relate to price points and predictions. A model run would identify the artifact behind a prediction. News articles could produce sentiment scores, and a decision would reference evidence from predictions and sentiment. Exact keys, cardinalities, constraints and migration strategy still need formal schema design.

**Source references:**

- [docs/architecture/ARCHITECTURE.md](https://github.com/shdbfrz/AI-Powered-Financial-Analyst/blob/develop/docs/architecture/ARCHITECTURE.md)
- [backend/app/db/__init__.py](https://github.com/shdbfrz/AI-Powered-Financial-Analyst/blob/develop/backend/app/db/__init__.py)
- [docker-compose.yml](https://github.com/shdbfrz/AI-Powered-Financial-Analyst/blob/develop/docker-compose.yml)

### Slide 11: End-to-end workflow and storage

Speaker: Salma Ali | Suggested time: 45-60 seconds

**Technical explanation:** Separates the current file pipeline from its planned application extension. Redis infrastructure exists in Compose, while the implemented AI cache uses local files.

**Suggested script:**

The current workflow can collect market data into local files and transform raw OHLCV into processed features and documentation. Reports include data-quality summaries and feature metadata. The future application extends that path with trained model inference, news sentiment, a decision object and an LLM explanation. The backend would persist results and send them to the React dashboard. Redis is intended as an optional cache or queue component, but the existing utility cache is file-based. This distinction matters because a configured Redis container does not prove that the application uses Redis.

**Source references:**

- [ai/data_collection/storage.py](https://github.com/shdbfrz/AI-Powered-Financial-Analyst/blob/develop/ai/data_collection/storage.py)
- [ai/feature_engineering/storage.py](https://github.com/shdbfrz/AI-Powered-Financial-Analyst/blob/develop/ai/feature_engineering/storage.py)
- [docs/architecture/ARCHITECTURE.md](https://github.com/shdbfrz/AI-Powered-Financial-Analyst/blob/develop/docs/architecture/ARCHITECTURE.md)

### Slide 12: Security, reliability and evaluation

Speaker: Salma Ali | Suggested time: 45-60 seconds

**Technical explanation:** Summarizes existing error-handling utilities and test definitions. Highlights remaining authentication, production configuration and evaluation work. Centered swing features need causal treatment before live modeling.

**Suggested script:**

Reliability support includes provider error types, retry utilities, logging and test files. CI configuration exists, but this review does not establish a successful CI run or a deployed system. Security work remains: JWT configuration needs actual enforcement, debug CORS needs explicit production origins, and placeholder secrets must be replaced. Future model evaluation must use chronological splits and prevent target leakage. Swing features use centered windows and require future-bar confirmation, so they need lagging or exclusion for live use. Prediction responses must eventually enforce the educational disclaimer in their schemas. Mohammad will close with interface design and the roadmap.

**Source references:**

- [.github/workflows/ci.yml](https://github.com/shdbfrz/AI-Powered-Financial-Analyst/blob/develop/.github/workflows/ci.yml)
- [ai/tests/test_feature_engineering.py](https://github.com/shdbfrz/AI-Powered-Financial-Analyst/blob/develop/ai/tests/test_feature_engineering.py)
- [ai/feature_engineering/features/price_action.py](https://github.com/shdbfrz/AI-Powered-Financial-Analyst/blob/develop/ai/feature_engineering/features/price_action.py)
- [ai/feature_engineering/features/target.py](https://github.com/shdbfrz/AI-Powered-Financial-Analyst/blob/develop/ai/feature_engineering/features/target.py)
- [backend/app/main.py](https://github.com/shdbfrz/AI-Powered-Financial-Analyst/blob/develop/backend/app/main.py)

### Slide 13: UI/UX module and proposed interface

Speaker: Mohammad Arslala | Suggested time: 45-60 seconds

**Technical explanation:** Presents an explicitly proposed wireframe. It prioritizes ticker selection, freshness, historical evidence, uncertainty, sentiment and readable explanations. Accessibility goals require future testing.

**Suggested script:**

My responsibility is UI and UX design. This wireframe is a conceptual proposal, not a screenshot of the current application. The user journey begins with ticker selection, followed by a view of data freshness and historical prices. Forecasts and sentiment should remain distinct so users can understand their evidence and uncertainty. Explanations should identify supporting drivers and limitations. Planned accessibility work includes keyboard navigation, visible focus, readable contrast, labeled charts and status messages that do not rely only on color. The current interface only renders the scaffold page, so these usability goals still require implementation and testing.

**Source references:**

- [frontend/src/App.jsx](https://github.com/shdbfrz/AI-Powered-Financial-Analyst/blob/develop/frontend/src/App.jsx)
- [docs/architecture/ARCHITECTURE.md](https://github.com/shdbfrz/AI-Powered-Financial-Analyst/blob/develop/docs/architecture/ARCHITECTURE.md)

### Slide 14: Project status and next milestones

Speaker: Mohammad Arslala | Suggested time: 45-60 seconds

**Technical explanation:** Reconciles the stale main README with later data-collection and feature-engineering code. The committed sample uses synthetic data and does not establish model accuracy.

**Suggested script:**

The strongest completed foundation is the data pipeline. The backend, frontend and deployment files establish structure, while the core analysis application remains under development. The committed sample uses 300 synthetic trading days and demonstrates output structure, not real-market forecasting performance. The main README still describes an earlier scaffolding phase, so the module code and Sprint 2 documentation provide a more precise status. Next priorities are schema and API implementation, leakage-safe model baselines, and then sentiment and dashboard integration. Production readiness will require successful tests, provider validation, observability and an end-to-end deployment review.

**Source references:**

- [README.md](https://github.com/shdbfrz/AI-Powered-Financial-Analyst/blob/develop/README.md)
- [ai/feature_engineering/README.md](https://github.com/shdbfrz/AI-Powered-Financial-Analyst/blob/develop/ai/feature_engineering/README.md)
- [docs/sprint2_sample_output/README.md](https://github.com/shdbfrz/AI-Powered-Financial-Analyst/blob/develop/docs/sprint2_sample_output/README.md)
- [docs/architecture/ARCHITECTURE.md](https://github.com/shdbfrz/AI-Powered-Financial-Analyst/blob/develop/docs/architecture/ARCHITECTURE.md)

### Slide 15: Team responsibilities and Q&A

Speaker: Mohammad Arslala | Suggested time: 45-60 seconds

**Technical explanation:** Closes with all five assigned responsibilities and speaking ranges. The team assignments do not verify individual implementation authorship.

**Suggested script:**

To conclude, this project establishes a documented architecture and an implemented data-preparation foundation for financial decision support. Shadab covers AI and machine learning, Umar the backend, Nooh the frontend, Salma database management and design, and I cover UI and UX. These are our assigned responsibilities, not claims about verified individual code authorship. The next goal is to connect these areas through tested data and API contracts. The project is educational and does not provide financial advice. Thank you. We welcome questions on the implemented pipeline, proposed integration, current limitations and development roadmap.

**Source references:**

- [README.md](https://github.com/shdbfrz/AI-Powered-Financial-Analyst/blob/develop/README.md)

## High-level architecture talking points

1. Provider adapters isolate external API differences. Existing implementations include Yahoo Finance and Alpha Vantage market data plus NewsAPI news collection.
2. The feature pipeline transforms OHLCV into documented outputs. Local CSV, JSON and Markdown files are current persistence, rather than PostgreSQL records.
3. Model training remains offline in ai/. The serving layer is intended to load versioned model artifacts and invoke inference.
4. Forecasting and FinBERT sentiment are separate analytical inputs to the planned decision engine.
5. The decision engine produces the structured signal, risk, confidence and drivers. The LLM is restricted to narration of that object.
6. FastAPI is the intended application boundary. React consumes the API rather than invoking providers or training code directly.
7. PostgreSQL is intended for durable application entities. Redis is an optional cache or queue. Compose configuration exists, but application integration is missing.

## Evaluation questions to prepare for

**What is implemented today?** Data collection and feature engineering have substantive code. FastAPI exposes the health route. React renders a scaffold page.

**What model accuracy did you achieve?** No forecasting accuracy or investment-return result is established by the inspected source. The committed Sprint 2 sample uses synthetic OHLCV data.

**Why use an LLM?** The design uses it to explain structured analytical outputs. It does not independently produce the price forecast or decision signal.

**How will you prevent leakage?** Use chronological training and evaluation, exclude target columns from predictors, fit preprocessing on training data only, and lag or exclude centered swing features until their confirmation time.

**Is authentication working?** JWT configuration and dependency declarations exist. Auth routes and token verification remain to be implemented.

**Is the database implemented?** PostgreSQL and Redis have Compose services. ORM models, database sessions and migrations are absent.

**Why does the README say only scaffolding exists?** The main README describes an earlier phase. Sprint 2 module documentation and source show later data-pipeline progress.

**What comes next?** Formalize persistence and API contracts, implement leakage-safe model baselines, integrate sentiment and explanations, build the dashboard and verify the full deployment.

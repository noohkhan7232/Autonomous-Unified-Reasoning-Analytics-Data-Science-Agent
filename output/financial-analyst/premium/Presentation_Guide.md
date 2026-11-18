# Presentation guide

AI-Powered Financial Analyst & Investment Decision Support System

18 slides. Suggested duration: 13-16 minutes plus Q&A. Replace [Institution name] on the cover before presenting.

## Five speaking sections

| Speaker | URN | Slides | Assigned area |
|---|---|---|---|
| Shadab Firoz | 2305051530127 | 1–4 | AI/ML Development |
| Umar Forooque | 2305051530151 | 5–8 | Backend Development |
| Nooh Khan | 2305051530092 | 9–11 | Frontend Development |
| Salma Ali | 2305051530118 | 12–14 | Database Management and Design |
| Mohammad Arslala | 2305051530077 | 15–18 | UI/UX Design |

### Shadab Firoz

Coverage: Introduction, problem, proposed solution and AI/data architecture.

Suggested time: approximately 2.5-3.5 minutes.

Handoff: "Umar will now explain the system boundaries and serving layer."

### Umar Forooque

Coverage: Layered architecture, technology stack, API communication and security.

Suggested time: approximately 2.5-3.5 minutes.

Handoff: "Nooh will now discuss the frontend, sample visualization and full workflow."

### Nooh Khan

Coverage: Frontend architecture, repository sample chart and complete workflow.

Suggested time: approximately 2.5-3.5 minutes.

Handoff: "Salma will now explain persistence, implementation status and the roadmap."

### Salma Ali

Coverage: Conceptual database, implementation status and future delivery scope.

Suggested time: approximately 2.5-3.5 minutes.

Handoff: "Mohammad will now explain the proposed user experience and team handoffs."

### Mohammad Arslala

Coverage: User journey, conceptual dashboard, team contribution diagram and Q&A.

Suggested time: approximately 2.5-3.5 minutes.

Handoff: "Thank you. We welcome questions from the evaluators."

## Slide 1: AI-Powered Financial Analyst

Speaker: Shadab Firoz

**Technical explanation:** Introduces the project scope and the five assigned technical areas. The cover separates implemented foundations from proposed services.

**Suggested script:**

Good morning. Our project is the AI-Powered Financial Analyst and Investment Decision Support System. The goal is to connect market data, analytical models and understandable explanations in one educational research platform. Our five technical responsibilities cover AI and machine learning, backend, frontend, database, and UI/UX. We will distinguish the implemented data-preparation foundation from the target analysis application throughout the presentation. The cover illustration represents the concept of connected analytical layers. It is not a screenshot or a technical system diagram.

**Sources:**

- [README.md](https://github.com/shdbfrz/AI-Powered-Financial-Analyst/blob/develop/README.md)

## Slide 2: The financial analysis problem

Speaker: Shadab Firoz

**Technical explanation:** Identifies fragmented market inputs, inconsistent feature definitions and limited forecast transparency as the project problems.

**Suggested script:**

The problem is fragmented evidence. Historical prices and financial news arrive through different sources. Inconsistent indicator definitions make model comparison difficult, and a prediction alone gives little explanation of its uncertainty. The project responds with normalized inputs, a shared feature vocabulary and a proposed explanation layer. These are engineering objectives. We do not claim investment returns or improved forecasting accuracy because the inspected project does not yet contain a trained forecasting service or a validated performance benchmark.

**Sources:**

- [docs/PDR.md](https://github.com/shdbfrz/AI-Powered-Financial-Analyst/blob/develop/docs/PDR.md)
- [ai/feature_engineering/README.md](https://github.com/shdbfrz/AI-Powered-Financial-Analyst/blob/develop/ai/feature_engineering/README.md)

## Slide 3: Proposed decision-support platform

Speaker: Shadab Firoz

**Technical explanation:** Shows the proposed data-to-dashboard contract. Data and feature preparation have implementation code, while inference, decisions and explanations remain planned.

**Suggested script:**

The proposed platform begins with a real foundation: Yahoo Finance data collection, a NewsAPI adapter, symbol search and feature engineering. It then adds planned model inference, sentiment scoring, structured decisions and explanations. The LLM is restricted to explaining the decision object. It must not independently generate a price forecast or trading signal. This design separates data preparation, inference and presentation so that each can be tested. Alpha Vantage has a registered provider interface, but its data methods currently raise ProviderNotImplementedError.

**Sources:**

- [docs/PDR.md](https://github.com/shdbfrz/AI-Powered-Financial-Analyst/blob/develop/docs/PDR.md)
- [docs/architecture/ARCHITECTURE.md](https://github.com/shdbfrz/AI-Powered-Financial-Analyst/blob/develop/docs/architecture/ARCHITECTURE.md)

## Slide 4: AI/ML and data processing architecture

Speaker: Shadab Firoz

**Technical explanation:** Shows raw OHLCV cleaning, sixteen generator groups, report-only selection analysis and versioned outputs, followed by three planned predictive model families.

**Suggested script:**

My assigned area is AI and machine learning. The implemented path loads raw OHLCV, cleans and profiles it, runs sixteen feature generator groups and writes processed data, metadata and reports. Selection analysis is report-only. The planned model layer compares machine learning, time-series and deep-learning families against a shared dataset. FinBERT sentiment is another planned input. No model training or inference implementation is present in these folders. Before modeling, future target columns must be excluded from predictors and centered swing features must be lagged or excluded until confirmation. Umar will now explain the system boundaries.

**Sources:**

- [ai/feature_engineering/pipeline.py](https://github.com/shdbfrz/AI-Powered-Financial-Analyst/blob/develop/ai/feature_engineering/pipeline.py)
- [ai/feature_engineering/features/__init__.py](https://github.com/shdbfrz/AI-Powered-Financial-Analyst/blob/develop/ai/feature_engineering/features/__init__.py)
- [ai/data_collection/alpha_vantage_provider.py](https://github.com/shdbfrz/AI-Powered-Financial-Analyst/blob/develop/ai/data_collection/alpha_vantage_provider.py)

## Slide 5: High-level system architecture

Speaker: Umar Forooque

**Technical explanation:** Separates the experience, application, intelligence and data layers. Arrows show intended response flow, while labels distinguish code present, scaffolds and proposed services.

**Suggested script:**

My responsibility is backend development. The high-level architecture has four layers. The experience layer is the React scaffold. The application layer is FastAPI, where only the app and health endpoint currently exist. The intelligence layer contains planned inference, sentiment, decisions and LLM explanation. The data layer has implemented collection and feature engineering with local files. PostgreSQL and Redis have Compose services, but the application does not yet use an ORM persistence layer. The arrows show the intended response flow upward through these layers. Model training stays outside request handlers.

**Sources:**

- [docs/architecture/ARCHITECTURE.md](https://github.com/shdbfrz/AI-Powered-Financial-Analyst/blob/develop/docs/architecture/ARCHITECTURE.md)
- [backend/app/main.py](https://github.com/shdbfrz/AI-Powered-Financial-Analyst/blob/develop/backend/app/main.py)
- [frontend/src/App.jsx](https://github.com/shdbfrz/AI-Powered-Financial-Analyst/blob/develop/frontend/src/App.jsx)

## Slide 6: Technology stack

Speaker: Umar Forooque

**Technical explanation:** Maps technologies to their evidence status. Dependencies and configuration are distinguished from implemented application integration.

**Suggested script:**

This stack distinguishes implemented code from dependency declarations and future choices. React, Vite and Tailwind support the scaffold. Router, Axios and chart libraries are declared but not wired into a dashboard. FastAPI and Pydantic Settings support the backend app. The implemented data modules use pandas, NumPy, yfinance and requests. SQLAlchemy, PostgreSQL and Redis still require application integration. Predictive and language modules remain planned. TensorFlow or PyTorch is an open design choice, and the full AI dependency pins require reconciliation before later modeling work.

**Sources:**

- [frontend/package.json](https://github.com/shdbfrz/AI-Powered-Financial-Analyst/blob/develop/frontend/package.json)
- [backend/requirements.txt](https://github.com/shdbfrz/AI-Powered-Financial-Analyst/blob/develop/backend/requirements.txt)
- [ai/requirements-core.txt](https://github.com/shdbfrz/AI-Powered-Financial-Analyst/blob/develop/ai/requirements-core.txt)
- [ai/requirements.txt](https://github.com/shdbfrz/AI-Powered-Financial-Analyst/blob/develop/ai/requirements.txt)

## Slide 7: Backend and API communication

Speaker: Umar Forooque

**Technical explanation:** Contrasts the implemented health route with the proposed analysis request. JWT verification, business schemas, persistence and AI orchestration remain future work.

**Suggested script:**

The only implemented API endpoint is GET slash api slash v1 slash health. It returns status ok and demonstrates liveness. Pydantic Settings centralizes environment configuration, including database and JWT fields. Those settings do not implement authentication. The lower flow shows the planned analysis endpoint: the React client submits a ticker, FastAPI calls an analytical service, and the service returns a structured result. The request schemas, JWT verification, persistence and AI orchestration still need development. Loading, empty results and provider failures also need client-facing handling.

**Sources:**

- [backend/app/main.py](https://github.com/shdbfrz/AI-Powered-Financial-Analyst/blob/develop/backend/app/main.py)
- [backend/app/api/v1/router.py](https://github.com/shdbfrz/AI-Powered-Financial-Analyst/blob/develop/backend/app/api/v1/router.py)
- [backend/app/api/v1/endpoints/health.py](https://github.com/shdbfrz/AI-Powered-Financial-Analyst/blob/develop/backend/app/api/v1/endpoints/health.py)
- [backend/app/core/config.py](https://github.com/shdbfrz/AI-Powered-Financial-Analyst/blob/develop/backend/app/core/config.py)

## Slide 8: Security and technical considerations

Speaker: Umar Forooque

**Technical explanation:** Separates existing provider reliability utilities from release requirements. Chronological evaluation and causal treatment of centered features are essential for future modeling.

**Suggested script:**

The source contains useful reliability primitives: typed provider errors, retries, file caching, logging and test definitions. A CI workflow exists, but this presentation does not claim a successful CI run or deployment. Release work includes JWT enforcement, explicit production CORS origins, real secrets, dependency readiness and monitoring. Model evaluation must use chronological splits and prevent target leakage. Centered swing features depend on future confirmation. The repository also documents a future AI dependency-pin conflict. Educational disclaimers must eventually be enforced by prediction response schemas. Nooh will now discuss the frontend.

**Sources:**

- [backend/app/main.py](https://github.com/shdbfrz/AI-Powered-Financial-Analyst/blob/develop/backend/app/main.py)
- [.github/workflows/ci.yml](https://github.com/shdbfrz/AI-Powered-Financial-Analyst/blob/develop/.github/workflows/ci.yml)
- [ai/feature_engineering/features/price_action.py](https://github.com/shdbfrz/AI-Powered-Financial-Analyst/blob/develop/ai/feature_engineering/features/price_action.py)
- [ai/feature_engineering/features/target.py](https://github.com/shdbfrz/AI-Powered-Financial-Analyst/blob/develop/ai/feature_engineering/features/target.py)
- [ai/requirements-core.txt](https://github.com/shdbfrz/AI-Powered-Financial-Analyst/blob/develop/ai/requirements-core.txt)

## Slide 9: Frontend architecture

Speaker: Nooh Khan

**Technical explanation:** Shows main.jsx mounting the placeholder App.jsx. The proposed dashboard, API-service and chart boundaries are editable conceptual components.

**Suggested script:**

My responsibility is frontend development. main.jsx mounts App.jsx, which currently renders a project title and a scaffold message. The component, page, route, hook and service folders are placeholders. The proposed structure separates the dashboard page, an Axios API service, chart components and the explanation view. React Router would manage navigation. Chart.js and Recharts are declared dependencies rather than implemented visualizations. The diagram therefore shows a proposed component boundary. The next slide uses a committed repository sample to demonstrate how feature data could be visualized without pretending that the dashboard already exists.

**Sources:**

- [frontend/src/App.jsx](https://github.com/shdbfrz/AI-Powered-Financial-Analyst/blob/develop/frontend/src/App.jsx)
- [frontend/src/main.jsx](https://github.com/shdbfrz/AI-Powered-Financial-Analyst/blob/develop/frontend/src/main.jsx)
- [frontend/package.json](https://github.com/shdbfrz/AI-Powered-Financial-Analyst/blob/develop/frontend/package.json)

## Slide 10: Feature output as visual evidence

Speaker: Nooh Khan

**Technical explanation:** Plots close and SMA5 directly from the committed synthetic SAMPLE preview. Rows five through twenty-five demonstrate feature output, not forecasting performance.

**Suggested script:**

This chart uses the committed SAMPLE dataset, which the repository says comes from synthetic OHLCV. It is not a real stock or a prediction. We show close and the five-period simple moving average for sample rows five through twenty-five, where both values exist. The initial four rows have no SMA5 because the rolling window has not filled. The chart demonstrates output shape and visualization readiness. It establishes neither forecast accuracy nor investment value. Both series and their underlying values remain editable in PowerPoint.

**Sources:**

- [docs/sprint2_sample_output/README.md](https://github.com/shdbfrz/AI-Powered-Financial-Analyst/blob/develop/docs/sprint2_sample_output/README.md)
- [docs/sprint2_sample_output/features_preview_first25rows.csv](https://github.com/shdbfrz/AI-Powered-Financial-Analyst/blob/develop/docs/sprint2_sample_output/features_preview_first25rows.csv)

## Slide 11: Complete system workflow

Speaker: Nooh Khan

**Technical explanation:** Separates current OHLCV processing from the planned analysis application. NewsAPI supplies a separate input to future sentiment analysis.

**Suggested script:**

The current workflow collects data into local raw files, transforms OHLCV into processed features and writes quality and feature reports. The target extension adds trained model inference, news sentiment, a structured decision and an LLM explanation, then exposes results through FastAPI to React. The backend should persist results once the database layer exists. Redis is a configured optional service, while the existing AI utility cache uses local JSON files. These are different implementation states. Salma will now explain persistence and the remaining development sequence.

**Sources:**

- [ai/data_collection/manager.py](https://github.com/shdbfrz/AI-Powered-Financial-Analyst/blob/develop/ai/data_collection/manager.py)
- [ai/feature_engineering/pipeline.py](https://github.com/shdbfrz/AI-Powered-Financial-Analyst/blob/develop/ai/feature_engineering/pipeline.py)
- [docs/architecture/ARCHITECTURE.md](https://github.com/shdbfrz/AI-Powered-Financial-Analyst/blob/develop/docs/architecture/ARCHITECTURE.md)

## Slide 12: Database architecture

Speaker: Salma Ali

**Technical explanation:** Shows proposed relationships among documented entities. PostgreSQL and Redis have configuration, but keys, cardinalities, ORM sessions and migrations remain unimplemented.

**Suggested script:**

My assigned responsibility is database management and design. PostgreSQL 16 and Redis 7 appear in Compose, with a persistent PostgreSQL volume. However, ORM models, a session factory and migration files are absent. The diagram is a conceptual subset of the architecture document. A ticker relates to price points and predictions, and a model run identifies the artifact behind a prediction. News articles could produce sentiment scores used by decisions. Exact keys, constraints, cardinalities and migration rules still need design. Current analytical outputs use local files.

**Sources:**

- [docker-compose.yml](https://github.com/shdbfrz/AI-Powered-Financial-Analyst/blob/develop/docker-compose.yml)
- [docs/architecture/ARCHITECTURE.md](https://github.com/shdbfrz/AI-Powered-Financial-Analyst/blob/develop/docs/architecture/ARCHITECTURE.md)
- [backend/app/db/__init__.py](https://github.com/shdbfrz/AI-Powered-Financial-Analyst/blob/develop/backend/app/db/__init__.py)

## Slide 13: Implementation status

Speaker: Salma Ali

**Technical explanation:** Reconciles implemented collection and feature-engineering code with application scaffolds and planned AI modules. Alpha Vantage remains interface-only.

**Suggested script:**

The most substantial implemented areas are data collection and feature engineering. The backend has an app factory and health route, and React has a scaffold page. Predictive models, FinBERT, decision support, LLM explanations and application persistence remain planned. Alpha Vantage is interface-only, which is more precise than simply saying multiple providers work. The main README describes an earlier scaffolding phase, while Sprint 2 documentation and code show later progress. The committed synthetic sample illustrates pipeline output. We do not infer successful live operation or model quality from its presence.

**Sources:**

- [README.md](https://github.com/shdbfrz/AI-Powered-Financial-Analyst/blob/develop/README.md)
- [ai/feature_engineering/README.md](https://github.com/shdbfrz/AI-Powered-Financial-Analyst/blob/develop/ai/feature_engineering/README.md)
- [ai/data_collection/alpha_vantage_provider.py](https://github.com/shdbfrz/AI-Powered-Financial-Analyst/blob/develop/ai/data_collection/alpha_vantage_provider.py)
- [frontend/src/App.jsx](https://github.com/shdbfrz/AI-Powered-Financial-Analyst/blob/develop/frontend/src/App.jsx)

## Slide 14: Future scope and delivery roadmap

Speaker: Salma Ali

**Technical explanation:** Shows a proposed dependency order for delivery and distinguishes the documented single-ticker MVP from later time-series and provider extensions.

**Suggested script:**

The documented MVP starts with one ticker, Random Forest and LSTM, FinBERT sentiment, a basic decision engine and one explanation provider. Time-series forecasting is a later extension in the MVP document. A practical sequence is schema and API contracts, leakage-safe model baselines, sentiment and decision integration, then a dashboard and deployment review. Provider expansion and richer portfolio or report features can follow. Every phase needs evidence of correctness before the next. Mohammad will now explain the proposed user experience and team handoffs.

**Sources:**

- [docs/MVP.md](https://github.com/shdbfrz/AI-Powered-Financial-Analyst/blob/develop/docs/MVP.md)
- [docs/architecture/ARCHITECTURE.md](https://github.com/shdbfrz/AI-Powered-Financial-Analyst/blob/develop/docs/architecture/ARCHITECTURE.md)

## Slide 15: UI/UX design and user journey

Speaker: Mohammad Arslala

**Technical explanation:** Maps ticker selection, evidence inspection, output comparison and explanation into a proposed user journey. Accessibility principles remain design goals.

**Suggested script:**

My responsibility is UI and UX design. The proposed user journey has four steps: select a ticker, inspect the underlying data, compare analytical outputs and read an explanation with uncertainty. Visual hierarchy should keep historical evidence distinct from forecast outputs and sentiment. Accessibility goals include keyboard navigation, visible focus, clear status messages, chart labels and adequate contrast. These are design goals that still require implementation and usability testing. The current repository interface is a scaffold, so the next slide is explicitly a conceptual dashboard.

**Sources:**

- [frontend/src/App.jsx](https://github.com/shdbfrz/AI-Powered-Financial-Analyst/blob/develop/frontend/src/App.jsx)
- [docs/architecture/ARCHITECTURE.md](https://github.com/shdbfrz/AI-Powered-Financial-Analyst/blob/develop/docs/architecture/ARCHITECTURE.md)

## Slide 16: Conceptual dashboard

Speaker: Mohammad Arslala

**Technical explanation:** Presents an editable conceptual dashboard with explicit unavailable-output states. It is not a screenshot of the repository application.

**Suggested script:**

This is an editable conceptual mockup, not a screenshot of a working dashboard. The left navigation groups market overview, analysis and reports as proposed destinations. The main area reserves space for ticker selection, historical evidence and analysis results. Planned outputs show placeholder states rather than invented prices, confidence scores or recommendations. The explanation area should identify the evidence and limitations behind a decision. Loading, provider errors and unavailable results must remain understandable. Actual chart integration and responsive behavior are future frontend work.

**Sources:**

- [frontend/src/App.jsx](https://github.com/shdbfrz/AI-Powered-Financial-Analyst/blob/develop/frontend/src/App.jsx)
- [docs/architecture/ARCHITECTURE.md](https://github.com/shdbfrz/AI-Powered-Financial-Analyst/blob/develop/docs/architecture/ARCHITECTURE.md)

## Slide 17: Team contribution architecture

Speaker: Mohammad Arslala

**Technical explanation:** Maps the five assigned technical responsibilities to one platform and gives the consecutive speaking sections. This is an assignment map rather than verified commit authorship.

**Suggested script:**

The team diagram shows assigned responsibility boundaries. Shadab owns the AI and machine-learning explanation, Umar the backend, Nooh the frontend, Salma database management and design, and I cover UI and UX. It also gives our speaking sections. These assignments come from the project brief and are not a claim about verified individual commit authorship. The shared system depends on explicit contracts between these areas: documented feature outputs, validated API payloads, persistent records and consistent interface states.

**Sources:**

- [README.md](https://github.com/shdbfrz/AI-Powered-Financial-Analyst/blob/develop/README.md)

## Slide 18: Conclusion and Q&A

Speaker: Mohammad Arslala

**Technical explanation:** Closes with the implemented data foundation, the planned integration work and the educational-use boundary.

**Suggested script:**

To conclude, the project has an implemented data-preparation foundation and a documented architecture for a wider financial decision-support application. The next goal is tested integration across persistence, inference and the user interface. We have separated implemented features, scaffolds and planned capabilities throughout the presentation. The system is for educational and research use, and it does not provide financial advice. Thank you. We welcome questions about the pipeline, architecture, leakage risks, interface design and development roadmap.

**Sources:**

- [docs/architecture/ARCHITECTURE.md](https://github.com/shdbfrz/AI-Powered-Financial-Analyst/blob/develop/docs/architecture/ARCHITECTURE.md)

## Source and visual provenance

Primary evidence: supplied AI-Powered-Financial-Analyst-develop.zip and selected connected GitHub develop files. Source review: 18 November 2026.

Implementation means source present. Live providers, CI and deployment were not executed as part of this presentation review.

The chart uses synthetic SAMPLE close and SMA5 values from the committed preview, rows 5-25. Its embedded workbook is a new literal snapshot of those source values.

The dashboard is a conceptual editable mockup. The repository contains only the frontend scaffold.

Cover asset: built-in ImageGen. Saved project path: D:\AI-Ml-PJT\Autonomous Unified Reasoning & Analytics Data Science Agent\.presentation-build\premium-assets\analytics-hero.png

Final image prompt:

Create a premium technology conference presentation illustration, widescreen 16:9. Deep midnight navy background (#07152B). Entire LEFT 48% is very quiet almost solid navy negative space for editable title to be added later, no text. On RIGHT half: exquisite architectural visualization of financial data intelligence, a small set of translucent glass data layers and precise interconnected luminous nodes flowing through a central faceted analytical core. Royal blue, cyan, restrained teal and violet accents, sophisticated studio 3D lighting, crisp purposeful composition, premium enterprise AI research aesthetic. Thin elegant cyan connections between layers, depth, subtle light refraction. No words, no letters, no numbers, no logos, no currency symbols, no fake UI, no actual financial charts, no robots, no human figures, no stock-photo look. Keep far bottom quiet for small author line. The illustration is conceptual art, not a technical architecture diagram. Avoid busy neon cyberpunk effects.

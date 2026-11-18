# `ai/feature_engineering/` — Sprint 2: Feature Engineering Pipeline

Status: **Complete**
Depends on: `ai/data_collection/` (Sprint 1), `ai/utils/`
Feeds: Sprint 3 (Machine Learning), Sprint 4 (Time Series), Sprint 5 (Deep Learning), Sprint 7 (Decision Support Engine)

---

## 1. Sprint Goal

Turn a raw OHLCV CSV (Sprint 1's output, `datasets/raw/`) into a clean,
richly feature-engineered, model-ready dataset (`datasets/processed/`),
covering price, trend, momentum, volatility, volume, and advanced
technical-analysis (price action / structure / zones / Fibonacci) features,
plus supervised-learning target labels — with every feature documented
(formula, meaning, interpretation, priority, recommended model family).

## 2. Business Problem

Raw OHLCV bars carry almost no directly usable signal for a model — a
`close` price on its own says nothing about trend, momentum, or risk. Every
downstream module (Sprint 3-7) needs a *shared, versioned, well-documented*
feature vocabulary instead of each reinventing indicator math independently,
which would risk subtly different RSI/MACD/ATR implementations feeding
different models and producing inconsistent explanations from the LLM layer
later (violates ARCHITECTURE.md §2's reproducibility principle).

## 3. Why This Sprint Comes Before The Next

Sprint 3 (ML), Sprint 4 (Time Series), and Sprint 5 (Deep Learning) all
consume the *same* processed feature table — building three sets of model
training code against three different ad-hoc feature sets would triple the
maintenance burden and make model comparison meaningless (SRS FR-5.6 requires
comparing LSTM vs GRU "on the same data split"). Feature engineering must be
finished and stable first.

## 4. Architecture

### 4.1 High-Level

```
datasets/raw/*.csv (Sprint 1)
        |
        v
  data_loader.py  ---->  eda.py (Phase 1: profile raw data)
        |                        |
        v                        v
 preprocessing.py         storage/reports/eda/*.{json,md}
 (Phase 2: clean)
        |
        v
  pipeline.py (Phase 3+4: generator chain, in dependency order)
        |
        v
  features/*.py (16 generators; see §4.3)
        |
        v
  selection.py (report-only: correlation / low-variance / duplicates)
        |
        v
  storage.py -----> datasets/processed/{ticker}_{version}_features.csv
                     datasets/processed/{ticker}_{version}_Feature_Metadata.json
                     datasets/processed/{ticker}_{version}_Feature_Summary.csv
                     datasets/processed/{ticker}_{version}_Feature_Report.md
```

### 4.2 Low-Level: Generator Dependency Chain

Feature groups are NOT independent — several read columns an earlier group
produced. `features/__init__.py::build_generators` always runs them in this
order regardless of what order they're listed in config:

```
price -> trend -> momentum -> volatility -> bollinger -> macd -> volume
  -> rolling -> lag -> date -> price_action -> support_resistance
  -> fibonacci -> market_structure -> breakout -> target
```

Key cross-group dependencies:
- `lag` reads `price.pct_return`
- `volume` reads `price.typical_price`
- `support_resistance` reads `price_action.swing_high` / `swing_low`
- `fibonacci` reads `support_resistance.dynamic_support` / `dynamic_resistance`
- `market_structure` reads `price_action.change_of_character`
- `breakout` reads `support_resistance.static_support/resistance` + `nearest_demand_zone`/`nearest_supply_zone`, and `volume.volume_ratio`

### 4.3 Class Design

- **`BaseFeatureGenerator`** (Template Method) — `features/base.py`. Every
  feature group subclasses this. `generate()` validates required input
  columns, calls the subclass's `_compute()`, logs what was added, and wraps
  any exception in `FeatureComputationError`. Subclasses only implement
  `_compute()` (the math) and `describe()` (metadata).
- **`FeatureDefinition`** — immutable dataclass documenting one column:
  formula, meaning, interpretation, priority, recommended model family,
  advantages, limitations, when-to-use. This is what populates
  `Feature_Metadata.json` and `Feature_Report.md` — documentation is
  generated from the same source of truth as the code, so it can't drift.
- **`FeatureEngineeringConfig`** — frozen dataclass of every tunable
  parameter (SMA windows, RSI period, ATR period, ...). Passed through the
  whole pipeline so a run's exact parameters are reproducible and loggable.
- **`FeatureEngineeringPipeline`** (Facade + Pipeline) — `pipeline.py`. The
  single entry point: `FeatureEngineeringPipeline().run(ticker="AAPL")`.
- **`CleaningReport`**, **`EDAReport`**, **`FeatureSelectionReport`** —
  dataclasses carrying structured results between phases and into the
  generated reports.

### 4.4 Design Patterns Used

| Pattern | Where | Why |
|---|---|---|
| Template Method | `BaseFeatureGenerator.generate()` | Shared validation/logging/error-handling; subclasses only write math. |
| Factory | `features/__init__.py::build_generators` | Maps config-driven group names to generator instances in dependency-safe order. |
| Facade | `FeatureEngineeringPipeline` | One call (`run()`) hides loading, EDA, cleaning, 16 generators, selection, and storage. |
| Pipeline | `pipeline.py::run()` | Linear phase sequence (load -> EDA -> clean -> generate -> select -> save), each phase's output feeding the next. |
| Strategy (implicit) | Each `BaseFeatureGenerator` subclass | Interchangeable, independently-testable computation units selected by config. |

## 5. Workflow Diagram

```
Sprint 2
  |
  v
Data Preprocessing (Phase 2)
  |
  v
Feature Engineering (Phase 3: price/trend/momentum/volatility/bollinger/macd/volume/rolling/lag/date/target)
  |
  v
Technical Analysis Engine (Phase 4: price action / S&R / supply-demand / fibonacci / market structure / breakout)
  |
  v
Processed Dataset
```

## 6. Folder Structure

```
ai/feature_engineering/
├── __init__.py              # public API: FeatureEngineeringPipeline, config, exceptions
├── config.py                 # FeatureEngineeringConfig (all tunables)
├── exceptions.py              # typed exception hierarchy
├── data_loader.py             # reads datasets/raw/*.csv
├── preprocessing.py           # Phase 2: cleaning
├── eda.py                     # Phase 1: lightweight EDA -> storage/reports/eda/
├── selection.py                # correlation / low-variance / duplicate analysis
├── pipeline.py                 # orchestrator (Facade + Pipeline pattern)
├── storage.py                   # writes datasets/processed/* outputs
├── README.md                    # this file (architecture, workflow, design)
└── features/
    ├── __init__.py            # generator registry / factory
    ├── base.py                 # BaseFeatureGenerator, FeatureDefinition
    ├── price.py                 # Phase 3.A
    ├── trend.py                  # Phase 3.B
    ├── momentum.py                # Phase 3.C
    ├── volatility.py               # Phase 3.D
    ├── bollinger.py                 # Phase 3.E
    ├── macd.py                       # Phase 3.F
    ├── volume.py                      # Phase 3.G
    ├── rolling.py                      # Phase 3.H
    ├── lag.py                           # Phase 3.I
    ├── date.py                           # Phase 3.J
    ├── target.py                          # target labels
    ├── price_action.py                     # Phase 4.A
    ├── support_resistance.py                # Phase 4.B + 4.C
    ├── fibonacci.py                           # Phase 4.D
    ├── market_structure.py                     # Phase 4.E + 4.G
    └── breakout.py                               # Phase 4.F

ai/tests/test_feature_engineering.py   # unit + integration tests (offline)
scripts/run_feature_engineering_demo.py # manual end-to-end verification (not in CI)
```

## 7. External Dependencies

Only `pandas` and `numpy` (both already transitive dependencies of Sprint 1
via `pandas`). No TA-Lib or other technical-analysis library is used — every
indicator is implemented directly in pandas/numpy so the formula is visible
and auditable in this codebase, matching the "explain every indicator"
requirement. See `ai/requirements-core.txt`.

## 8. Configuration

Two separate configuration surfaces, deliberately kept apart (see
`config.py` docstring):
- `ai/utils/config.py::settings` — env-var-backed paths (`processed_data_dir`,
  `eda_reports_dir`, etc.), consistent with Sprint 1.
- `ai/feature_engineering/config.py::FeatureEngineeringConfig` — non-secret,
  purely computational tunables (window sizes, thresholds), passed explicitly
  through the pipeline for reproducibility rather than read from the
  environment.

## 9. Common Mistakes (avoided here, worth remembering)

- **Assuming the raw CSV schema matches the sprint brief exactly.** The
  brief's example schema includes `Ticker`/`Adj Close` columns Sprint 1's
  actual output does NOT have (`ai/data_collection/yahoo_finance_provider.py`
  writes `date, open, high, low, close, volume`, ticker only in the
  filename). `data_loader.py` reads the real schema and derives `ticker`
  from the filename instead of assuming it's a column.
- **Computing "market structure" from bar-to-bar highs/lows.** A naive
  Higher-High/Higher-Low count using consecutive *bars* is dominated by
  noise. `market_structure.py` instead compares consecutive *confirmed swing
  points*, matching how Dow Theory structure is actually read.
- **Silently dropping NaN rows.** Rolling-window warm-up NaNs (e.g. the
  first 199 rows before `sma_200` exists) are real and expected — dropping
  them by default would silently discard valid short-window training data.
  `drop_warmup_nan_rows` defaults to `False`; NaN counts are reported
  instead (`Feature_Summary.csv`'s `missing_count` column).
- **pandas 3.0 strict dtype casting.** Assigning `pd.NA` into a plain numpy
  `bool` column raises `LossySetitemError` under pandas 3.0 (it did not
  under 2.x). Every boolean feature that can be legitimately unknown (e.g.
  `swing_high` during warm-up) is explicitly cast to the nullable
  `"boolean"` dtype before any `pd.NA` assignment.
- **`idxmin`/`idxmax` on all-NaN rows raising instead of returning NaN**
  (also new/stricter in pandas 3.0) — guarded in `fibonacci.py` by filling
  with `np.inf` first, then masking the result back to NaN.

## 10. Improvements (tracked for later, not blocking Sprint 2)

- Supply/Demand zone detection (`support_resistance.py`) is a documented
  heuristic, not a standardized indicator — worth revisiting with labeled
  backtest data once Sprint 3+ can evaluate whether it actually helps.
- `market_structure.py`'s rolling regression slope (`_rolling_slope`) is
  O(n * window) via `.rolling().apply()`; fine at daily-bar scale (hundreds
  to low thousands of rows) but would need vectorizing for intraday data.
- Multi-ticker batch runs currently mean calling `pipeline.run()` once per
  ticker; a thin batch wrapper could be added if Sprint 3 needs to process
  an entire universe at once.

## 11. How This Sprint Connects To The Next

Sprint 3 (Machine Learning) trains Linear Regression / Random Forest /
XGBoost directly against `datasets/processed/{ticker}_{version}_features.csv`,
using `target_direction_*_day` / `future_return_*_day` as labels and the
`Feature_Report.md` priority/recommended-model-family annotations to decide
an initial feature subset per model family before doing its own feature
selection (FR-3.1, FR-3.2).
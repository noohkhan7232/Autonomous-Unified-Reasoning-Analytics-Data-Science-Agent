# Sprint 2 — Feature Engineering — Architecture

> Full design rationale, class design, patterns, and configuration details
> live in [`ai/feature_engineering/README.md`](../../ai/feature_engineering/README.md).
> This file is the standalone Architecture.md the sprint brief asked for;
> it stays in sync with that README's §4 (Architecture).

## High-Level Architecture

```
datasets/raw/*.csv (Sprint 1 output)
        |
        v
  data_loader.py  ---->  eda.py (Phase 1: profile raw data)
        |                        |
        v                        v
 preprocessing.py         storage/reports/eda/*.{json,md}
 (Phase 2: clean)
        |
        v
  pipeline.py (Phase 3+4: generator chain, dependency order)
        |
        v
  features/*.py (16 generators)
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

## Low-Level Architecture — Generator Dependency Chain

Feature groups are not independent. `features/__init__.py::build_generators`
always runs them in this order, regardless of what order they're listed in
`FeatureEngineeringConfig.enabled_feature_groups`:

```
price -> trend -> momentum -> volatility -> bollinger -> macd -> volume
  -> rolling -> lag -> date -> price_action -> support_resistance
  -> fibonacci -> market_structure -> breakout -> target
```

| Consumer group | Depends on | Column(s) consumed |
|---|---|---|
| `lag` | `price` | `pct_return` |
| `volume` | `price` | `typical_price` |
| `support_resistance` | `price_action` | `swing_high`, `swing_low` |
| `fibonacci` | `support_resistance` | `dynamic_support`, `dynamic_resistance` |
| `market_structure` | `price_action` | `change_of_character` |
| `breakout` | `support_resistance`, `volume` | `static_support`/`static_resistance`/zone columns, `volume_ratio` |

## Design Patterns Used

| Pattern | Where | Why |
|---|---|---|
| Template Method | `BaseFeatureGenerator.generate()` | Shared validation/logging/error-handling; subclasses only implement the math. |
| Factory | `features/__init__.py::build_generators` | Maps config-driven group names to generator instances, in dependency-safe order. |
| Facade | `FeatureEngineeringPipeline` | One call (`run()`) hides loading, EDA, cleaning, 16 generators, selection, and storage. |
| Pipeline | `pipeline.py::run()` | Linear phase sequence, each phase's output feeding the next. |
| Strategy (implicit) | Each `BaseFeatureGenerator` subclass | Interchangeable, independently testable/swappable computation units. |

## Technology

Pure `pandas` + `numpy` — no TA-Lib or other black-box technical-analysis
library, so every formula is visible and auditable in this codebase (see
`Feature_Report.md` for the formula behind every one of the 205 generated
columns).
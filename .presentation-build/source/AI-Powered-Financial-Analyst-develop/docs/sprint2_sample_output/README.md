# Sprint 2 — Sample Output (for review without running the pipeline)

`datasets/processed/` and `storage/reports/eda/` are gitignored (see their
`README.md`s) — real pipeline output isn't committed, by design, same as
Sprint 1's `datasets/raw/`. That's normal for a data pipeline, but it means
a reviewer (professor, teammate) can't see what the pipeline actually
produces without running it themselves.

This folder is the fix: a **committed, static snapshot** of one real
pipeline run, so the generated documentation and output shape are visible
directly on GitHub.

## What's here

| File | What it is |
|---|---|
| `Feature_Report.md` | Full indicator documentation — formula, meaning, interpretation, priority, recommended model family for all 205 generated features. This is the sprint's core "explain every indicator" deliverable. |
| `Feature_Metadata.json` | Same content as `Feature_Report.md`, machine-readable (this is what Sprint 3+ code would parse to pick features by priority/model family). |
| `Feature_Summary.csv` | `describe()`-style statistics (mean/std/min/max/missing count) for every numeric feature. |
| `EDA_Report.md` / `EDA_Report.json` | Phase 1 lightweight EDA output: shape, dtypes, missing values, data-quality/cleaning summary. |
| `features_preview_first25rows.csv` | First 25 rows of the full processed dataset (213 columns), so the actual output shape is visible without downloading an 800KB+ file. |

## How this was generated

Synthetic OHLCV data (300 trading days, ticker `SAMPLE`) was run through the
full pipeline:

```python
from ai.feature_engineering import FeatureEngineeringPipeline
pipeline = FeatureEngineeringPipeline()
result = pipeline.run(raw_df=synthetic_df, version="sample")
```

Synthetic data was used (not a real ticker) specifically so this sample is
reproducible by anyone, with no dependency on Sprint 1's live data
providers or `.env` API keys.

## To regenerate with real data

Once Sprint 1 has pulled a real ticker into `datasets/raw/`:

```powershell
python scripts\run_feature_engineering_demo.py AAPL
```

Real output lands in `datasets/processed/` and `storage/reports/eda/`
(gitignored, local-only) — this `docs/` folder is not automatically
updated and should be refreshed manually if it needs to reflect a newer
version of the pipeline.
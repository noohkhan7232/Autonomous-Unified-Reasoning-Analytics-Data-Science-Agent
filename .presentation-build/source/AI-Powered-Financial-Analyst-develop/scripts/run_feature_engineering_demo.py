"""
scripts/run_feature_engineering_demo.py
========================================
One-off script to run the full Sprint 2 Feature Engineering pipeline
end-to-end and print a summary, for manual verification (not part of CI).

Usage:
    # from the project root, with a venv that has ai/requirements-core.txt installed
    python scripts/run_feature_engineering_demo.py AAPL

If no raw OHLCV file exists yet for the given ticker under `datasets/raw/`
(i.e. Sprint 1's data collection hasn't been run for it), this script
generates a small synthetic OHLCV series instead, purely so the pipeline can
be exercised end-to-end without a network call.

What it checks, in order:
    1. Load raw data (real if present, synthetic fallback otherwise)
    2. Run the full pipeline: EDA -> preprocessing -> Phase 3+4 features -> selection -> storage
    3. Print output file locations and a feature-count summary per group
"""

import sys
from pathlib import Path

# Allow running this script directly (python scripts/run_feature_engineering_demo.py)
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from ai.feature_engineering import FeatureEngineeringPipeline  # noqa: E402
from ai.feature_engineering.data_loader import find_raw_ohlcv_files  # noqa: E402

PASS = "\033[92mPASS\033[0m"
FAIL = "\033[91mFAIL\033[0m"
INFO = "\033[94mINFO\033[0m"


def _synthetic_ohlcv(ticker: str, n: int = 300) -> pd.DataFrame:
    rng = np.random.default_rng(7)
    dates = pd.bdate_range("2023-01-02", periods=n)
    close = 100 + np.cumsum(rng.normal(0.05, 1.5, n))
    close = np.maximum(close, 5)
    open_ = close + rng.normal(0, 0.5, n)
    high = np.maximum(open_, close) + np.abs(rng.normal(0.3, 0.3, n))
    low = np.minimum(open_, close) - np.abs(rng.normal(0.3, 0.3, n))
    volume = rng.integers(1_000_000, 5_000_000, n)
    return pd.DataFrame({
        "date": dates, "ticker": ticker, "open": open_, "high": high,
        "low": low, "close": close, "volume": volume,
    })


def main() -> int:
    ticker = sys.argv[1].upper() if len(sys.argv) > 1 else "DEMO"

    print("=" * 70)
    print(f"Sprint 2 Feature Engineering Demo — ticker={ticker}")
    print("=" * 70)

    pipeline = FeatureEngineeringPipeline()
    raw_files = find_raw_ohlcv_files(ticker)

    if raw_files:
        print(f"  [{INFO}] Found real Sprint 1 raw data: {raw_files[-1]}")
        run_kwargs = {"ticker": ticker}
    else:
        print(f"  [{INFO}] No raw OHLCV file found for '{ticker}' under datasets/raw/. "
              "Using synthetic data for this demo run instead.")
        run_kwargs = {"raw_df": _synthetic_ohlcv(ticker)}

    try:
        result = pipeline.run(version="demo", **run_kwargs)
    except Exception as e:
        print(f"  [{FAIL}] Pipeline run failed: {e}")
        return 1

    print(f"  [{PASS}] Pipeline completed in {result.duration_seconds:.2f}s")
    print()
    print("-" * 70)
    print(f"Rows:    {result.rows_in} -> {result.rows_out}")
    print(f"Columns: {result.columns_out} (raw OHLCV + {len(result.feature_definitions)} generated features)")
    print("-" * 70)

    by_group: dict[str, int] = {}
    for d in result.feature_definitions:
        by_group[d.group] = by_group.get(d.group, 0) + 1
    for group, count in by_group.items():
        print(f"  {group:<20} {count:>3} feature(s)")

    print("-" * 70)
    print("Selection analysis:")
    print(f"  Highly correlated pairs: {len(result.selection_report.highly_correlated_pairs)}")
    print(f"  Low-variance features:   {len(result.selection_report.low_variance_features)}")
    print(f"  Duplicate feature groups:{len(result.selection_report.duplicate_feature_groups)}")

    print("-" * 70)
    print("Output files:")
    for label, path in [
        ("EDA report (json)", result.eda_json_path),
        ("EDA report (md)", result.eda_md_path),
        ("Processed dataset", result.processed_csv_path),
        ("Feature metadata", result.metadata_json_path),
        ("Feature summary", result.summary_csv_path),
        ("Feature report", result.feature_report_md_path),
    ]:
        print(f"  {label:<20} {path}")
    print("=" * 70)

    return 0


if __name__ == "__main__":
    sys.exit(main())
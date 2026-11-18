"""
Phase 2 — Data Preprocessing for `ai/feature_engineering/`.

Cleans a raw OHLCV DataFrame (as produced by
`ai.feature_engineering.data_loader.load_raw_ohlcv`) before any feature is
computed: missing values, duplicates, date parsing/sorting, ticker/numeric
validation, outlier flagging, and invalid-row detection. Every step logs what
it changed and returns a `CleaningReport` so the EDA/data-quality report
(Phase 1 deliverable) can show exactly what preprocessing did.
"""

from dataclasses import dataclass, field
from typing import Optional

import numpy as np
import pandas as pd

from ai.feature_engineering.exceptions import InsufficientDataError, SchemaValidationError
from ai.utils.logger import get_logger
from ai.utils.validators import ValidationError, validate_ticker

logger = get_logger(__name__)

NUMERIC_OHLCV_COLUMNS = ("open", "high", "low", "close", "volume")
MIN_ROWS_AFTER_CLEANING = 30  # below this, most rolling-window features are meaningless


@dataclass
class CleaningReport:
    """Summary of every change `clean_ohlcv` made, for the data-quality report."""

    rows_in: int = 0
    rows_out: int = 0
    duplicates_removed: int = 0
    missing_values_before: dict = field(default_factory=dict)
    missing_values_filled: dict = field(default_factory=dict)
    invalid_rows_dropped: int = 0
    outliers_flagged: int = 0
    date_parse_failures: int = 0
    ticker_normalized: Optional[str] = None
    notes: list[str] = field(default_factory=list)

    def as_dict(self) -> dict:
        return {
            "rows_in": self.rows_in,
            "rows_out": self.rows_out,
            "duplicates_removed": self.duplicates_removed,
            "missing_values_before": self.missing_values_before,
            "missing_values_filled": self.missing_values_filled,
            "invalid_rows_dropped": self.invalid_rows_dropped,
            "outliers_flagged": self.outliers_flagged,
            "date_parse_failures": self.date_parse_failures,
            "ticker_normalized": self.ticker_normalized,
            "notes": self.notes,
        }


def _parse_and_sort_dates(df: pd.DataFrame, report: CleaningReport) -> pd.DataFrame:
    before = len(df)
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    failures = int(df["date"].isna().sum())
    if failures:
        report.date_parse_failures = failures
        report.notes.append(f"Dropped {failures} row(s) with unparseable dates.")
        df = df.dropna(subset=["date"])
    df = df.sort_values("date").reset_index(drop=True)
    if len(df) != before - failures:
        report.notes.append("Unexpected row count change during date parsing.")
    return df


def _remove_duplicates(df: pd.DataFrame, report: CleaningReport) -> pd.DataFrame:
    before = len(df)
    df = df.drop_duplicates(subset=["date", "ticker"], keep="last")
    report.duplicates_removed = before - len(df)
    if report.duplicates_removed:
        report.notes.append(f"Removed {report.duplicates_removed} duplicate (date, ticker) row(s).")
    return df.reset_index(drop=True)


def _validate_ticker_column(df: pd.DataFrame, report: CleaningReport) -> pd.DataFrame:
    if "ticker" not in df.columns:
        raise SchemaValidationError("ticker column missing before validation", missing_columns=["ticker"])

    unique_tickers = df["ticker"].dropna().unique()
    if len(unique_tickers) == 0:
        raise SchemaValidationError("ticker column is entirely empty")
    if len(unique_tickers) > 1:
        report.notes.append(
            f"Multiple tickers found in one file ({list(unique_tickers)}); this pipeline "
            "processes a single ticker at a time — keeping the most frequent one."
        )
        keep = df["ticker"].value_counts().idxmax()
        df = df[df["ticker"] == keep].reset_index(drop=True)

    try:
        normalized = validate_ticker(str(df["ticker"].iloc[0]))
    except ValidationError as e:
        raise SchemaValidationError(f"invalid ticker in data: {e}") from e

    df["ticker"] = normalized
    report.ticker_normalized = normalized
    return df


def _coerce_numeric(df: pd.DataFrame, report: CleaningReport) -> pd.DataFrame:
    for col in NUMERIC_OHLCV_COLUMNS:
        if col not in df.columns:
            raise SchemaValidationError(f"required numeric column '{col}' missing", missing_columns=[col])
        report.missing_values_before[col] = int(df[col].isna().sum())
        df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def _drop_invalid_rows(df: pd.DataFrame, report: CleaningReport) -> pd.DataFrame:
    """Drop rows that are structurally impossible for a price bar:
    non-positive prices/volume, or high/low that don't bound open/close.
    """
    before = len(df)
    valid = (
        (df["open"] > 0)
        & (df["high"] > 0)
        & (df["low"] > 0)
        & (df["close"] > 0)
        & (df["volume"] >= 0)
        & (df["high"] >= df[["open", "close", "low"]].max(axis=1))
        & (df["low"] <= df[["open", "close", "high"]].min(axis=1))
    )
    df = df[valid.fillna(False)].reset_index(drop=True)
    report.invalid_rows_dropped = before - len(df)
    if report.invalid_rows_dropped:
        report.notes.append(
            f"Dropped {report.invalid_rows_dropped} structurally invalid OHLC row(s) "
            "(non-positive price/volume or high/low not bounding open/close)."
        )
    return df


def _fill_missing_values(df: pd.DataFrame, report: CleaningReport) -> pd.DataFrame:
    """Forward-fill missing OHLCV values (standard for price series — a
    missing bar is best approximated by the last known price), then
    back-fill any remaining leading NaNs. Missing volume is filled with 0
    rather than forward-filled, since a missing volume print is not the same
    as "volume unchanged".
    """
    filled_counts: dict = {}
    for col in ("open", "high", "low", "close"):
        n_before = int(df[col].isna().sum())
        if n_before:
            df[col] = df[col].ffill().bfill()
            filled_counts[col] = n_before - int(df[col].isna().sum())

    n_vol_before = int(df["volume"].isna().sum())
    if n_vol_before:
        df["volume"] = df["volume"].fillna(0)
        filled_counts["volume"] = n_vol_before

    report.missing_values_filled = filled_counts
    if filled_counts:
        report.notes.append(f"Filled missing values: {filled_counts}.")
    return df


def _flag_outliers(df: pd.DataFrame, report: CleaningReport, z_threshold: float = 6.0) -> pd.DataFrame:
    """Flag (not drop) extreme single-day returns via a z-score on daily
    percentage return. Outliers are kept — genuine earnings-day gaps and
    splits look like outliers too — but flagged in `is_price_outlier` so
    downstream models/analysts can choose to exclude them.
    """
    daily_return = df["close"].pct_change()
    std = daily_return.std(ddof=0)
    if not std or np.isnan(std):
        df["is_price_outlier"] = False
        return df
    z = (daily_return - daily_return.mean()) / std
    df["is_price_outlier"] = z.abs() > z_threshold
    report.outliers_flagged = int(df["is_price_outlier"].sum())
    if report.outliers_flagged:
        report.notes.append(
            f"Flagged {report.outliers_flagged} row(s) as price outliers (|z| > {z_threshold} on daily return); "
            "not removed."
        )
    return df


def clean_ohlcv(raw_df: pd.DataFrame) -> tuple[pd.DataFrame, CleaningReport]:
    """Run the full Phase 2 cleaning pipeline on a raw OHLCV DataFrame.

    Returns:
        (cleaned_df, CleaningReport)

    Raises:
        SchemaValidationError: required columns are missing or unusable.
        InsufficientDataError: fewer than MIN_ROWS_AFTER_CLEANING rows remain.
    """
    df = raw_df.copy()
    report = CleaningReport(rows_in=len(df))

    df = _validate_ticker_column(df, report)
    df = _parse_and_sort_dates(df, report)
    df = _remove_duplicates(df, report)
    df = _coerce_numeric(df, report)
    df = _fill_missing_values(df, report)
    df = _drop_invalid_rows(df, report)
    df = _flag_outliers(df, report)

    report.rows_out = len(df)

    if len(df) < MIN_ROWS_AFTER_CLEANING:
        raise InsufficientDataError(
            MIN_ROWS_AFTER_CLEANING, len(df),
            context={"ticker": df["ticker"].iloc[0] if len(df) else None},
        )

    logger.info(
        "Cleaned OHLCV data: %d -> %d rows (removed %d duplicates, %d invalid rows, flagged %d outliers)",
        report.rows_in, report.rows_out, report.duplicates_removed,
        report.invalid_rows_dropped, report.outliers_flagged,
    )
    return df, report
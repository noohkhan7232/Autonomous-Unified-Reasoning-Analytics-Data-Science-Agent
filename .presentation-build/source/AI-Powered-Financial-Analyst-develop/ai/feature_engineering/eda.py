"""
Phase 1 — Lightweight Exploratory Data Analysis.

Produces a concise data profile (shape, dtypes, missing values, duplicates,
summary stats, correlation, price/volume distribution, trend, data-quality
notes) and writes it to `storage/reports/eda/`. Per the sprint brief this is
intentionally lightweight text/markdown, not a visualization-heavy report —
the primary effort budget goes to feature engineering.
"""

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from ai.feature_engineering.preprocessing import CleaningReport
from ai.utils.config import settings
from ai.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class EDAReport:
    ticker: str
    generated_at: str
    shape: tuple = ()
    dtypes: dict = field(default_factory=dict)
    missing_values: dict = field(default_factory=dict)
    duplicate_rows: int = 0
    summary_statistics: dict = field(default_factory=dict)
    correlation_matrix: dict = field(default_factory=dict)
    price_distribution: dict = field(default_factory=dict)
    volume_distribution: dict = field(default_factory=dict)
    time_series_trend: dict = field(default_factory=dict)
    cleaning_report: dict = field(default_factory=dict)

    def as_dict(self) -> dict:
        return asdict(self)


def profile_raw_data(raw_df: pd.DataFrame, ticker: str, cleaning_report: CleaningReport) -> EDAReport:
    """Compute the Phase 1 profile from the *raw* (pre-cleaning) DataFrame,
    annotated with what `preprocessing.clean_ohlcv` subsequently changed.
    """
    numeric_cols = [c for c in ("open", "high", "low", "close", "volume") if c in raw_df.columns]

    price_cols = [c for c in ("open", "high", "low", "close") if c in raw_df.columns]
    price_stats = raw_df[price_cols].describe().to_dict() if price_cols else {}
    volume_stats = raw_df["volume"].describe().to_dict() if "volume" in raw_df.columns else {}

    trend = {}
    if "close" in raw_df.columns and len(raw_df) > 1:
        first_close, last_close = raw_df["close"].iloc[0], raw_df["close"].iloc[-1]
        trend = {
            "first_close": float(first_close),
            "last_close": float(last_close),
            "net_change_pct": float((last_close - first_close) / first_close * 100) if first_close else None,
            "min_close": float(raw_df["close"].min()),
            "max_close": float(raw_df["close"].max()),
        }

    return EDAReport(
        ticker=ticker,
        generated_at=datetime.now(timezone.utc).isoformat(),
        shape=tuple(raw_df.shape),
        dtypes={c: str(t) for c, t in raw_df.dtypes.items()},
        missing_values={c: int(raw_df[c].isna().sum()) for c in raw_df.columns},
        duplicate_rows=int(raw_df.duplicated().sum()),
        summary_statistics=raw_df[numeric_cols].describe().to_dict() if numeric_cols else {},
        correlation_matrix=raw_df[numeric_cols].corr().round(4).to_dict() if len(numeric_cols) > 1 else {},
        price_distribution=price_stats,
        volume_distribution=volume_stats,
        time_series_trend=trend,
        cleaning_report=cleaning_report.as_dict(),
    )


def _fmt_table(rows: list[tuple[str, str]]) -> str:
    lines = ["| Field | Value |", "|---|---|"]
    lines += [f"| {k} | {v} |" for k, v in rows]
    return "\n".join(lines)


def render_markdown(report: EDAReport) -> str:
    lines = [
        f"# EDA Report — {report.ticker}",
        f"_Generated: {report.generated_at}_",
        "",
        "## Dataset Shape",
        f"{report.shape[0]} rows x {report.shape[1]} columns",
        "",
        "## Data Types",
        _fmt_table(list(report.dtypes.items())),
        "",
        "## Missing Values (raw, before cleaning)",
        _fmt_table([(k, str(v)) for k, v in report.missing_values.items() if v]) or "No missing values.",
        "",
        "## Duplicate Rows (raw)",
        str(report.duplicate_rows),
        "",
        "## Time Series Trend",
        _fmt_table([(k, str(v)) for k, v in report.time_series_trend.items()]) if report.time_series_trend else "N/A",
        "",
        "## Data Quality Report (Phase 2 cleaning outcome)",
        _fmt_table([(k, str(v)) for k, v in report.cleaning_report.items() if k != "notes"]),
        "",
        "### Cleaning Notes",
        "\n".join(f"- {n}" for n in report.cleaning_report.get("notes", [])) or "- None",
        "",
        "## Summary Statistics, Price/Volume Distribution, Correlation Matrix",
        "See the accompanying `.json` report for full numeric detail "
        "(kept out of this markdown file to stay lightweight per Sprint 2 scope).",
    ]
    return "\n".join(lines)


def save_eda_report(report: EDAReport) -> tuple[Path, Path]:
    """Write both a `.json` (full detail) and `.md` (human-readable summary)
    EDA report to `storage/reports/eda/`. Returns (json_path, md_path).
    """
    out_dir = settings.resolve(settings.eda_reports_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    json_path = out_dir / f"{report.ticker}_eda_report.json"
    md_path = out_dir / f"{report.ticker}_eda_report.md"

    json_path.write_text(json.dumps(report.as_dict(), indent=2, default=str), encoding="utf-8")
    md_path.write_text(render_markdown(report), encoding="utf-8")

    logger.info("Saved EDA report for %s to %s and %s", report.ticker, json_path, md_path)
    return json_path, md_path
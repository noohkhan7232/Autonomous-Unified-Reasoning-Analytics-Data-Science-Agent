"""
Persistence helpers for `ai/feature_engineering/`.

Mirrors `ai/data_collection/storage.py`: atomic writes (temp file + rename)
so a crash mid-write never leaves a corrupt file where downstream code
(Sprint 3 model training) expects a valid one. Satisfies the sprint's output
requirements: `datasets/processed/`, `Feature_Metadata.json`,
`Feature_Report.md`, `Feature_Summary.csv`.
"""

import json
import os
from pathlib import Path
from typing import Union

import pandas as pd

from ai.feature_engineering.exceptions import StorageError
from ai.feature_engineering.features.base import FeatureDefinition
from ai.feature_engineering.selection import FeatureSelectionReport
from ai.utils.config import settings
from ai.utils.logger import get_logger

logger = get_logger(__name__)


def _processed_data_dir() -> Path:
    path = settings.resolve(settings.processed_data_dir)
    path.mkdir(parents=True, exist_ok=True)
    return path


def _atomic_write(path: Path, write_fn) -> None:
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    try:
        write_fn(tmp_path)
        os.replace(tmp_path, path)
    except OSError as e:
        raise StorageError(f"failed writing '{path}': {e}") from e
    finally:
        if tmp_path.exists():
            try:
                tmp_path.unlink()
            except OSError:
                pass


def save_processed_dataset(df: pd.DataFrame, ticker: str, version: str) -> Path:
    """Save the fully feature-engineered DataFrame to
    `datasets/processed/{ticker}_{version}_features.csv` (FR-2.3: versioned
    processed datasets, traceable to the run that produced them).
    """
    filename = f"{ticker}_{version}_features.csv"
    path = _processed_data_dir() / filename
    _atomic_write(path, lambda tmp: df.to_csv(tmp, index=False))
    logger.info("Saved %d processed rows x %d columns to %s", len(df), df.shape[1], path)
    return path


def _write_json(tmp_path: Path, data: Union[dict, list]) -> None:
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, default=str)


def save_feature_metadata(definitions: list[FeatureDefinition], ticker: str, version: str) -> Path:
    """Save `Feature_Metadata.json`: one entry per generated column."""
    filename = f"{ticker}_{version}_Feature_Metadata.json"
    path = _processed_data_dir() / filename
    payload = {"ticker": ticker, "version": version, "features": [d.as_dict() for d in definitions]}
    _atomic_write(path, lambda tmp: _write_json(tmp, payload))
    logger.info("Saved metadata for %d feature(s) to %s", len(definitions), path)
    return path


def save_feature_summary_csv(df: pd.DataFrame, ticker: str, version: str) -> Path:
    """Save `Feature_Summary.csv`: `describe()` transposed, one row per column."""
    filename = f"{ticker}_{version}_Feature_Summary.csv"
    path = _processed_data_dir() / filename
    numeric_df = df.select_dtypes(include="number")
    summary = numeric_df.describe().transpose()
    summary["missing_count"] = df[numeric_df.columns].isna().sum()
    summary["dtype"] = [str(df[c].dtype) for c in numeric_df.columns]
    _atomic_write(path, lambda tmp: summary.to_csv(tmp))
    logger.info("Saved feature summary (%d numeric columns) to %s", len(numeric_df.columns), path)
    return path


def render_feature_report_markdown(
    definitions: list[FeatureDefinition], selection_report: FeatureSelectionReport, ticker: str, version: str
) -> str:
    by_group: dict[str, list[FeatureDefinition]] = {}
    for d in definitions:
        by_group.setdefault(d.group, []).append(d)

    lines = [f"# Feature Report — {ticker} ({version})", ""]
    for group, defs in by_group.items():
        lines.append(f"## {group}")
        for d in defs:
            lines += [
                f"### `{d.name}`  _(Priority: {d.priority})_",
                f"- **Formula:** {d.formula}",
                f"- **Meaning:** {d.meaning}",
                f"- **Interpretation:** {d.interpretation}",
                f"- **Recommended for:** {', '.join(d.recommended_for) or 'N/A'}",
            ]
            if d.advantages:
                lines.append(f"- **Advantages:** {d.advantages}")
            if d.limitations:
                lines.append(f"- **Limitations:** {d.limitations}")
            if d.when_to_use:
                lines.append(f"- **When to use:** {d.when_to_use}")
            lines.append("")

    lines += ["## Feature Selection Analysis", ""]
    lines.append(f"### Highly Correlated Pairs (>= threshold)")
    if selection_report.highly_correlated_pairs:
        lines.append("| Feature A | Feature B | Correlation |")
        lines.append("|---|---|---|")
        for a, b, corr in selection_report.highly_correlated_pairs:
            lines.append(f"| {a} | {b} | {corr:.4f} |")
    else:
        lines.append("None found.")
    lines.append("")
    lines.append("### Low-Variance Features")
    lines.append(", ".join(selection_report.low_variance_features) or "None found.")
    lines.append("")
    lines.append("### Duplicate Feature Groups")
    if selection_report.duplicate_feature_groups:
        for group in selection_report.duplicate_feature_groups:
            lines.append(f"- {', '.join(group)}")
    else:
        lines.append("None found.")

    return "\n".join(lines)


def save_feature_report(
    definitions: list[FeatureDefinition], selection_report: FeatureSelectionReport, ticker: str, version: str
) -> Path:
    filename = f"{ticker}_{version}_Feature_Report.md"
    path = _processed_data_dir() / filename
    content = render_feature_report_markdown(definitions, selection_report, ticker, version)
    _atomic_write(path, lambda tmp: tmp.write_text(content, encoding="utf-8"))
    logger.info("Saved feature report to %s", path)
    return path
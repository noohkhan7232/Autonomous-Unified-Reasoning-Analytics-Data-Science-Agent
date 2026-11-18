"""
Feature Selection analysis for `ai/feature_engineering/`.

Does not drop any columns itself (that decision belongs to each downstream
model's training code in Sprint 3+) — it *reports* which generated features
are highly correlated, near-constant, or exact duplicates of each other, so
consumers can make an informed choice per model family.
"""

from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from ai.feature_engineering.config import FeatureEngineeringConfig
from ai.utils.logger import get_logger

logger = get_logger(__name__)

# Columns that are identifiers/targets/labels, never candidates for correlation-based pruning.
_EXCLUDE_FROM_SELECTION_PREFIXES = ("target_", "future_return_")
_EXCLUDE_FROM_SELECTION_COLUMNS = {"date", "ticker", "year", "month", "day", "week", "quarter", "day_of_week"}


@dataclass
class FeatureSelectionReport:
    highly_correlated_pairs: list[tuple[str, str, float]] = field(default_factory=list)
    low_variance_features: list[str] = field(default_factory=list)
    duplicate_feature_groups: list[list[str]] = field(default_factory=list)

    def as_dict(self) -> dict:
        return {
            "highly_correlated_pairs": [
                {"feature_a": a, "feature_b": b, "correlation": round(c, 4)}
                for a, b, c in self.highly_correlated_pairs
            ],
            "low_variance_features": self.low_variance_features,
            "duplicate_feature_groups": self.duplicate_feature_groups,
        }


def _numeric_candidate_columns(df: pd.DataFrame) -> list[str]:
    numeric_cols = df.select_dtypes(include=[np.number, "bool", "boolean"]).columns
    return [
        c for c in numeric_cols
        if c not in _EXCLUDE_FROM_SELECTION_COLUMNS and not c.startswith(_EXCLUDE_FROM_SELECTION_PREFIXES)
    ]


def analyze_features(df: pd.DataFrame, config: FeatureEngineeringConfig) -> FeatureSelectionReport:
    """Run correlation, low-variance, and duplicate-column analysis over the
    generated (non-target) numeric/boolean feature columns.
    """
    candidates = _numeric_candidate_columns(df)
    report = FeatureSelectionReport()
    if len(candidates) < 2:
        return report

    numeric_df = df[candidates].astype(float)

    # --- Highly correlated pairs (upper triangle only, to avoid duplicate/self pairs) ---
    corr = numeric_df.corr().abs()
    upper = corr.where(np.triu(np.ones(corr.shape), k=1).astype(bool))
    for col in upper.columns:
        for row in upper.index:
            value = upper.loc[row, col]
            if pd.notna(value) and value >= config.high_correlation_threshold:
                report.highly_correlated_pairs.append((row, col, float(value)))
    report.highly_correlated_pairs.sort(key=lambda t: -t[2])

    # --- Low-variance features ---
    variances = numeric_df.var(skipna=True)
    report.low_variance_features = sorted(
        variances[variances.fillna(0) < config.low_variance_threshold].index.tolist()
    )

    # --- Exact duplicate columns (identical values wherever both are non-null) ---
    seen: dict[tuple, list[str]] = {}
    for col in candidates:
        key = tuple(numeric_df[col].fillna(np.nan).round(10).tolist())
        seen.setdefault(key, []).append(col)
    report.duplicate_feature_groups = [group for group in seen.values() if len(group) > 1]

    logger.info(
        "Feature selection: %d highly-correlated pair(s), %d low-variance feature(s), %d duplicate group(s)",
        len(report.highly_correlated_pairs), len(report.low_variance_features), len(report.duplicate_feature_groups),
    )
    return report
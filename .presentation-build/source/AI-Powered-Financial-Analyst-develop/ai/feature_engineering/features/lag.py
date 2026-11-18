"""
Phase 3.I — Lag Features.

Directly exposes past values as columns on today's row — the standard way
to turn a time series into a supervised-learning table for ML models that
have no inherent notion of sequence (unlike LSTM/GRU, which take raw
sequences instead — see SRS FR-5.4).
"""

import pandas as pd

from ai.feature_engineering.features.base import BaseFeatureGenerator, FeatureDefinition

_LAG_SOURCE_COLUMNS = {
    "close": "close",
    "open": "open",
    "high": "high",
    "low": "low",
    "volume": "volume",
}


class LagFeatureGenerator(BaseFeatureGenerator):
    group_name = "lag"
    # `pct_return` is produced by the price group, which must run before this one.
    requires_columns = ("close", "open", "high", "low", "volume")

    def _compute(self, df: pd.DataFrame) -> pd.DataFrame:
        for label, col in _LAG_SOURCE_COLUMNS.items():
            for lag in self.config.lag_periods:
                df[f"{label}_lag_{lag}"] = df[col].shift(lag)

        return_col = "pct_return" if "pct_return" in df.columns else None
        if return_col:
            for lag in self.config.lag_periods:
                df[f"return_lag_{lag}"] = df[return_col].shift(lag)
        return df

    def describe(self) -> list[FeatureDefinition]:
        defs = []
        for label in _LAG_SOURCE_COLUMNS:
            for lag in self.config.lag_periods:
                defs.append(FeatureDefinition(
                    name=f"{label}_lag_{lag}", group=self.group_name,
                    formula=f"{label.capitalize()}(t - {lag})",
                    meaning=f"{label.capitalize()} value from {lag} day(s) ago.",
                    interpretation="Gives non-sequential models (e.g. Random Forest) direct access to recent history.",
                    priority="High" if lag in (1, 2, 3) else "Medium",
                    recommended_for=("Machine Learning",),
                    limitations="Redundant for LSTM/GRU, which already consume sequences (FR-5.4) — only needed for non-sequential models.",
                    when_to_use="Tabular ML models (Random Forest, XGBoost, Linear Regression).",
                ))
        for lag in self.config.lag_periods:
            defs.append(FeatureDefinition(
                name=f"return_lag_{lag}", group=self.group_name,
                formula=f"pct_return(t - {lag})",
                meaning=f"Percentage return from {lag} day(s) ago.",
                interpretation="Lets a model see recent return momentum/mean-reversion patterns directly.",
                priority="High" if lag in (1, 2, 3) else "Medium",
                recommended_for=("Machine Learning",),
            ))
        return defs
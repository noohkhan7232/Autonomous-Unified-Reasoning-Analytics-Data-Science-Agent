"""
Phase 3.H — Generic Rolling Window Features.

Distinct from the indicator-specific rolling calculations above (SMA, ATR,
Bollinger, ...), these are generic descriptive statistics over a rolling
window of closing price, useful as low-level, model-agnostic inputs
(especially for tree-based ML models that can find their own interactions).
"""

import pandas as pd

from ai.feature_engineering.features.base import BaseFeatureGenerator, FeatureDefinition


class RollingFeatureGenerator(BaseFeatureGenerator):
    group_name = "rolling"

    def _compute(self, df: pd.DataFrame) -> pd.DataFrame:
        for w in self.config.rolling_stat_windows:
            roll = df["close"].rolling(window=w, min_periods=w)
            df[f"rolling_mean_{w}"] = roll.mean()
            df[f"rolling_median_{w}"] = roll.median()
            df[f"rolling_max_{w}"] = roll.max()
            df[f"rolling_min_{w}"] = roll.min()
            df[f"rolling_std_{w}"] = roll.std()
            df[f"rolling_var_{w}"] = roll.var()
        return df

    def describe(self) -> list[FeatureDefinition]:
        defs = []
        for w in self.config.rolling_stat_windows:
            for stat, meaning in [
                ("mean", "average"), ("median", "median"), ("max", "maximum"),
                ("min", "minimum"), ("std", "standard deviation"), ("var", "variance"),
            ]:
                defs.append(FeatureDefinition(
                    name=f"rolling_{stat}_{w}", group=self.group_name,
                    formula=f"{meaning}(Close, last {w} days)",
                    meaning=f"Rolling {w}-day {meaning} of closing price.",
                    interpretation="General-purpose descriptive statistic; combined with the current close it lets a model infer relative positioning cheaply.",
                    priority="Medium" if stat in ("mean", "std") else "Low",
                    recommended_for=("Machine Learning",),
                    when_to_use="Feed as raw model-agnostic inputs to tree-based ML (Random Forest / XGBoost), which can learn nonlinear combinations on its own.",
                ))
        return defs
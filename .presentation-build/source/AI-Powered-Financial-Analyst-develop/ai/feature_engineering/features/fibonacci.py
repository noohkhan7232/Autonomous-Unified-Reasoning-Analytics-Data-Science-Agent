"""
Phase 4.D — Fibonacci Analysis Features.

Levels are computed against the current swing range established by
`support_resistance.py` (`dynamic_support` -> `dynamic_resistance`), so this
generator must run after `SupportResistanceFeatureGenerator`. Retracement
levels sit inside the swing range (potential pullback support in an
uptrend); extension levels project beyond the swing high (potential
continuation targets).
"""

import numpy as np
import pandas as pd

from ai.feature_engineering.features.base import BaseFeatureGenerator, FeatureDefinition

_RETRACEMENT_LEVELS = {"236": 0.236, "382": 0.382, "50": 0.5, "618": 0.618, "786": 0.786}
_EXTENSION_LEVELS = {"1272": 1.272, "1618": 1.618, "2618": 2.618}


class FibonacciFeatureGenerator(BaseFeatureGenerator):
    group_name = "fibonacci"
    requires_columns = ("close", "dynamic_support", "dynamic_resistance")

    def _compute(self, df: pd.DataFrame) -> pd.DataFrame:
        cfg = self.config
        low, high, close = df["dynamic_support"], df["dynamic_resistance"], df["close"]
        swing_range = (high - low)

        level_cols = []
        for suffix, ratio in {**_RETRACEMENT_LEVELS, **_EXTENSION_LEVELS}.items():
            col = f"fib_{suffix}"
            df[col] = low + ratio * swing_range
            level_cols.append(col)

        levels_df = df[level_cols]
        diffs = levels_df.sub(close, axis=0).abs()
        df["distance_from_fibonacci"] = diffs.min(axis=1) / close
        closest_idx = diffs.fillna(np.inf).idxmin(axis=1)
        df["closest_fibonacci_level"] = closest_idx.where(swing_range.notna())

        tol = cfg.support_resistance_tolerance_pct
        if {"static_support", "static_resistance"}.issubset(df.columns):
            confluence = pd.Series(False, index=df.index)
            for col in level_cols:
                for sr_col in ("static_support", "static_resistance"):
                    close_to_sr = (df[col] - df[sr_col]).abs() / close <= tol
                    confluence = confluence | close_to_sr.fillna(False)
            df["fibonacci_confluence"] = confluence
        else:
            df["fibonacci_confluence"] = pd.NA

        return df

    def describe(self) -> list[FeatureDefinition]:
        defs = []
        for suffix, ratio in _RETRACEMENT_LEVELS.items():
            defs.append(FeatureDefinition(
                name=f"fib_{suffix}", group=self.group_name,
                formula=f"dynamic_support + {ratio} * (dynamic_resistance - dynamic_support)",
                meaning=f"{ratio:.1%} Fibonacci retracement level of the current swing range.",
                interpretation="A common area for a pullback within the prevailing trend to find support/resistance.",
                priority="Medium", recommended_for=("Machine Learning", "Decision Engine"),
                limitations="Only as reliable as the underlying swing points (dynamic_support/dynamic_resistance), which repaint.",
            ))
        for suffix, ratio in _EXTENSION_LEVELS.items():
            defs.append(FeatureDefinition(
                name=f"fib_{suffix}", group=self.group_name,
                formula=f"dynamic_support + {ratio} * (dynamic_resistance - dynamic_support)",
                meaning=f"{ratio:.3f} Fibonacci extension level beyond the current swing range.",
                interpretation="A common projected target if the prevailing trend continues past the recent swing high.",
                priority="Low", recommended_for=("Machine Learning", "Decision Engine"),
            ))
        defs.append(FeatureDefinition(
            name="distance_from_fibonacci", group=self.group_name,
            formula="min(|Close - each fib level|) / Close",
            meaning="Normalized distance from price to the nearest Fibonacci level.",
            interpretation="Near zero = price is sitting right on a Fibonacci level.",
            priority="Medium", recommended_for=("Machine Learning",),
        ))
        defs.append(FeatureDefinition(
            name="closest_fibonacci_level", group=self.group_name,
            formula="argmin(|Close - each fib level|)",
            meaning="Name of the nearest Fibonacci level.",
            interpretation="Categorical feature identifying which level price is currently reacting to.",
            priority="Low", recommended_for=("Machine Learning",),
        ))
        defs.append(FeatureDefinition(
            name="fibonacci_confluence", group=self.group_name,
            formula=f"any fib level within {self.config.support_resistance_tolerance_pct:.1%} of static_support/static_resistance",
            meaning="A Fibonacci level lines up with an independent support/resistance level.",
            interpretation="Confluence of multiple methods at the same price is traditionally considered a stronger level.",
            priority="High", recommended_for=("Decision Engine", "Machine Learning"),
        ))
        return defs
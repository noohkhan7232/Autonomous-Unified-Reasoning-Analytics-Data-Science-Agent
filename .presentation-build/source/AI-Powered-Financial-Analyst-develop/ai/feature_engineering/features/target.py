"""
Target Features — future prediction labels.

Unlike every other generator, these look *forward* (`shift(-horizon)`), so
the most recent `max(target_horizons)` rows will always have NaN targets —
that's correct, not a bug: those are the rows the model would eventually be
asked to predict for a real ticker, and the true future isn't known yet.
"""

import pandas as pd

from ai.feature_engineering.features.base import BaseFeatureGenerator, FeatureDefinition


class TargetFeatureGenerator(BaseFeatureGenerator):
    group_name = "target"

    def _compute(self, df: pd.DataFrame) -> pd.DataFrame:
        close = df["close"]
        for h in self.config.target_horizons:
            future_close = close.shift(-h)
            df[f"target_{h}_day"] = future_close
            df[f"future_return_{h}_day"] = (future_close - close) / close
            df[f"target_direction_{h}_day"] = (future_close > close).astype("boolean")
            df.loc[future_close.isna(), f"target_direction_{h}_day"] = pd.NA
            df[f"target_regression_{h}_day"] = df[f"future_return_{h}_day"]
        return df

    def describe(self) -> list[FeatureDefinition]:
        defs = []
        for h in self.config.target_horizons:
            defs.append(FeatureDefinition(
                name=f"target_{h}_day", group=self.group_name,
                formula=f"Close(t + {h})",
                meaning=f"Raw future closing price {h} day(s) ahead.",
                interpretation="Regression label; NaN for the last few rows where the future isn't known yet.",
                priority="High", recommended_for=("Machine Learning", "Time Series", "Deep Learning"),
                when_to_use="Direct regression target for price-level prediction models.",
            ))
            defs.append(FeatureDefinition(
                name=f"future_return_{h}_day", group=self.group_name,
                formula=f"(Close(t+{h}) - Close(t)) / Close(t)",
                meaning=f"Percentage return over the next {h} day(s).",
                interpretation="Scale-invariant regression label, comparable across tickers.",
                priority="High", recommended_for=("Machine Learning", "Deep Learning"),
                when_to_use="Preferred regression target over raw price for cross-ticker models.",
            ))
            defs.append(FeatureDefinition(
                name=f"target_direction_{h}_day", group=self.group_name,
                formula=f"Close(t+{h}) > Close(t)",
                meaning=f"Binary up/down direction over the next {h} day(s).",
                interpretation="True = price rose; False = price fell or was flat.",
                priority="High", recommended_for=("Machine Learning", "Decision Engine"),
                when_to_use="Classification target for Buy/Hold/Sell-style signal models.",
            ))
            defs.append(FeatureDefinition(
                name=f"target_regression_{h}_day", group=self.group_name,
                formula=f"future_return_{h}_day",
                meaning="Alias of future_return, named explicitly as the regression target per spec.",
                interpretation="Identical values to future_return_*_day.",
                priority="Medium", recommended_for=("Machine Learning",),
            ))
        return defs
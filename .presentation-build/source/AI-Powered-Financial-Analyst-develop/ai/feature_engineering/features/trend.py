"""
Phase 3.B — Trend Features.

Moving averages smooth out day-to-day noise to reveal the underlying trend
direction. SMA weights every day in the window equally; EMA weights recent
days more heavily, so it reacts faster to new information.
"""

import pandas as pd

from ai.feature_engineering.features.base import BaseFeatureGenerator, FeatureDefinition


class TrendFeatureGenerator(BaseFeatureGenerator):
    group_name = "trend"

    def _compute(self, df: pd.DataFrame) -> pd.DataFrame:
        cfg = self.config
        for w in cfg.sma_windows:
            df[f"sma_{w}"] = df["close"].rolling(window=w, min_periods=w).mean()
        for w in cfg.ema_windows:
            df[f"ema_{w}"] = df["close"].ewm(span=w, adjust=False, min_periods=w).mean()

        fast, slow = cfg.golden_death_cross_fast, cfg.golden_death_cross_slow
        fast_col, slow_col = f"sma_{fast}", f"sma_{slow}"
        if fast_col not in df.columns:
            df[fast_col] = df["close"].rolling(window=fast, min_periods=fast).mean()
        if slow_col not in df.columns:
            df[slow_col] = df["close"].rolling(window=slow, min_periods=slow).mean()

        above = (df[fast_col] > df[slow_col]).astype("boolean")
        prev_above = above.shift(1)
        df["golden_cross"] = (above & ~prev_above.fillna(False)).astype("boolean")
        df["death_cross"] = (~above & prev_above.fillna(False)).astype("boolean")
        df.loc[df[fast_col].isna() | df[slow_col].isna(), ["golden_cross", "death_cross"]] = pd.NA
        return df

    def describe(self) -> list[FeatureDefinition]:
        defs = []
        for w in self.config.sma_windows:
            defs.append(FeatureDefinition(
                name=f"sma_{w}", group=self.group_name,
                formula=f"mean(Close, last {w} days)",
                meaning=f"{w}-day Simple Moving Average.",
                interpretation="Price above SMA = uptrend bias; below = downtrend bias. Longer windows = smoother, laggier.",
                priority="High" if w in (20, 50, 200) else "Medium",
                recommended_for=("Machine Learning", "Time Series", "Decision Engine"),
                advantages="Simple, robust, widely understood baseline trend measure.",
                limitations=f"Lags price by ~{w // 2} days; whipsaws in sideways markets.",
                when_to_use="Trend-following features, crossover signals (see golden_cross/death_cross).",
            ))
        for w in self.config.ema_windows:
            defs.append(FeatureDefinition(
                name=f"ema_{w}", group=self.group_name,
                formula=f"EWMA(Close, span={w})",
                meaning=f"{w}-day Exponential Moving Average.",
                interpretation="Reacts faster to recent price changes than the equivalent SMA.",
                priority="High" if w in (12, 20, 26, 50) else "Medium",
                recommended_for=("Machine Learning", "Deep Learning", "Decision Engine"),
                advantages="More responsive to new information than SMA; underlies MACD.",
                limitations="More sensitive to short-term noise/whipsaws than SMA.",
                when_to_use="Faster trend signal, or as an input to MACD-style features.",
            ))
        defs.append(FeatureDefinition(
            name="golden_cross", group=self.group_name,
            formula=f"sma_{self.config.golden_death_cross_fast} crosses above sma_{self.config.golden_death_cross_slow}",
            meaning="Bullish long-term trend-change signal (classically 50-day crossing above 200-day).",
            interpretation="True on the single day the fast SMA first exceeds the slow SMA.",
            priority="High", recommended_for=("Decision Engine", "Machine Learning"),
            advantages="Well-known, widely referenced signal; easy to explain to end users.",
            limitations="Lagging by construction (needs the crossover to already happen); frequent false signals in choppy markets.",
            when_to_use="Long-horizon regime/trend-change feature, not short-term timing.",
        ))
        defs.append(FeatureDefinition(
            name="death_cross", group=self.group_name,
            formula=f"sma_{self.config.golden_death_cross_fast} crosses below sma_{self.config.golden_death_cross_slow}",
            meaning="Bearish long-term trend-change signal.",
            interpretation="True on the single day the fast SMA first drops below the slow SMA.",
            priority="High", recommended_for=("Decision Engine", "Machine Learning"),
            limitations="Same lag/false-signal caveats as golden_cross.",
            when_to_use="Long-horizon regime/trend-change feature.",
        ))
        return defs
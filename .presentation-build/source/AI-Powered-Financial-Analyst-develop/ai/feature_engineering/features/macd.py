"""
Phase 3.F — MACD (Moving Average Convergence Divergence).

Measures the relationship between two EMAs of different speeds, turning the
"trend vs. trend" comparison into a momentum-style oscillator.
"""

import pandas as pd

from ai.feature_engineering.features.base import BaseFeatureGenerator, FeatureDefinition


class MACDFeatureGenerator(BaseFeatureGenerator):
    group_name = "macd"

    def _compute(self, df: pd.DataFrame) -> pd.DataFrame:
        cfg = self.config
        fast_ema = df["close"].ewm(span=cfg.macd_fast_period, adjust=False, min_periods=cfg.macd_fast_period).mean()
        slow_ema = df["close"].ewm(span=cfg.macd_slow_period, adjust=False, min_periods=cfg.macd_slow_period).mean()

        macd_line = fast_ema - slow_ema
        signal_line = macd_line.ewm(
            span=cfg.macd_signal_period, adjust=False, min_periods=cfg.macd_signal_period
        ).mean()

        df["macd_line"] = macd_line
        df["macd_signal"] = signal_line
        df["macd_histogram"] = macd_line - signal_line
        return df

    def describe(self) -> list[FeatureDefinition]:
        cfg = self.config
        return [
            FeatureDefinition(
                name="macd_line", group=self.group_name,
                formula=f"EMA(Close, {cfg.macd_fast_period}) - EMA(Close, {cfg.macd_slow_period})",
                meaning="Difference between the fast and slow EMA.",
                interpretation="Positive = fast EMA above slow EMA (bullish momentum); negative = bearish momentum.",
                priority="High", recommended_for=("Machine Learning", "Decision Engine"),
                advantages="Combines trend and momentum in one line; widely used and well understood.",
                limitations="Lagging (built from EMAs); less useful in strongly sideways/choppy markets.",
                when_to_use="Trend-momentum confirmation alongside RSI.",
            ),
            FeatureDefinition(
                name="macd_signal", group=self.group_name,
                formula=f"EMA(macd_line, {cfg.macd_signal_period})",
                meaning="Smoothed trigger line for the MACD line.",
                interpretation="Crossovers of macd_line above/below macd_signal are classic buy/sell triggers.",
                priority="High", recommended_for=("Machine Learning", "Decision Engine"),
            ),
            FeatureDefinition(
                name="macd_histogram", group=self.group_name,
                formula="macd_line - macd_signal",
                meaning="Distance between the MACD line and its signal line.",
                interpretation="Sign shows which side of the crossover price is on; magnitude shows momentum strength; shrinking histogram often precedes a crossover.",
                priority="High", recommended_for=("Machine Learning", "Deep Learning", "Decision Engine"),
                when_to_use="Early-warning feature for upcoming MACD crossovers.",
            ),
        ]
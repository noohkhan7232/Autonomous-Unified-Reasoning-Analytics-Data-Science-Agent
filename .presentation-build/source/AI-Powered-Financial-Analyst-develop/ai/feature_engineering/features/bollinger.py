"""
Phase 3.E — Bollinger Band Features.

Bollinger Bands wrap a moving average in bands set N standard deviations
away, giving a dynamic (volatility-adjusted) range around price.
"""

import pandas as pd

from ai.feature_engineering.features.base import BaseFeatureGenerator, FeatureDefinition


class BollingerFeatureGenerator(BaseFeatureGenerator):
    group_name = "bollinger"

    def _compute(self, df: pd.DataFrame) -> pd.DataFrame:
        cfg = self.config
        w, k = cfg.bollinger_window, cfg.bollinger_num_std

        mid = df["close"].rolling(window=w, min_periods=w).mean()
        std = df["close"].rolling(window=w, min_periods=w).std()

        df["bollinger_middle"] = mid
        df["bollinger_upper"] = mid + k * std
        df["bollinger_lower"] = mid - k * std
        df["bollinger_bandwidth"] = (df["bollinger_upper"] - df["bollinger_lower"]) / mid
        band_range = df["bollinger_upper"] - df["bollinger_lower"]
        df["bollinger_percent_b"] = (df["close"] - df["bollinger_lower"]) / band_range.replace(0, pd.NA)
        return df

    def describe(self) -> list[FeatureDefinition]:
        cfg = self.config
        return [
            FeatureDefinition(
                name="bollinger_middle", group=self.group_name,
                formula=f"SMA(Close, {cfg.bollinger_window})",
                meaning="Center line of the Bollinger Bands.",
                interpretation="Same as sma_20 by default; the trend baseline the bands are drawn around.",
                priority="Medium", recommended_for=("Machine Learning", "Decision Engine"),
            ),
            FeatureDefinition(
                name="bollinger_upper", group=self.group_name,
                formula=f"middle + {cfg.bollinger_num_std}*std(Close, {cfg.bollinger_window})",
                meaning="Upper volatility band.",
                interpretation="Price reaching/exceeding this band suggests a statistically stretched move.",
                priority="High", recommended_for=("Machine Learning", "Decision Engine"),
            ),
            FeatureDefinition(
                name="bollinger_lower", group=self.group_name,
                formula=f"middle - {cfg.bollinger_num_std}*std(Close, {cfg.bollinger_window})",
                meaning="Lower volatility band.",
                interpretation="Price reaching/exceeding this band suggests a statistically stretched downside move.",
                priority="High", recommended_for=("Machine Learning", "Decision Engine"),
            ),
            FeatureDefinition(
                name="bollinger_bandwidth", group=self.group_name,
                formula="(upper - lower) / middle",
                meaning="Normalized band width — a direct volatility measure.",
                interpretation="A tight bandwidth ('squeeze') often precedes a sharp directional move.",
                priority="High", recommended_for=("Machine Learning", "Decision Engine"),
                when_to_use="Volatility-regime / breakout-anticipation feature.",
            ),
            FeatureDefinition(
                name="bollinger_percent_b", group=self.group_name,
                formula="(Close - lower) / (upper - lower)",
                meaning="Where price sits within the bands, normalized 0-1 (can exceed the range on breakouts).",
                interpretation="%B near 1 = near the upper band; near 0 = near the lower band; >1 or <0 = outside the bands.",
                priority="High", recommended_for=("Machine Learning", "Decision Engine"),
                limitations="Undefined (NaN) when the bands have zero width (flat price); guarded against divide-by-zero.",
            ),
        ]
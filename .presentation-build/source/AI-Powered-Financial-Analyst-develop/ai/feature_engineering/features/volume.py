"""
Phase 3.G — Volume Features.

Volume confirms (or contradicts) price moves — a price breakout on low
volume is far less trustworthy than the same breakout on high volume (see
also Phase 4's breakout confirmation features).
"""

import numpy as np
import pandas as pd

from ai.feature_engineering.features.base import BaseFeatureGenerator, FeatureDefinition


class VolumeFeatureGenerator(BaseFeatureGenerator):
    group_name = "volume"

    def _compute(self, df: pd.DataFrame) -> pd.DataFrame:
        cfg = self.config

        for w in cfg.volume_rolling_windows:
            df[f"volume_rolling_mean_{w}"] = df["volume"].rolling(window=w, min_periods=w).mean()
            df[f"volume_rolling_std_{w}"] = df["volume"].rolling(window=w, min_periods=w).std()

        df["volume_change"] = df["volume"].pct_change(periods=cfg.volume_change_period)

        base_window = cfg.volume_rolling_windows[0] if cfg.volume_rolling_windows else 20
        rolling_mean_col = f"volume_rolling_mean_{base_window}"
        if rolling_mean_col not in df.columns:
            df[rolling_mean_col] = df["volume"].rolling(window=base_window, min_periods=base_window).mean()
        df["volume_ratio"] = df["volume"] / df[rolling_mean_col].replace(0, pd.NA)

        typical_price = df["typical_price"] if "typical_price" in df.columns else (
            df["high"] + df["low"] + df["close"]
        ) / 3
        cum_vol = df["volume"].cumsum()
        cum_vol_price = (typical_price * df["volume"]).cumsum()
        df["vwap"] = cum_vol_price / cum_vol.replace(0, pd.NA)

        direction = np.sign(df["close"].diff().fillna(0))
        df["obv"] = (direction * df["volume"]).fillna(0).cumsum()

        return df

    def describe(self) -> list[FeatureDefinition]:
        cfg = self.config
        defs = []
        for w in cfg.volume_rolling_windows:
            defs.append(FeatureDefinition(
                name=f"volume_rolling_mean_{w}", group=self.group_name,
                formula=f"mean(Volume, last {w} days)",
                meaning=f"{w}-day average trading volume.",
                interpretation="Baseline 'normal' volume for the ticker; compare current volume against it.",
                priority="Medium", recommended_for=("Machine Learning", "Decision Engine"),
            ))
            defs.append(FeatureDefinition(
                name=f"volume_rolling_std_{w}", group=self.group_name,
                formula=f"std(Volume, last {w} days)",
                meaning=f"{w}-day volume volatility.",
                interpretation="High values indicate erratic/event-driven trading activity.",
                priority="Low", recommended_for=("Machine Learning",),
            ))
        defs.extend([
            FeatureDefinition(
                name="volume_change", group=self.group_name,
                formula=f"pct_change(Volume, {cfg.volume_change_period})",
                meaning="Day-over-day percentage change in volume.",
                interpretation="Spikes often coincide with news/earnings events.",
                priority="Medium", recommended_for=("Machine Learning", "Decision Engine"),
            ),
            FeatureDefinition(
                name="volume_ratio", group=self.group_name,
                formula=f"Volume(t) / volume_rolling_mean_{cfg.volume_rolling_windows[0] if cfg.volume_rolling_windows else 20}",
                meaning="Today's volume relative to its recent average.",
                interpretation="Ratio > 1.5-2x is commonly used as a 'high conviction' participation threshold (see breakout features).",
                priority="High", recommended_for=("Machine Learning", "Decision Engine"),
            ),
            FeatureDefinition(
                name="vwap", group=self.group_name,
                formula="cumsum(typical_price * Volume) / cumsum(Volume)",
                meaning="Volume-Weighted Average Price, cumulative from the start of the loaded series.",
                interpretation="Price above VWAP suggests buyers are in control on average; a common institutional execution benchmark.",
                priority="Medium", recommended_for=("Machine Learning", "Decision Engine"),
                limitations="Cumulative-from-series-start VWAP is most meaningful intraday; for daily bars, treat it as a long-run reference line rather than a session VWAP.",
                when_to_use="Reference level for whether current price is 'expensive' or 'cheap' relative to volume-weighted history.",
            ),
            FeatureDefinition(
                name="obv", group=self.group_name,
                formula="cumsum(sign(Close change) * Volume)",
                meaning="On-Balance Volume — running total that adds volume on up days and subtracts it on down days.",
                interpretation="Rising OBV alongside rising price confirms the trend; OBV diverging from price can flag weakening trends.",
                priority="Medium", recommended_for=("Machine Learning", "Decision Engine"),
                limitations="A cumulative indicator — its absolute level is arbitrary; only its slope/divergence from price is meaningful.",
            ),
        ])
        return defs
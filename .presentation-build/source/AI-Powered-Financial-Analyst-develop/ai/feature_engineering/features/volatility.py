"""
Phase 3.D — Volatility Features.

Volatility measures how much price moves, independent of direction — the
core input to risk scoring in the Decision Support Engine (Module 7) and to
scaling requirements for LSTM/GRU inputs (SRS FR-5.5).
"""

import numpy as np
import pandas as pd

from ai.feature_engineering.features.base import BaseFeatureGenerator, FeatureDefinition


def _true_range(df: pd.DataFrame) -> pd.Series:
    prev_close = df["close"].shift(1)
    ranges = pd.concat(
        [df["high"] - df["low"], (df["high"] - prev_close).abs(), (df["low"] - prev_close).abs()],
        axis=1,
    )
    return ranges.max(axis=1)


class VolatilityFeatureGenerator(BaseFeatureGenerator):
    group_name = "volatility"

    def _compute(self, df: pd.DataFrame) -> pd.DataFrame:
        cfg = self.config

        df["true_range"] = _true_range(df)
        df["atr"] = df["true_range"].ewm(alpha=1 / cfg.atr_period, min_periods=cfg.atr_period, adjust=False).mean()

        if "pct_return" in df.columns:
            returns = df["pct_return"]
        else:
            returns = df["close"].pct_change()

        for w in cfg.rolling_volatility_windows:
            df[f"rolling_volatility_{w}"] = returns.rolling(window=w, min_periods=w).std()

        hv_w = cfg.historical_volatility_window
        log_return = np.log(df["close"] / df["close"].shift(1))
        df["historical_volatility"] = log_return.rolling(window=hv_w, min_periods=hv_w).std() * np.sqrt(
            cfg.trading_days_per_year
        )

        for w in cfg.std_windows:
            df[f"std_{w}"] = df["close"].rolling(window=w, min_periods=w).std()
            df[f"variance_{w}"] = df["close"].rolling(window=w, min_periods=w).var()

        return df

    def describe(self) -> list[FeatureDefinition]:
        cfg = self.config
        defs = [
            FeatureDefinition(
                name="true_range", group=self.group_name,
                formula="max(High-Low, |High-PrevClose|, |Low-PrevClose|)",
                meaning="The full price range a bar covered, including any gap from the prior close.",
                interpretation="Larger values indicate a more volatile session, including overnight gaps.",
                priority="Medium", recommended_for=("Machine Learning", "Decision Engine"),
                when_to_use="Building block for ATR; on its own, a per-bar volatility snapshot.",
            ),
            FeatureDefinition(
                name="atr", group=self.group_name,
                formula=f"Wilder EMA(true_range, period={cfg.atr_period})",
                meaning="Average True Range — smoothed measure of typical daily trading range.",
                interpretation="Rising ATR = expanding volatility regime; commonly used to size stop-losses.",
                priority="High", recommended_for=("Machine Learning", "Decision Engine"),
                advantages="Captures gap risk (unlike a plain High-Low range); industry-standard.",
                limitations="Lagging (smoothed); doesn't indicate direction, only magnitude.",
                when_to_use="Risk/position-sizing features, volatility-regime detection.",
            ),
            FeatureDefinition(
                name="historical_volatility", group=self.group_name,
                formula=f"std(log_return, {cfg.historical_volatility_window}d) * sqrt({cfg.trading_days_per_year})",
                meaning="Annualized historical volatility from log returns.",
                interpretation="Directly comparable across tickers and to option-implied volatility.",
                priority="High", recommended_for=("Machine Learning", "Decision Engine", "Time Series"),
                when_to_use="Risk scoring, cross-ticker volatility comparison.",
            ),
        ]
        for w in cfg.rolling_volatility_windows:
            defs.append(FeatureDefinition(
                name=f"rolling_volatility_{w}", group=self.group_name,
                formula=f"std(pct_return, last {w} days)",
                meaning=f"{w}-day rolling standard deviation of daily percentage returns.",
                interpretation="Higher = choppier recent price action.",
                priority="Medium", recommended_for=("Machine Learning", "Deep Learning"),
            ))
        for w in cfg.std_windows:
            defs.append(FeatureDefinition(
                name=f"std_{w}", group=self.group_name,
                formula=f"std(Close, last {w} days)",
                meaning=f"{w}-day rolling standard deviation of raw closing price.",
                interpretation="Price-level dependent (not scale-invariant) — prefer rolling_volatility_* for cross-ticker comparisons.",
                priority="Low", recommended_for=("Machine Learning",),
                limitations="Scale depends on the ticker's price level.",
            ))
            defs.append(FeatureDefinition(
                name=f"variance_{w}", group=self.group_name,
                formula=f"var(Close, last {w} days)",
                meaning=f"{w}-day rolling variance of raw closing price (std_{w} squared).",
                interpretation="Same information as std, in squared units.",
                priority="Low", recommended_for=("Machine Learning",),
            ))
        return defs
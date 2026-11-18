"""
Phase 3.A — Price Features.

Simple derived price series computed directly from a single day's OHLCV bar
(no rolling window). These are the foundation nearly every downstream
feature (trend, momentum, volatility) is built on top of.
"""

import numpy as np
import pandas as pd

from ai.feature_engineering.features.base import BaseFeatureGenerator, FeatureDefinition


class PriceFeatureGenerator(BaseFeatureGenerator):
    group_name = "price"

    def _compute(self, df: pd.DataFrame) -> pd.DataFrame:
        df["daily_return"] = df["close"].diff()
        df["pct_return"] = df["close"].pct_change()
        df["log_return"] = np.log(df["close"] / df["close"].shift(1))
        df["price_diff"] = df["close"] - df["open"]
        df["open_close_diff"] = df["close"] - df["open"]
        df["high_low_diff"] = df["high"] - df["low"]
        df["typical_price"] = (df["high"] + df["low"] + df["close"]) / 3
        df["median_price"] = (df["high"] + df["low"]) / 2
        df["weighted_close"] = (df["high"] + df["low"] + 2 * df["close"]) / 4
        return df

    def describe(self) -> list[FeatureDefinition]:
        return [
            FeatureDefinition(
                name="daily_return", group=self.group_name,
                formula="Close(t) - Close(t-1)",
                meaning="Absolute day-over-day price change.",
                interpretation="Positive = price rose today; negative = price fell.",
                priority="Medium", recommended_for=("Machine Learning", "Time Series"),
                advantages="Simple, interpretable.",
                limitations="Not scale-invariant across tickers/time — use pct_return for comparisons.",
                when_to_use="Feature for models trained on a single ticker over a stable price range.",
            ),
            FeatureDefinition(
                name="pct_return", group=self.group_name,
                formula="(Close(t) - Close(t-1)) / Close(t-1)",
                meaning="Percentage day-over-day return.",
                interpretation="Scale-invariant version of daily_return; comparable across tickers/time.",
                priority="High", recommended_for=("Machine Learning", "Time Series", "Deep Learning"),
                advantages="Stationary-ish, comparable across price levels.",
                limitations="Can be noisy for low-priced/illiquid tickers.",
                when_to_use="Default target/feature basis for return-based modeling.",
            ),
            FeatureDefinition(
                name="log_return", group=self.group_name,
                formula="ln(Close(t) / Close(t-1))",
                meaning="Log return; approximately additive over time (log_return sums across days approximate the multi-day log return).",
                interpretation="Near-zero = flat; symmetric around 0 for up/down moves of similar magnitude.",
                priority="High", recommended_for=("Time Series", "Deep Learning"),
                advantages="Time-additive, closer to normally distributed than raw pct returns; preferred by ARIMA/DL.",
                limitations="Less intuitive to read directly than pct_return.",
                when_to_use="Time series models (ARIMA/SARIMA) and DL sequence inputs.",
            ),
            FeatureDefinition(
                name="price_diff", group=self.group_name,
                formula="Close - Open",
                meaning="Intraday price change.",
                interpretation="Positive = the session closed above where it opened (net buying pressure that day).",
                priority="Medium", recommended_for=("Machine Learning",),
            ),
            FeatureDefinition(
                name="open_close_diff", group=self.group_name,
                formula="Close - Open",
                meaning="Alias of price_diff, kept as a distinct named column per spec for readability in reports.",
                interpretation="Same as price_diff.",
                priority="Low", recommended_for=("Machine Learning",),
            ),
            FeatureDefinition(
                name="high_low_diff", group=self.group_name,
                formula="High - Low",
                meaning="Intraday trading range (absolute).",
                interpretation="Larger values indicate a more volatile session.",
                priority="Medium", recommended_for=("Machine Learning", "Decision Engine"),
                when_to_use="Cheap proxy for intraday volatility alongside ATR.",
            ),
            FeatureDefinition(
                name="typical_price", group=self.group_name,
                formula="(High + Low + Close) / 3",
                meaning="A single representative price for the session, weighting close, high and low equally.",
                interpretation="Commonly used as the input series for VWAP/CCI-style indicators.",
                priority="Medium", recommended_for=("Machine Learning", "Time Series"),
            ),
            FeatureDefinition(
                name="median_price", group=self.group_name,
                formula="(High + Low) / 2",
                meaning="Midpoint of the day's range, ignoring open/close.",
                interpretation="A smoother range-center reference than close alone.",
                priority="Low", recommended_for=("Machine Learning",),
            ),
            FeatureDefinition(
                name="weighted_close", group=self.group_name,
                formula="(High + Low + 2*Close) / 4",
                meaning="Typical price with double weight on the close.",
                interpretation="Emphasizes the closing price, which usually carries the most information.",
                priority="Low", recommended_for=("Machine Learning",),
            ),
        ]
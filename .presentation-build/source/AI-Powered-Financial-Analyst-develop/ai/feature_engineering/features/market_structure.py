"""
Phase 4.E + 4.G — Trend Structure and Market Structure Features.

Trend Structure (E) asks "is price trending, and how strongly" using a
rolling linear-regression slope of closing price, normalized by price level
and volatility so it's comparable across tickers.

Market Structure (G) asks "what has the *sequence of swing points* been
doing" — classic Dow Theory: an uptrend is a series of Higher Highs (HH) and
Higher Lows (HL); a downtrend is a series of Lower Highs (LH) and Lower Lows
(LL). This compares each confirmed swing point only to the *previous*
confirmed swing point of the same type (not bar-to-bar), which is what
distinguishes it from the simpler `higher_high`/`higher_low` bar-to-bar flags
in `price_action.py`. Must run after `PriceActionFeatureGenerator`.
"""

import numpy as np
import pandas as pd

from ai.feature_engineering.features.base import BaseFeatureGenerator, FeatureDefinition


def _rolling_slope(series: pd.Series, window: int) -> pd.Series:
    """OLS slope of `series` against a 0..window-1 time index, per rolling window."""
    x = np.arange(window, dtype=float)
    x_mean = x.mean()
    x_var = ((x - x_mean) ** 2).sum()

    def _slope(y: np.ndarray) -> float:
        return float(((y - y.mean()) * (x - x_mean)).sum() / x_var)

    return series.rolling(window=window, min_periods=window).apply(_slope, raw=True)


def _swing_sequence_flags(prices: pd.Series, mask: pd.Series) -> tuple[pd.Series, pd.Series]:
    """Compare each confirmed swing point (`prices` where `mask` is True)
    against the *previous* confirmed swing point of the same type.
    Returns (is_higher_than_prev_swing, is_lower_than_prev_swing), both
    forward-filled and reindexed to the full timeline.
    """
    swings = prices.where(mask.fillna(False))
    swing_only = swings.dropna()
    higher = (swing_only > swing_only.shift(1)).astype("boolean").reindex(prices.index)
    lower = (swing_only < swing_only.shift(1)).astype("boolean").reindex(prices.index)
    return higher.ffill().fillna(False).astype(bool), lower.ffill().fillna(False).astype(bool)


def _rolling_swing_count(mask: pd.Series, flag: pd.Series, n_swings: int) -> pd.Series:
    """Count how many of the last `n_swings` confirmed swings satisfy `flag`,
    reindexed back to the full timeline (ffilled between swing points).
    """
    confirmed = mask.fillna(False)
    flag_at_swings = flag[confirmed]
    count_at_swings = flag_at_swings.rolling(window=n_swings, min_periods=1).sum()
    return count_at_swings.reindex(mask.index).ffill().fillna(0)


class MarketStructureFeatureGenerator(BaseFeatureGenerator):
    group_name = "market_structure"
    requires_columns = ("close", "high", "low", "swing_high", "swing_low", "change_of_character")

    def _compute(self, df: pd.DataFrame) -> pd.DataFrame:
        cfg = self.config

        # --- Trend structure: rolling regression slope of closing price ---
        window = cfg.trend_structure_window
        slope = _rolling_slope(df["close"], window)
        vol = df["close"].rolling(window=window, min_periods=window).std().replace(0, np.nan)
        trend_score = (slope * window) / vol  # slope over the window, in std-dev units

        df["trend_score"] = trend_score
        threshold = 1.0
        df["trend_label"] = np.select(
            [trend_score > threshold, trend_score < -threshold],
            ["Uptrend", "Downtrend"],
            default="Sideways",
        )
        df.loc[trend_score.isna(), "trend_label"] = pd.NA
        df["is_uptrend"] = (trend_score > threshold).astype("boolean")
        df["is_downtrend"] = (trend_score < -threshold).astype("boolean")
        df["is_sideways"] = (trend_score.abs() <= threshold).astype("boolean")
        df.loc[trend_score.isna(), ["is_uptrend", "is_downtrend", "is_sideways"]] = pd.NA

        prev_label = pd.Series(df["trend_label"]).shift(1)
        df["trend_reversal_signal"] = (
            (df["trend_label"] != prev_label)
            & df["trend_label"].notna()
            & prev_label.notna()
            & (df["trend_label"] != "Sideways")
            & (prev_label != "Sideways")
        ) | df["change_of_character"].fillna(False)

        # --- Market structure: swing-to-swing HH/HL/LH/LL sequences ---
        swing_high_bool = df["swing_high"]
        swing_low_bool = df["swing_low"]

        hh_flag, lh_flag = _swing_sequence_flags(df["high"], swing_high_bool)
        hl_flag, ll_flag = _swing_sequence_flags(df["low"], swing_low_bool)

        n = cfg.market_structure_swing_count
        df["higher_high_count"] = _rolling_swing_count(swing_high_bool, hh_flag, n)
        df["lower_high_count"] = _rolling_swing_count(swing_high_bool, lh_flag, n)
        df["higher_low_count"] = _rolling_swing_count(swing_low_bool, hl_flag, n)
        df["lower_low_count"] = _rolling_swing_count(swing_low_bool, ll_flag, n)

        df["bullish_structure"] = hh_flag & hl_flag
        df["bearish_structure"] = lh_flag & ll_flag
        df["market_bias"] = np.select(
            [df["bullish_structure"], df["bearish_structure"]],
            ["Bullish", "Bearish"],
            default="Neutral",
        )
        df["market_structure"] = df["market_bias"]  # exposed under the spec's requested column name too

        return df

    def describe(self) -> list[FeatureDefinition]:
        cfg = self.config
        return [
            FeatureDefinition(
                name="trend_score", group=self.group_name,
                formula=f"OLS slope of Close over last {cfg.trend_structure_window} bars * window, in rolling-std units",
                meaning="Normalized trend strength and direction.",
                interpretation="Positive = uptrend, negative = downtrend; magnitude = conviction, comparable across tickers.",
                priority="High", recommended_for=("Machine Learning", "Decision Engine"),
                limitations="A regression slope treats the window as linear — doesn't capture curvature/acceleration.",
            ),
            FeatureDefinition(
                name="trend_label", group=self.group_name,
                formula="Uptrend if trend_score > 1, Downtrend if < -1, else Sideways",
                meaning="Categorical trend regime.",
                interpretation="Direct, human-readable trend classification.",
                priority="High", recommended_for=("Decision Engine", "Machine Learning"),
            ),
            FeatureDefinition(
                name="is_uptrend", group=self.group_name, formula="trend_label == 'Uptrend'",
                meaning="Boolean uptrend flag.", interpretation="One-hot-style flag for tree models.",
                priority="Medium", recommended_for=("Machine Learning",),
            ),
            FeatureDefinition(
                name="is_downtrend", group=self.group_name, formula="trend_label == 'Downtrend'",
                meaning="Boolean downtrend flag.", interpretation="One-hot-style flag for tree models.",
                priority="Medium", recommended_for=("Machine Learning",),
            ),
            FeatureDefinition(
                name="is_sideways", group=self.group_name, formula="trend_label == 'Sideways'",
                meaning="Boolean sideways/range-bound flag.", interpretation="One-hot-style flag for tree models.",
                priority="Medium", recommended_for=("Machine Learning",),
            ),
            FeatureDefinition(
                name="trend_reversal_signal", group=self.group_name,
                formula="trend_label flips between Uptrend and Downtrend, or change_of_character is True",
                meaning="A structural or regression-based trend change just occurred.",
                interpretation="Early-warning flag; combine with volume confirmation before acting on it.",
                priority="High", recommended_for=("Decision Engine", "Machine Learning"),
            ),
            FeatureDefinition(
                name="higher_high_count", group=self.group_name,
                formula=f"count of Higher Highs among the last {cfg.market_structure_swing_count} confirmed swing highs",
                meaning="How many of the recent swing highs were higher than the swing high before them.",
                interpretation="Higher counts support an uptrend classification (Dow Theory).",
                priority="Medium", recommended_for=("Machine Learning", "Decision Engine"),
            ),
            FeatureDefinition(
                name="lower_high_count", group=self.group_name,
                formula=f"count of Lower Highs among the last {cfg.market_structure_swing_count} confirmed swing highs",
                meaning="How many recent swing highs were lower than the one before them.",
                interpretation="Higher counts support a downtrend classification.",
                priority="Medium", recommended_for=("Machine Learning", "Decision Engine"),
            ),
            FeatureDefinition(
                name="higher_low_count", group=self.group_name,
                formula=f"count of Higher Lows among the last {cfg.market_structure_swing_count} confirmed swing lows",
                meaning="How many recent swing lows were higher than the one before them.",
                interpretation="Higher counts support an uptrend classification.",
                priority="Medium", recommended_for=("Machine Learning", "Decision Engine"),
            ),
            FeatureDefinition(
                name="lower_low_count", group=self.group_name,
                formula=f"count of Lower Lows among the last {cfg.market_structure_swing_count} confirmed swing lows",
                meaning="How many recent swing lows were lower than the one before them.",
                interpretation="Higher counts support a downtrend classification.",
                priority="Medium", recommended_for=("Machine Learning", "Decision Engine"),
            ),
            FeatureDefinition(
                name="bullish_structure", group=self.group_name,
                formula="most recent swing is both a Higher High and a Higher Low",
                meaning="Textbook Dow Theory uptrend confirmation.",
                interpretation="True = structure currently supports an uptrend read.",
                priority="High", recommended_for=("Decision Engine", "Machine Learning"),
            ),
            FeatureDefinition(
                name="bearish_structure", group=self.group_name,
                formula="most recent swing is both a Lower High and a Lower Low",
                meaning="Textbook Dow Theory downtrend confirmation.",
                interpretation="True = structure currently supports a downtrend read.",
                priority="High", recommended_for=("Decision Engine", "Machine Learning"),
            ),
            FeatureDefinition(
                name="market_bias", group=self.group_name,
                formula="Bullish if bullish_structure, Bearish if bearish_structure, else Neutral",
                meaning="Categorical summary of current market structure.",
                interpretation="Human-readable structure-based bias, independent of trend_label's regression approach.",
                priority="High", recommended_for=("Decision Engine",),
            ),
            FeatureDefinition(
                name="market_structure", group=self.group_name, formula="= market_bias",
                meaning="Alias exposed under the spec's requested column name.",
                interpretation="See market_bias.", priority="Medium", recommended_for=("Decision Engine",),
            ),
        ]
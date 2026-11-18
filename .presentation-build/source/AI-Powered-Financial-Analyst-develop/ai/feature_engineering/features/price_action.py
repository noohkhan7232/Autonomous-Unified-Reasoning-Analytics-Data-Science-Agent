"""
Phase 4.A — Price Action Features.

Candlestick-pattern and swing-point primitives read directly off the raw
OHLC bar shape. Swing highs/lows use a centered rolling window (looking
`swing_lookback` bars both before *and* after each bar), which makes them
excellent backtest/training features but means they "repaint": the swing
label for today's bar isn't final until `swing_lookback` future bars exist.
This is intentional for offline feature engineering (SRS scope: Sprint 2 is
model-input preparation, not live signal generation) and is called out
explicitly in `when_to_use` below.
"""

import numpy as np
import pandas as pd

from ai.feature_engineering.features.base import BaseFeatureGenerator, FeatureDefinition

_BODY_DOJI_RATIO = 0.1
_HAMMER_WICK_RATIO = 2.0
_MARUBOZU_WICK_RATIO = 0.05


class PriceActionFeatureGenerator(BaseFeatureGenerator):
    group_name = "price_action"

    def _compute(self, df: pd.DataFrame) -> pd.DataFrame:
        cfg = self.config
        o, h, l, c = df["open"], df["high"], df["low"], df["close"]
        body = (c - o).abs()
        candle_range = (h - l).replace(0, np.nan)
        upper_wick = h - c.where(c >= o, o)
        lower_wick = c.where(c <= o, o) - l

        # --- Structure: higher high / higher low / lower high / lower low (bar-to-bar) ---
        df["higher_high"] = h > h.shift(1)
        df["higher_low"] = l > l.shift(1)
        df["lower_high"] = h < h.shift(1)
        df["lower_low"] = l < l.shift(1)

        # --- Inside / outside bars ---
        df["inside_bar"] = (h < h.shift(1)) & (l > l.shift(1))
        df["outside_bar"] = (h > h.shift(1)) & (l < l.shift(1))

        # --- Candlestick patterns ---
        df["is_doji"] = body <= (_BODY_DOJI_RATIO * candle_range)
        prev_body_bearish = c.shift(1) < o.shift(1)
        curr_body_bullish = c > o
        df["is_bullish_engulfing"] = (
            prev_body_bearish & curr_body_bullish
            & (o <= c.shift(1)) & (c >= o.shift(1))
        )
        prev_body_bullish = c.shift(1) > o.shift(1)
        curr_body_bearish = c < o
        df["is_bearish_engulfing"] = (
            prev_body_bullish & curr_body_bearish
            & (o >= c.shift(1)) & (c <= o.shift(1))
        )
        df["is_pin_bar"] = (
            ((lower_wick >= _HAMMER_WICK_RATIO * body) & (upper_wick <= body))
            | ((upper_wick >= _HAMMER_WICK_RATIO * body) & (lower_wick <= body))
        )
        df["is_hammer"] = (lower_wick >= _HAMMER_WICK_RATIO * body) & (upper_wick <= body) & (body > 0)
        df["is_shooting_star"] = (upper_wick >= _HAMMER_WICK_RATIO * body) & (lower_wick <= body) & (body > 0)
        df["is_marubozu"] = (upper_wick <= _MARUBOZU_WICK_RATIO * candle_range) & (
            lower_wick <= _MARUBOZU_WICK_RATIO * candle_range
        )

        # --- Trend strength: fraction of the range captured by the body, signed by direction ---
        direction = np.sign(c - o)
        df["trend_strength"] = direction * (body / candle_range)

        # --- Swing highs/lows (centered fractal window) ---
        lb = cfg.swing_lookback
        roll_max = h.rolling(window=2 * lb + 1, center=True, min_periods=2 * lb + 1).max()
        roll_min = l.rolling(window=2 * lb + 1, center=True, min_periods=2 * lb + 1).min()
        df["swing_high"] = h.eq(roll_max).astype("boolean")
        df["swing_low"] = l.eq(roll_min).astype("boolean")
        df.loc[roll_max.isna(), "swing_high"] = pd.NA
        df.loc[roll_min.isna(), "swing_low"] = pd.NA

        # --- Break of Structure / Change of Character ---
        last_swing_high = h.where(df["swing_high"].fillna(False)).ffill()
        last_swing_low = l.where(df["swing_low"].fillna(False)).ffill()
        df["break_of_structure_up"] = c > last_swing_high.shift(1)
        df["break_of_structure_down"] = c < last_swing_low.shift(1)

        bos_up_seen = df["break_of_structure_up"].astype("boolean")
        bos_down_seen = df["break_of_structure_down"].astype("boolean")
        last_bull_bos = bos_up_seen.where(bos_up_seen.fillna(False)).ffill().fillna(False).astype(bool)
        last_bear_bos = bos_down_seen.where(bos_down_seen.fillna(False)).ffill().fillna(False).astype(bool)
        # CHOCH: a break of structure in the opposite direction of the most recent BOS trend.
        df["change_of_character"] = (bos_down_seen & last_bull_bos) | (bos_up_seen & last_bear_bos)

        # --- Consolidated categorical label (first matching pattern wins, priority order below) ---
        pattern_priority = [
            ("Bullish Engulfing", df["is_bullish_engulfing"]),
            ("Bearish Engulfing", df["is_bearish_engulfing"]),
            ("Hammer", df["is_hammer"]),
            ("Shooting Star", df["is_shooting_star"]),
            ("Doji", df["is_doji"]),
            ("Marubozu", df["is_marubozu"]),
            ("Pin Bar", df["is_pin_bar"]),
            ("Inside Bar", df["inside_bar"]),
            ("Outside Bar", df["outside_bar"]),
        ]
        label = pd.Series("None", index=df.index)
        for name, flag in reversed(pattern_priority):
            label = label.where(~flag.fillna(False), name)
        df["price_action_label"] = label

        return df

    def describe(self) -> list[FeatureDefinition]:
        candle = dict(priority="Medium", recommended_for=("Machine Learning", "Decision Engine"))
        return [
            FeatureDefinition(name="higher_high", group=self.group_name, formula="High(t) > High(t-1)",
                               meaning="Today's high exceeded yesterday's high.", interpretation="Building block of uptrend structure.", **candle),
            FeatureDefinition(name="higher_low", group=self.group_name, formula="Low(t) > Low(t-1)",
                               meaning="Today's low exceeded yesterday's low.", interpretation="Building block of uptrend structure.", **candle),
            FeatureDefinition(name="lower_high", group=self.group_name, formula="High(t) < High(t-1)",
                               meaning="Today's high is below yesterday's high.", interpretation="Building block of downtrend structure.", **candle),
            FeatureDefinition(name="lower_low", group=self.group_name, formula="Low(t) < Low(t-1)",
                               meaning="Today's low is below yesterday's low.", interpretation="Building block of downtrend structure.", **candle),
            FeatureDefinition(name="inside_bar", group=self.group_name, formula="High(t)<High(t-1) and Low(t)>Low(t-1)",
                               meaning="Today's range is fully contained within yesterday's range.", interpretation="Often signals consolidation/indecision before a breakout.", **candle),
            FeatureDefinition(name="outside_bar", group=self.group_name, formula="High(t)>High(t-1) and Low(t)<Low(t-1)",
                               meaning="Today's range fully engulfs yesterday's range.", interpretation="Signals a volatility expansion / potential reversal bar.", **candle),
            FeatureDefinition(name="is_doji", group=self.group_name, formula="|Close-Open| <= 10% of (High-Low)",
                               meaning="Open and close are nearly equal.", interpretation="Indecision; often precedes a reversal, especially after a strong trend.", **candle),
            FeatureDefinition(name="is_bullish_engulfing", group=self.group_name,
                               formula="Bearish candle followed by a bullish candle whose body engulfs it",
                               meaning="Two-candle bullish reversal pattern.", interpretation="Stronger when it occurs after a downtrend / at support.",
                               priority="High", recommended_for=("Machine Learning", "Decision Engine")),
            FeatureDefinition(name="is_bearish_engulfing", group=self.group_name,
                               formula="Bullish candle followed by a bearish candle whose body engulfs it",
                               meaning="Two-candle bearish reversal pattern.", interpretation="Stronger when it occurs after an uptrend / at resistance.",
                               priority="High", recommended_for=("Machine Learning", "Decision Engine")),
            FeatureDefinition(name="is_pin_bar", group=self.group_name,
                               formula="One wick >= 2x body and the opposite wick <= body",
                               meaning="Long single-sided wick, small body/opposite wick.", interpretation="Rejection of price at the wick's extreme; potential reversal.", **candle),
            FeatureDefinition(name="is_hammer", group=self.group_name,
                               formula="Long lower wick >= 2x body, small/no upper wick",
                               meaning="Bullish reversal candle after a decline.", interpretation="Buyers rejected lower prices within the session.",
                               priority="High", recommended_for=("Machine Learning", "Decision Engine")),
            FeatureDefinition(name="is_shooting_star", group=self.group_name,
                               formula="Long upper wick >= 2x body, small/no lower wick",
                               meaning="Bearish reversal candle after an advance.", interpretation="Sellers rejected higher prices within the session.",
                               priority="High", recommended_for=("Machine Learning", "Decision Engine")),
            FeatureDefinition(name="is_marubozu", group=self.group_name,
                               formula="Wicks <= 5% of the candle's range on both ends",
                               meaning="Full-bodied candle with virtually no wicks.", interpretation="Strong one-sided conviction for the full session.", **candle),
            FeatureDefinition(name="trend_strength", group=self.group_name,
                               formula="sign(Close-Open) * body / (High-Low)",
                               meaning="Signed fraction of the day's range captured by the candle body.",
                               interpretation="Near +1/-1 = strong directional conviction; near 0 = indecisive session.",
                               priority="Medium", recommended_for=("Machine Learning",)),
            FeatureDefinition(name="swing_high", group=self.group_name,
                               formula=f"High(t) is the max High within +/-{self.config.swing_lookback} bars",
                               meaning="Local price peak (fractal high).",
                               interpretation="Used as pivot points for support/resistance and structure features.",
                               priority="High", recommended_for=("Machine Learning", "Decision Engine"),
                               limitations="Repaints: only confirmed once the trailing lookback window of future bars exists.",
                               when_to_use="Offline feature engineering / backtesting, not real-time signal generation without an added lag."),
            FeatureDefinition(name="swing_low", group=self.group_name,
                               formula=f"Low(t) is the min Low within +/-{self.config.swing_lookback} bars",
                               meaning="Local price trough (fractal low).",
                               interpretation="Used as pivot points for support/resistance and structure features.",
                               priority="High", recommended_for=("Machine Learning", "Decision Engine"),
                               limitations="Repaints (see swing_high).",
                               when_to_use="Offline feature engineering / backtesting."),
            FeatureDefinition(name="break_of_structure_up", group=self.group_name,
                               formula="Close(t) > most recent confirmed swing_high",
                               meaning="Price broke above the last significant swing high.",
                               interpretation="Continuation signal in an uptrend.",
                               priority="High", recommended_for=("Machine Learning", "Decision Engine")),
            FeatureDefinition(name="break_of_structure_down", group=self.group_name,
                               formula="Close(t) < most recent confirmed swing_low",
                               meaning="Price broke below the last significant swing low.",
                               interpretation="Continuation signal in a downtrend.",
                               priority="High", recommended_for=("Machine Learning", "Decision Engine")),
            FeatureDefinition(name="change_of_character", group=self.group_name,
                               formula="A break-of-structure opposite to the prevailing BOS direction",
                               meaning="First structural break against the prevailing trend.",
                               interpretation="Early warning of a potential trend reversal.",
                               priority="High", recommended_for=("Decision Engine", "Machine Learning")),
            FeatureDefinition(name="price_action_label", group=self.group_name,
                               formula="first matching candlestick pattern in priority order, else 'None'",
                               meaning="Single human-readable label summarizing today's candlestick pattern.",
                               interpretation="Convenience categorical for reports/dashboards; the underlying boolean columns are more precise for modeling.",
                               priority="Medium", recommended_for=("Decision Engine",)),
        ]
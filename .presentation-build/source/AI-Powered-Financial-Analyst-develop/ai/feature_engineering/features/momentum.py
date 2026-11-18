"""
Phase 3.C — Momentum Features.

Momentum indicators measure the speed/strength of recent price moves,
independent of trend direction — useful for spotting overbought/oversold
conditions and confirming (or diverging from) the trend features above.
"""

import pandas as pd

from ai.feature_engineering.features.base import BaseFeatureGenerator, FeatureDefinition


def _rsi(close: pd.Series, period: int) -> pd.Series:
    """Wilder's RSI via an exponential (Wilder) moving average of gains/losses."""
    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()
    rs = avg_gain / avg_loss.replace(0, pd.NA)
    rsi = 100 - (100 / (1 + rs))
    rsi = rsi.where(avg_loss != 0, 100.0)  # no losses in window -> RSI saturates at 100
    return rsi


class MomentumFeatureGenerator(BaseFeatureGenerator):
    group_name = "momentum"

    def _compute(self, df: pd.DataFrame) -> pd.DataFrame:
        cfg = self.config
        df["rsi"] = _rsi(df["close"], cfg.rsi_period)
        df["roc"] = (df["close"] - df["close"].shift(cfg.roc_period)) / df["close"].shift(cfg.roc_period) * 100
        df["momentum"] = df["close"] - df["close"].shift(cfg.momentum_period)
        df["price_momentum"] = df["close"].pct_change(periods=cfg.momentum_period)
        df["volume_momentum"] = df["volume"] - df["volume"].shift(cfg.volume_momentum_period)
        return df

    def describe(self) -> list[FeatureDefinition]:
        cfg = self.config
        return [
            FeatureDefinition(
                name="rsi", group=self.group_name,
                formula=f"100 - 100/(1 + RS), RS = Wilder-smoothed avg gain / avg loss over {cfg.rsi_period} days",
                meaning="Relative Strength Index — bounded 0-100 momentum oscillator.",
                interpretation="Traditionally >70 = overbought, <30 = oversold; divergence from price can signal reversals.",
                priority="High", recommended_for=("Machine Learning", "Decision Engine"),
                advantages="Bounded scale makes it comparable across tickers/time; well-studied.",
                limitations="Can stay 'overbought'/'oversold' for extended periods in strong trends (false signals).",
                when_to_use="Overbought/oversold screening; confirming momentum alongside MACD.",
            ),
            FeatureDefinition(
                name="roc", group=self.group_name,
                formula=f"(Close(t) - Close(t-{cfg.roc_period})) / Close(t-{cfg.roc_period}) * 100",
                meaning="Rate of Change — percentage price change over the lookback period.",
                interpretation="Positive and rising = accelerating upward momentum.",
                priority="Medium", recommended_for=("Machine Learning", "Time Series"),
                when_to_use="Momentum feature comparable in scale across tickers.",
            ),
            FeatureDefinition(
                name="momentum", group=self.group_name,
                formula=f"Close(t) - Close(t-{cfg.momentum_period})",
                meaning="Absolute price momentum over the lookback period.",
                interpretation="Magnitude and direction of the recent price move.",
                priority="Medium", recommended_for=("Machine Learning",),
                limitations="Not scale-invariant across tickers — prefer roc/price_momentum for cross-ticker models.",
            ),
            FeatureDefinition(
                name="price_momentum", group=self.group_name,
                formula=f"pct_change(Close, {cfg.momentum_period})",
                meaning="Percentage version of `momentum`.",
                interpretation="Scale-invariant momentum measure.",
                priority="Medium", recommended_for=("Machine Learning", "Deep Learning"),
            ),
            FeatureDefinition(
                name="volume_momentum", group=self.group_name,
                formula=f"Volume(t) - Volume(t-{cfg.volume_momentum_period})",
                meaning="Change in trading volume over the lookback period.",
                interpretation="Rising volume momentum alongside price momentum supports trend conviction.",
                priority="Medium", recommended_for=("Machine Learning", "Decision Engine"),
                when_to_use="Confirming price moves with participation (volume) — see also breakout features.",
            ),
        ]
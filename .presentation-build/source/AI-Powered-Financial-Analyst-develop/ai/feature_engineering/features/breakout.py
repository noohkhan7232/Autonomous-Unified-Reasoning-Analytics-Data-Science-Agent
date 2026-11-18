"""
Phase 4.F — Breakout Features.

Detects price pushing through a static support/resistance level and checks
whether volume confirms it. Must run after `SupportResistanceFeatureGenerator`
(needs `static_support`/`static_resistance`) and `VolumeFeatureGenerator`
(needs `volume_ratio`).
"""

import pandas as pd

from ai.feature_engineering.features.base import BaseFeatureGenerator, FeatureDefinition


class BreakoutFeatureGenerator(BaseFeatureGenerator):
    group_name = "breakout"
    requires_columns = (
        "close", "high", "low", "static_support", "static_resistance", "volume_ratio",
        "nearest_demand_zone", "nearest_supply_zone",
    )

    def _compute(self, df: pd.DataFrame) -> pd.DataFrame:
        cfg = self.config
        close = df["close"]
        prev_resistance = df["static_resistance"].shift(1)
        prev_support = df["static_support"].shift(1)

        breakout_up = close > prev_resistance
        breakout_down = close < prev_support
        df["breakout_above_resistance"] = breakout_up
        df["breakdown_below_support"] = breakout_down

        volume_confirmed = df["volume_ratio"] >= cfg.breakout_confirmation_volume_multiplier
        df["volume_confirmation"] = volume_confirmed

        # Fake breakout: price broke the level but closed back inside it within the
        # next bar (checked via next-bar close, so this label finalizes one bar late).
        next_close = close.shift(-1)
        fake_up = breakout_up & (next_close <= prev_resistance)
        fake_down = breakout_down & (next_close >= prev_support)
        df["fake_breakout"] = fake_up | fake_down

        df["breakout_label"] = "None"
        df.loc[breakout_up & volume_confirmed, "breakout_label"] = "Confirmed Breakout Up"
        df.loc[breakout_up & ~volume_confirmed, "breakout_label"] = "Unconfirmed Breakout Up"
        df.loc[breakout_down & volume_confirmed, "breakout_label"] = "Confirmed Breakdown"
        df.loc[breakout_down & ~volume_confirmed, "breakout_label"] = "Unconfirmed Breakdown"
        df.loc[df["fake_breakout"].fillna(False), "breakout_label"] = "Fake Breakout"

        # --- Reaction-at-level convenience flags (ties S/R + zones together) ---
        tol = cfg.support_resistance_tolerance_pct
        near_support = (close - df["static_support"]).abs() / close <= tol
        near_resistance = (df["static_resistance"] - close).abs() / close <= tol
        bullish_bar = close > df["open"] if "open" in df.columns else pd.Series(True, index=df.index)
        bearish_bar = close < df["open"] if "open" in df.columns else pd.Series(False, index=df.index)

        df["support_bounce"] = near_support & bullish_bar & ~breakout_down
        df["resistance_rejection"] = near_resistance & bearish_bar & ~breakout_up

        near_demand = (df["low"] <= df["nearest_demand_zone"] * (1 + tol)) & df["nearest_demand_zone"].notna()
        near_supply = (df["high"] >= df["nearest_supply_zone"] * (1 - tol)) & df["nearest_supply_zone"].notna()
        df["demand_zone_bounce"] = near_demand & bullish_bar
        df["supply_zone_rejection"] = near_supply & bearish_bar

        return df

    def describe(self) -> list[FeatureDefinition]:
        cfg = self.config
        return [
            FeatureDefinition(
                name="breakout_above_resistance", group=self.group_name,
                formula="Close(t) > static_resistance(t-1)",
                meaning="Price closed above the prior rolling resistance level.",
                interpretation="Potential start of a new upward move.",
                priority="High", recommended_for=("Decision Engine", "Machine Learning"),
                limitations="A single close above resistance is a weak signal alone — check volume_confirmation.",
            ),
            FeatureDefinition(
                name="breakdown_below_support", group=self.group_name,
                formula="Close(t) < static_support(t-1)",
                meaning="Price closed below the prior rolling support level.",
                interpretation="Potential start of a new downward move.",
                priority="High", recommended_for=("Decision Engine", "Machine Learning"),
            ),
            FeatureDefinition(
                name="volume_confirmation", group=self.group_name,
                formula=f"volume_ratio >= {cfg.breakout_confirmation_volume_multiplier}",
                meaning="Whether today's volume was elevated enough to trust a breakout.",
                interpretation="True = the move had above-average participation.",
                priority="High", recommended_for=("Decision Engine", "Machine Learning"),
            ),
            FeatureDefinition(
                name="fake_breakout", group=self.group_name,
                formula="breakout occurred but the very next close fell back inside the level",
                meaning="A breakout that failed to hold.",
                interpretation="Common trap for naive breakout strategies; finalizes one bar after the breakout bar.",
                priority="High", recommended_for=("Decision Engine", "Machine Learning"),
                limitations="Uses the next bar's close, so this label is only known one day later — not usable as a same-day live feature.",
            ),
            FeatureDefinition(
                name="breakout_label", group=self.group_name,
                formula="categorical combination of breakout direction + volume_confirmation + fake_breakout",
                meaning="Human-readable summary of the day's breakout status.",
                interpretation="One of: None, Confirmed/Unconfirmed Breakout Up, Confirmed/Unconfirmed Breakdown, Fake Breakout.",
                priority="Medium", recommended_for=("Decision Engine",),
            ),
            FeatureDefinition(
                name="support_bounce", group=self.group_name,
                formula=f"price within {cfg.support_resistance_tolerance_pct:.1%} of static_support and closed bullish, without breaking down",
                meaning="Price tested support and reacted upward.",
                interpretation="Supports a 'buy the dip' read at a known level.",
                priority="Medium", recommended_for=("Decision Engine", "Machine Learning"),
            ),
            FeatureDefinition(
                name="resistance_rejection", group=self.group_name,
                formula=f"price within {cfg.support_resistance_tolerance_pct:.1%} of static_resistance and closed bearish, without breaking out",
                meaning="Price tested resistance and reacted downward.",
                interpretation="Supports a 'fade the rally' read at a known level.",
                priority="Medium", recommended_for=("Decision Engine", "Machine Learning"),
            ),
            FeatureDefinition(
                name="demand_zone_bounce", group=self.group_name,
                formula="Low dipped into the nearest demand zone and the bar closed bullish",
                meaning="Price reacted upward from a demand zone.",
                interpretation="Zone-based analogue of support_bounce.",
                priority="Medium", recommended_for=("Decision Engine", "Machine Learning"),
            ),
            FeatureDefinition(
                name="supply_zone_rejection", group=self.group_name,
                formula="High pushed into the nearest supply zone and the bar closed bearish",
                meaning="Price reacted downward from a supply zone.",
                interpretation="Zone-based analogue of resistance_rejection.",
                priority="Medium", recommended_for=("Decision Engine", "Machine Learning"),
            ),
        ]
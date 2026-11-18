"""
Phase 4.B + 4.C — Support & Resistance and Supply & Demand Zone Features.

Both concepts are "where has price previously reversed, and is it likely to
react there again" — S/R uses confirmed swing points as the reaction levels,
Supply/Demand additionally requires a *strong* subsequent move away from a
tight base, so the two are implemented together and share the same
swing-point primitives from `price_action.py` (this generator must run after
`PriceActionFeatureGenerator` in the pipeline).

Zone detection here is a documented heuristic, not a proprietary formula —
"supply/demand zone" has no single universally-agreed mathematical
definition the way RSI or MACD does. The rule implemented is:

    A swing low (resp. high) is the origin of a fresh Demand (resp. Supply)
    zone if, within the following `supply_demand_lookback` bars, price moves
    away from it by more than one rolling-volatility unit. The zone's price
    band is the origin bar's [low, high]; the zone remains "fresh" until
    price closes back through it (a "retest") after formation.
"""

import numpy as np
import pandas as pd

from ai.feature_engineering.features.base import BaseFeatureGenerator, FeatureDefinition


class SupportResistanceFeatureGenerator(BaseFeatureGenerator):
    group_name = "support_resistance"
    requires_columns = ("date", "open", "high", "low", "close", "volume", "swing_high", "swing_low")

    def _compute(self, df: pd.DataFrame) -> pd.DataFrame:
        cfg = self.config
        close, high, low = df["close"], df["high"], df["low"]
        w = cfg.support_resistance_window

        # --- Static support/resistance: simple rolling extremes ---
        df["static_support"] = low.rolling(window=w, min_periods=w).min()
        df["static_resistance"] = high.rolling(window=w, min_periods=w).max()

        # --- Dynamic support/resistance: last confirmed swing low/high ---
        swing_high_bool = df["swing_high"].fillna(False).astype(bool)
        swing_low_bool = df["swing_low"].fillna(False).astype(bool)
        dynamic_resistance = high.where(swing_high_bool).ffill()
        dynamic_support = low.where(swing_low_bool).ffill()
        df["dynamic_resistance"] = dynamic_resistance
        df["dynamic_support"] = dynamic_support

        # --- Nearest support/resistance + distances ---
        df["nearest_support"] = dynamic_support
        df["nearest_resistance"] = dynamic_resistance
        df["support_distance"] = (close - dynamic_support) / close
        df["resistance_distance"] = (dynamic_resistance - close) / close

        # --- Swing zone (current trading range implied by the last two swings) ---
        df["swing_zone_width"] = (dynamic_resistance - dynamic_support) / close

        # --- Supply & Demand zones ---
        tol = cfg.support_resistance_tolerance_pct
        lookback = cfg.supply_demand_lookback
        vol_ref = close.pct_change().rolling(window=w, min_periods=w).std().fillna(0)

        # Forward move measured FROM the swing point over the next `lookback` bars.
        fwd_high = high.shift(-1).rolling(window=lookback, min_periods=1).max().shift(-(lookback - 1))
        fwd_low = low.shift(-1).rolling(window=lookback, min_periods=1).min().shift(-(lookback - 1))
        fwd_up_move = (fwd_high - close) / close
        fwd_down_move = (close - fwd_low) / close

        demand_zone = swing_low_bool & (fwd_up_move > (2 * vol_ref).clip(lower=tol))
        supply_zone = swing_high_bool & (fwd_down_move > (2 * vol_ref).clip(lower=tol))
        df["demand_zone"] = demand_zone
        df["supply_zone"] = supply_zone

        df["demand_zone_strength"] = fwd_up_move.where(demand_zone)
        df["supply_zone_strength"] = fwd_down_move.where(supply_zone)
        df["zone_width"] = (high - low).where(demand_zone | supply_zone)

        # --- Zone age: bars elapsed since the most recent zone of each type ---
        demand_idx = pd.Series(np.where(demand_zone, np.arange(len(df)), np.nan), index=df.index).ffill()
        supply_idx = pd.Series(np.where(supply_zone, np.arange(len(df)), np.nan), index=df.index).ffill()
        bar_idx = pd.Series(np.arange(len(df)), index=df.index)
        df["demand_zone_age"] = (bar_idx - demand_idx)
        df["supply_zone_age"] = (bar_idx - supply_idx)
        df["fresh_demand_zone"] = df["demand_zone_age"] <= lookback
        df["fresh_supply_zone"] = df["supply_zone_age"] <= lookback

        # --- Nearest zone reference levels (last formed zone's price band) ---
        nearest_demand_low = low.where(demand_zone).ffill()
        nearest_supply_high = high.where(supply_zone).ffill()
        df["nearest_demand_zone"] = nearest_demand_low
        df["nearest_supply_zone"] = nearest_supply_high

        # --- Retest detection: price re-enters a previously formed zone band ---
        demand_high_at_origin = high.where(demand_zone).ffill()
        supply_low_at_origin = low.where(supply_zone).ffill()
        df["demand_zone_retested"] = (low <= demand_high_at_origin) & (low >= nearest_demand_low) & (~demand_zone)
        df["supply_zone_retested"] = (high >= supply_low_at_origin) & (high <= nearest_supply_high) & (~supply_zone)

        return df

    def describe(self) -> list[FeatureDefinition]:
        cfg = self.config
        sr = dict(priority="High", recommended_for=("Machine Learning", "Decision Engine"))
        sd = dict(priority="Medium", recommended_for=("Machine Learning", "Decision Engine"))
        return [
            FeatureDefinition(name="static_support", group=self.group_name,
                               formula=f"min(Low, last {cfg.support_resistance_window} days)",
                               meaning="Simple rolling floor of recent price action.",
                               interpretation="A break below this level suggests the recent trading range has failed.", **sr),
            FeatureDefinition(name="static_resistance", group=self.group_name,
                               formula=f"max(High, last {cfg.support_resistance_window} days)",
                               meaning="Simple rolling ceiling of recent price action.",
                               interpretation="A break above this level suggests the recent trading range has failed to the upside.", **sr),
            FeatureDefinition(name="dynamic_support", group=self.group_name,
                               formula="Price of the most recent confirmed swing_low",
                               meaning="Structure-based (fractal) support level.",
                               interpretation="More reactive than static_support to the most recent meaningful pivot.", **sr),
            FeatureDefinition(name="dynamic_resistance", group=self.group_name,
                               formula="Price of the most recent confirmed swing_high",
                               meaning="Structure-based (fractal) resistance level.",
                               interpretation="More reactive than static_resistance to the most recent meaningful pivot.", **sr),
            FeatureDefinition(name="nearest_support", group=self.group_name, formula="= dynamic_support",
                               meaning="Alias exposed under the spec's requested column name.",
                               interpretation="See dynamic_support.", **sr),
            FeatureDefinition(name="nearest_resistance", group=self.group_name, formula="= dynamic_resistance",
                               meaning="Alias exposed under the spec's requested column name.",
                               interpretation="See dynamic_resistance.", **sr),
            FeatureDefinition(name="support_distance", group=self.group_name,
                               formula="(Close - nearest_support) / Close",
                               meaning="Normalized distance from price to the nearest support.",
                               interpretation="Small/near-zero = price is testing support right now (elevated bounce-or-break risk).", **sr),
            FeatureDefinition(name="resistance_distance", group=self.group_name,
                               formula="(nearest_resistance - Close) / Close",
                               meaning="Normalized distance from price to the nearest resistance.",
                               interpretation="Small/near-zero = price is testing resistance right now.", **sr),
            FeatureDefinition(name="swing_zone_width", group=self.group_name,
                               formula="(dynamic_resistance - dynamic_support) / Close",
                               meaning="Width of the current support-resistance trading range, normalized by price.",
                               interpretation="Narrow = tight range (potential breakout setup); wide = range-bound with room to move.",
                               priority="Medium", recommended_for=("Machine Learning", "Decision Engine")),
            FeatureDefinition(name="demand_zone", group=self.group_name,
                               formula="swing_low followed by a strong up-move within the lookback window (see module docstring)",
                               meaning="Origin bar of a fresh institutional-style demand (buy-side) zone.",
                               interpretation="Price returning to this zone is expected to find buying interest.",
                               limitations="Heuristic, not a formally standardized indicator; forward-looking by construction (repaints).", **sd),
            FeatureDefinition(name="supply_zone", group=self.group_name,
                               formula="swing_high followed by a strong down-move within the lookback window",
                               meaning="Origin bar of a fresh supply (sell-side) zone.",
                               interpretation="Price returning to this zone is expected to find selling interest.",
                               limitations="Heuristic; repaints (see demand_zone).", **sd),
            FeatureDefinition(name="demand_zone_strength", group=self.group_name,
                               formula="Forward % move away from the demand zone origin",
                               meaning="How strong the reaction away from the zone was.",
                               interpretation="Larger = more significant zone.", **sd),
            FeatureDefinition(name="supply_zone_strength", group=self.group_name,
                               formula="Forward % move away from the supply zone origin",
                               meaning="How strong the reaction away from the zone was.",
                               interpretation="Larger = more significant zone.", **sd),
            FeatureDefinition(name="zone_width", group=self.group_name, formula="High - Low of the zone origin bar",
                               meaning="Price band width of the zone.",
                               interpretation="Narrower zones are considered more precise reaction levels.", **sd),
            FeatureDefinition(name="demand_zone_age", group=self.group_name, formula="bars since the last demand_zone bar",
                               meaning="Recency of the most recent demand zone.",
                               interpretation="Smaller = more recently formed.", priority="Low", recommended_for=("Machine Learning",)),
            FeatureDefinition(name="supply_zone_age", group=self.group_name, formula="bars since the last supply_zone bar",
                               meaning="Recency of the most recent supply zone.",
                               interpretation="Smaller = more recently formed.", priority="Low", recommended_for=("Machine Learning",)),
            FeatureDefinition(name="fresh_demand_zone", group=self.group_name,
                               formula=f"demand_zone_age <= {cfg.supply_demand_lookback}",
                               meaning="Whether the nearest demand zone is still considered 'fresh' (untested).",
                               interpretation="Fresh zones are traditionally considered more reliable than repeatedly-tested ones.", **sd),
            FeatureDefinition(name="fresh_supply_zone", group=self.group_name,
                               formula=f"supply_zone_age <= {cfg.supply_demand_lookback}",
                               meaning="Whether the nearest supply zone is still considered 'fresh' (untested).",
                               interpretation="See fresh_demand_zone.", **sd),
            FeatureDefinition(name="nearest_demand_zone", group=self.group_name,
                               formula="Low of the most recent demand_zone origin bar",
                               meaning="Price level of the nearest demand zone floor.",
                               interpretation="Reference level for support-style reactions.", **sd),
            FeatureDefinition(name="nearest_supply_zone", group=self.group_name,
                               formula="High of the most recent supply_zone origin bar",
                               meaning="Price level of the nearest supply zone ceiling.",
                               interpretation="Reference level for resistance-style reactions.", **sd),
            FeatureDefinition(name="demand_zone_retested", group=self.group_name,
                               formula="price re-enters the demand zone band after formation",
                               meaning="Whether today's bar dipped back into an existing demand zone.",
                               interpretation="A retest that holds strengthens the zone; a retest that fails (closes through) invalidates it.", **sd),
            FeatureDefinition(name="supply_zone_retested", group=self.group_name,
                               formula="price re-enters the supply zone band after formation",
                               meaning="Whether today's bar pushed back into an existing supply zone.",
                               interpretation="See demand_zone_retested.", **sd),
        ]
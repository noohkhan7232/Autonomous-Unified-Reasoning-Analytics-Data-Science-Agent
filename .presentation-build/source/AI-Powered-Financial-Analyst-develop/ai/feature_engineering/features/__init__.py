"""
Feature generator registry for `ai/feature_engineering/features/`.

A Factory (`build_generators`) that maps each `group_name` to its
`BaseFeatureGenerator` subclass. `ai.feature_engineering.pipeline.Pipeline`
uses this instead of importing every generator class itself, so adding a new
feature group later means registering it here — nowhere else needs to
change.

Registration order in `_GENERATOR_REGISTRY` reflects real data dependencies
between groups (e.g. `fibonacci` reads columns `support_resistance`
produces) and matches `FeatureEngineeringConfig.enabled_feature_groups`'
default order. `build_generators` always returns generators in that
dependency-respecting order, regardless of the order group names are listed
in config.
"""

from ai.feature_engineering.config import FeatureEngineeringConfig
from ai.feature_engineering.features.base import BaseFeatureGenerator, FeatureDefinition
from ai.feature_engineering.features.bollinger import BollingerFeatureGenerator
from ai.feature_engineering.features.breakout import BreakoutFeatureGenerator
from ai.feature_engineering.features.date import DateFeatureGenerator
from ai.feature_engineering.features.fibonacci import FibonacciFeatureGenerator
from ai.feature_engineering.features.lag import LagFeatureGenerator
from ai.feature_engineering.features.macd import MACDFeatureGenerator
from ai.feature_engineering.features.market_structure import MarketStructureFeatureGenerator
from ai.feature_engineering.features.momentum import MomentumFeatureGenerator
from ai.feature_engineering.features.price import PriceFeatureGenerator
from ai.feature_engineering.features.price_action import PriceActionFeatureGenerator
from ai.feature_engineering.features.rolling import RollingFeatureGenerator
from ai.feature_engineering.features.support_resistance import SupportResistanceFeatureGenerator
from ai.feature_engineering.features.target import TargetFeatureGenerator
from ai.feature_engineering.features.trend import TrendFeatureGenerator
from ai.feature_engineering.features.volatility import VolatilityFeatureGenerator
from ai.feature_engineering.features.volume import VolumeFeatureGenerator

# Ordered by data dependency: later groups may consume columns earlier groups produce.
_GENERATOR_REGISTRY: dict[str, type[BaseFeatureGenerator]] = {
    "price": PriceFeatureGenerator,
    "trend": TrendFeatureGenerator,
    "momentum": MomentumFeatureGenerator,
    "volatility": VolatilityFeatureGenerator,
    "bollinger": BollingerFeatureGenerator,
    "macd": MACDFeatureGenerator,
    "volume": VolumeFeatureGenerator,          # uses price.typical_price
    "rolling": RollingFeatureGenerator,
    "lag": LagFeatureGenerator,                # uses price.pct_return
    "date": DateFeatureGenerator,
    "price_action": PriceActionFeatureGenerator,
    "support_resistance": SupportResistanceFeatureGenerator,  # uses price_action.swing_high/low
    "fibonacci": FibonacciFeatureGenerator,    # uses support_resistance.dynamic_support/resistance
    "market_structure": MarketStructureFeatureGenerator,      # uses price_action.change_of_character
    "breakout": BreakoutFeatureGenerator,      # uses support_resistance + volume
    "target": TargetFeatureGenerator,
}


def available_groups() -> list[str]:
    return list(_GENERATOR_REGISTRY)


def build_generators(config: FeatureEngineeringConfig) -> list[BaseFeatureGenerator]:
    """Instantiate every generator in `config.enabled_feature_groups`, in
    dependency-safe registry order (not necessarily the order they were
    listed in config).

    Raises:
        ValueError: an unknown group name is requested.
    """
    unknown = set(config.enabled_feature_groups) - set(_GENERATOR_REGISTRY)
    if unknown:
        raise ValueError(f"Unknown feature group(s): {sorted(unknown)}. Available: {available_groups()}")

    enabled = set(config.enabled_feature_groups)
    return [cls(config) for name, cls in _GENERATOR_REGISTRY.items() if name in enabled]


__all__ = [
    "BaseFeatureGenerator",
    "FeatureDefinition",
    "available_groups",
    "build_generators",
]
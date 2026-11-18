"""
Base abstractions for `ai/feature_engineering/features/`.

Every feature group (price, trend, momentum, ...) implements
`BaseFeatureGenerator` so the pipeline can treat them uniformly (Strategy
pattern): each generator receives the DataFrame built up so far, adds its own
columns, and declares metadata about what it added (`describe()`), which
feeds `Feature_Metadata.json` / `Feature_Report.md` (Sprint 2 output
requirement) without duplicating documentation by hand.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Literal

import pandas as pd

from ai.feature_engineering.config import FeatureEngineeringConfig
from ai.feature_engineering.exceptions import FeatureComputationError
from ai.utils.logger import get_logger

Priority = Literal["High", "Medium", "Low"]
ModelFamily = Literal["Machine Learning", "Time Series", "Deep Learning", "Decision Engine"]


@dataclass(frozen=True)
class FeatureDefinition:
    """Documents one generated column for `Feature_Metadata.json` / `Feature_Report.md`."""

    name: str
    group: str
    formula: str
    meaning: str
    interpretation: str
    priority: Priority
    recommended_for: tuple[ModelFamily, ...] = field(default_factory=tuple)
    advantages: str = ""
    limitations: str = ""
    when_to_use: str = ""

    def as_dict(self) -> dict:
        return {
            "name": self.name,
            "group": self.group,
            "formula": self.formula,
            "meaning": self.meaning,
            "interpretation": self.interpretation,
            "priority": self.priority,
            "recommended_for": list(self.recommended_for),
            "advantages": self.advantages,
            "limitations": self.limitations,
            "when_to_use": self.when_to_use,
        }


class BaseFeatureGenerator(ABC):
    """Template-method base class for a single feature group.

    Subclasses implement `_compute` (pure column addition logic) and
    `describe` (metadata). `generate` wraps `_compute` with logging,
    validation, and consistent error handling so subclasses stay focused on
    the math.
    """

    #: short, stable identifier used in config.enabled_feature_groups and logs
    group_name: str = "base"

    #: columns this generator requires to already exist on the input frame
    requires_columns: tuple[str, ...] = ("date", "open", "high", "low", "close", "volume")

    def __init__(self, config: FeatureEngineeringConfig):
        self.config = config
        self.logger = get_logger(f"feature_engineering.features.{self.group_name}")

    def generate(self, df: pd.DataFrame) -> pd.DataFrame:
        """Validate inputs, compute this group's features, and return the
        augmented DataFrame. Never mutates the caller's frame in place.
        """
        missing = [c for c in self.requires_columns if c not in df.columns]
        if missing:
            raise FeatureComputationError(
                self.group_name, f"missing required input column(s): {missing}",
                context={"available_columns": list(df.columns)},
            )
        before_cols = set(df.columns)
        try:
            out = self._compute(df.copy())
        except FeatureComputationError:
            raise
        except Exception as e:  # noqa: BLE001 - convert to typed error, never fail silently
            raise FeatureComputationError(self.group_name, str(e)) from e

        added = [c for c in out.columns if c not in before_cols]
        self.logger.info("Generated %d feature(s): %s", len(added), added)
        return out

    @abstractmethod
    def _compute(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add this group's columns to `df` and return it."""

    @abstractmethod
    def describe(self) -> list[FeatureDefinition]:
        """Return metadata for every column this generator can add."""
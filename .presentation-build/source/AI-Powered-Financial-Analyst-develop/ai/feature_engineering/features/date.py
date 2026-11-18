"""
Phase 3.J — Date/Calendar Features.

Captures seasonality and calendar effects (e.g. month-end rebalancing flows,
quarter-end reporting effects) that pure price/volume features can't see.
"""

import pandas as pd

from ai.feature_engineering.features.base import BaseFeatureGenerator, FeatureDefinition


class DateFeatureGenerator(BaseFeatureGenerator):
    group_name = "date"
    requires_columns = ("date",)

    def _compute(self, df: pd.DataFrame) -> pd.DataFrame:
        dt = df["date"]
        df["year"] = dt.dt.year
        df["quarter"] = dt.dt.quarter
        df["month"] = dt.dt.month
        df["week"] = dt.dt.isocalendar().week.astype(int)
        df["day"] = dt.dt.day
        df["day_of_week"] = dt.dt.dayofweek  # 0=Monday
        df["is_month_end"] = dt.dt.is_month_end
        df["is_month_start"] = dt.dt.is_month_start
        df["is_quarter_end"] = dt.dt.is_quarter_end
        return df

    def describe(self) -> list[FeatureDefinition]:
        common = dict(priority="Low", recommended_for=("Machine Learning",))
        return [
            FeatureDefinition(name="year", group=self.group_name, formula="Date.year",
                               meaning="Calendar year.", interpretation="Lets a model learn long-run/macro regime effects.", **common),
            FeatureDefinition(name="quarter", group=self.group_name, formula="Date.quarter",
                               meaning="Calendar quarter (1-4).", interpretation="Captures earnings-season/quarter-end effects.", **common),
            FeatureDefinition(name="month", group=self.group_name, formula="Date.month",
                               meaning="Calendar month (1-12).", interpretation="Captures seasonal patterns (e.g. 'January effect').", **common),
            FeatureDefinition(name="week", group=self.group_name, formula="Date.isocalendar().week",
                               meaning="ISO calendar week number.", interpretation="Finer-grained seasonality than month.", **common),
            FeatureDefinition(name="day", group=self.group_name, formula="Date.day",
                               meaning="Day of month (1-31).", interpretation="Captures monthly cyclicality (e.g. payday effects).", **common),
            FeatureDefinition(name="day_of_week", group=self.group_name, formula="Date.dayofweek (0=Mon)",
                               meaning="Day of the trading week.", interpretation="Captures day-of-week effects (e.g. 'Monday effect').",
                               priority="Medium", recommended_for=("Machine Learning",)),
            FeatureDefinition(name="is_month_end", group=self.group_name, formula="Date.is_month_end",
                               meaning="True on the last calendar day of the month.", interpretation="Flags potential month-end rebalancing flow.", **common),
            FeatureDefinition(name="is_month_start", group=self.group_name, formula="Date.is_month_start",
                               meaning="True on the first calendar day of the month.", interpretation="Flags potential start-of-month flow.", **common),
            FeatureDefinition(name="is_quarter_end", group=self.group_name, formula="Date.is_quarter_end",
                               meaning="True on the last calendar day of the quarter.", interpretation="Flags potential quarter-end/earnings-adjacent effects.",
                               priority="Medium", recommended_for=("Machine Learning", "Decision Engine")),
        ]
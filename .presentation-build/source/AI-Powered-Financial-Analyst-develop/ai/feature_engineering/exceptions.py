"""
Exception hierarchy for `ai/feature_engineering/`.

Mirrors the pattern established in `ai/data_collection/exceptions.py`: every
failure mode gets its own typed exception carrying structured context,
instead of a bare `Exception`/`ValueError`, so callers (Sprint 3+ model
training code) can catch precisely what they need to handle and errors are
never swallowed silently (SRS NFR-7).
"""

from typing import Any, Optional


class FeatureEngineeringError(Exception):
    """Base class for all errors raised by `ai/feature_engineering/`."""

    def __init__(self, message: str, *, context: Optional[dict] = None):
        self.message = message
        self.context = context or {}
        super().__init__(self._format())

    def _format(self) -> str:
        if self.context:
            ctx_str = ", ".join(f"{k}={v!r}" for k, v in self.context.items())
            return f"{self.message} ({ctx_str})"
        return self.message


class RawDataNotFoundError(FeatureEngineeringError):
    """No raw OHLCV file could be located under `datasets/raw/` for the request."""

    def __init__(self, ticker: str, search_dir: Any):
        super().__init__(
            f"no raw OHLCV file found for ticker '{ticker}'",
            context={"ticker": ticker, "search_dir": str(search_dir)},
        )
        self.ticker = ticker


class SchemaValidationError(FeatureEngineeringError):
    """Raw or intermediate DataFrame does not have the required columns/dtypes."""

    def __init__(self, reason: str, *, missing_columns: Optional[list] = None):
        super().__init__(reason, context={"missing_columns": missing_columns or []})
        self.missing_columns = missing_columns or []


class InsufficientDataError(FeatureEngineeringError):
    """Not enough rows remain after cleaning to compute the requested features
    (e.g. asking for a 200-day SMA on 30 rows of data).
    """

    def __init__(self, required_rows: int, available_rows: int, *, context: Optional[dict] = None):
        super().__init__(
            f"insufficient data: need at least {required_rows} rows, got {available_rows}",
            context={"required_rows": required_rows, "available_rows": available_rows, **(context or {})},
        )
        self.required_rows = required_rows
        self.available_rows = available_rows


class FeatureComputationError(FeatureEngineeringError):
    """A feature generator failed while computing its output columns."""

    def __init__(self, feature_group: str, reason: str, *, context: Optional[dict] = None):
        super().__init__(
            f"feature group '{feature_group}' failed: {reason}",
            context={"feature_group": feature_group, **(context or {})},
        )
        self.feature_group = feature_group


class StorageError(FeatureEngineeringError):
    """Saving/reading processed data, reports, or metadata failed."""
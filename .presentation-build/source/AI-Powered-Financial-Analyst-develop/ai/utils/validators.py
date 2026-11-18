"""
Shared validation helpers used across `ai/` modules — currently ticker
symbol format checking and date range normalization for Data Collection,
but intentionally generic enough for Feature Engineering / models later.
"""

import re
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import Optional, Union

from ai.utils.config import settings

DateLike = Union[str, date, datetime]

_TICKER_RE = re.compile(settings.ticker_pattern)


class ValidationError(ValueError):
    """Raised when a ticker or date range fails validation.

    Subclasses `ValueError` so existing `except ValueError` callers still
    work, while still being catchable specifically as `ValidationError`.
    """


def is_valid_ticker(ticker: str) -> bool:
    """Return True if `ticker` matches the expected symbol format.
    Format-only — does not confirm the ticker exists on an exchange.
    """
    if not isinstance(ticker, str):
        return False
    return bool(_TICKER_RE.match(ticker.strip().upper()))


def validate_ticker(ticker: str) -> str:
    """Validate and normalize a ticker symbol (uppercase, stripped).

    Raises:
        ValidationError: empty, non-string, or malformed ticker.
    """
    if not ticker or not isinstance(ticker, str) or not ticker.strip():
        raise ValidationError(f"ticker must be a non-empty string, got {ticker!r}")

    normalized = ticker.strip().upper()
    if not _TICKER_RE.match(normalized):
        raise ValidationError(
            f"ticker '{normalized}' does not match expected format (e.g. 'AAPL', 'BRK.B')"
        )
    return normalized


@dataclass(frozen=True)
class DateRange:
    """A validated, normalized (start, end) date pair, both inclusive."""

    start: date
    end: date

    @property
    def days(self) -> int:
        return (self.end - self.start).days + 1

    def as_strings(self, fmt: str = "%Y-%m-%d") -> tuple[str, str]:
        return self.start.strftime(fmt), self.end.strftime(fmt)

    def __str__(self) -> str:
        s, e = self.as_strings()
        return f"{s} to {e}"


def _to_date(value: DateLike, *, field_name: str) -> date:
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%m/%d/%Y"):
            try:
                return datetime.strptime(value, fmt).date()
            except ValueError:
                continue
        raise ValidationError(f"could not parse {field_name}='{value}'. Expected format YYYY-MM-DD.")
    raise ValidationError(f"{field_name} must be a str, date, or datetime, got {type(value).__name__}")


def normalize_date_range(
    start: Optional[DateLike] = None,
    end: Optional[DateLike] = None,
    *,
    default_lookback_days: int = 365,
) -> DateRange:
    """Validate and normalize a (start, end) pair into a DateRange.

    - If both are omitted, defaults to the last `default_lookback_days` days.
    - If only `end` is given, `start` is derived from the lookback window.
    - If only `start` is given, `end` defaults to today.
    - `start` must be <= `end`; `end` cannot be in the future.
    - The span cannot exceed settings.max_date_range_days.
    """
    today = date.today()

    end_date = _to_date(end, field_name="end") if end is not None else today
    start_date = (
        _to_date(start, field_name="start")
        if start is not None
        else end_date - timedelta(days=default_lookback_days)
    )

    if end_date > today:
        raise ValidationError(f"end date {end_date} cannot be in the future")
    if start_date > end_date:
        raise ValidationError(f"start date {start_date} must be on or before end date {end_date}")

    span_days = (end_date - start_date).days + 1
    if span_days > settings.max_date_range_days:
        raise ValidationError(
            f"date range spans {span_days} days, exceeding the {settings.max_date_range_days}-day limit"
        )

    return DateRange(start=start_date, end=end_date)
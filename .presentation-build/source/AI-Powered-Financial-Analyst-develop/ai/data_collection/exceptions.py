"""
Exception hierarchy for `ai/data_collection/`.

Every failure mode gets its own typed exception (carrying structured
context) instead of a bare `Exception`/`ValueError`, so callers — and
later, Feature Engineering — can catch precisely what they need to handle.
Satisfies SRS FR-1.4: provider errors/rate limits must be surfaced clearly,
never fail silently.
"""

from typing import Any, Optional


class DataCollectionError(Exception):
    """Base class for all errors raised by `ai/data_collection/`."""

    def __init__(self, message: str, *, context: Optional[dict] = None):
        self.message = message
        self.context = context or {}
        super().__init__(self._format())

    def _format(self) -> str:
        if self.context:
            ctx_str = ", ".join(f"{k}={v!r}" for k, v in self.context.items())
            return f"{self.message} ({ctx_str})"
        return self.message


class ConfigurationError(DataCollectionError):
    """Required configuration/credentials are missing or invalid (e.g. no API key)."""


class InvalidTickerError(DataCollectionError):
    """Ticker symbol fails format validation."""

    def __init__(self, ticker: str, reason: str = "invalid or unrecognized ticker symbol"):
        super().__init__(reason, context={"ticker": ticker})
        self.ticker = ticker


class InvalidDateRangeError(DataCollectionError):
    """Requested date range is malformed or out of bounds."""

    def __init__(self, start: Any, end: Any, reason: str):
        super().__init__(reason, context={"start": start, "end": end})
        self.start = start
        self.end = end


class ProviderError(DataCollectionError):
    """Base class for errors originating from an external data provider."""

    def __init__(self, message: str, *, provider: str, context: Optional[dict] = None):
        super().__init__(message, context={"provider": provider, **(context or {})})
        self.provider = provider


class ProviderConnectionError(ProviderError):
    """Provider could not be reached (network failure, DNS, timeout)."""


class ProviderRateLimitError(ProviderError):
    """Provider signaled that a rate limit has been exceeded."""

    def __init__(self, provider: str, retry_after_seconds: Optional[float] = None):
        super().__init__(
            "provider rate limit exceeded", provider=provider,
            context={"retry_after_seconds": retry_after_seconds},
        )
        self.retry_after_seconds = retry_after_seconds


class ProviderResponseError(ProviderError):
    """Provider returned an unexpected, empty, or malformed response."""

    def __init__(self, provider: str, reason: str, status_code: Optional[int] = None):
        super().__init__(reason, provider=provider, context={"status_code": status_code})
        self.status_code = status_code


class ProviderNotImplementedError(ProviderError):
    """Provider interface is defined but this method isn't wired to live
    calls yet (e.g. Alpha Vantage in Sprint 1).
    """

    def __init__(self, provider: str, method: str):
        super().__init__(
            f"'{method}' is not yet implemented for this provider",
            provider=provider, context={"method": method},
        )


class StorageError(DataCollectionError):
    """Saving/reading data to/from datasets/raw or storage/cache failed."""
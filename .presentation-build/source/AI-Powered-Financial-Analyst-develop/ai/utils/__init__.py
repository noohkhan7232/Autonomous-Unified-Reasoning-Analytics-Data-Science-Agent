"""Shared helpers used across `ai/` modules: config, logging, validation,
retry, and caching.
"""
from ai.utils.config import settings
from ai.utils.logger import get_logger
from ai.utils.validators import DateRange, normalize_date_range, is_valid_ticker, validate_ticker
from ai.utils.retry import retry_with_backoff
from ai.utils.cache import FileCache
from ai.utils.market_reference import US_INDICES, INDIA_INDICES, US_ETFS, INDIA_ETFS, with_exchange

__all__ = [
    "settings",
    "get_logger",
    "DateRange",
    "normalize_date_range",
    "is_valid_ticker",
    "validate_ticker",
    "retry_with_backoff",
    "FileCache",
    "US_INDICES",
    "INDIA_INDICES",
    "US_ETFS",
    "INDIA_ETFS",
    "with_exchange",
]
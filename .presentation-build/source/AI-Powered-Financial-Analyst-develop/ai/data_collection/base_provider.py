"""
Adapter interface for market-data providers.

Every concrete provider (Yahoo Finance, Alpha Vantage, Polygon, Twelve Data)
implements this interface so the rest of the pipeline never depends on a
specific vendor's API shape. Default provider is Yahoo Finance (free tier,
no API key required) — set DATA_PROVIDER in .env to switch (SRS FR-1.2).
"""

from abc import ABC, abstractmethod

import pandas as pd

from ai.utils.logger import get_logger


class BaseDataProvider(ABC):
    """Common interface every market-data provider must implement."""

    #: Short identifier used in logs and output filenames, e.g. "yahoo_finance".
    provider_name: str = "base"

    def __init__(self):
        self.logger = get_logger(f"data_collection.{self.provider_name}")

    @abstractmethod
    def get_historical_ohlcv(self, ticker: str, start: str, end: str, interval: str = "1d") -> pd.DataFrame:
        """Return a DataFrame with columns: date, open, high, low, close, volume."""
        raise NotImplementedError

    @abstractmethod
    def get_company_info(self, ticker: str) -> dict:
        """Return basic company/fundamental info for the ticker."""
        raise NotImplementedError

    def health_check(self) -> bool:
        """Return True if the provider is reachable and, if applicable,
        correctly authenticated. Cheap and side-effect-free. Subclasses
        override this; the default assumes unavailable.
        """
        return False

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} provider_name='{self.provider_name}'>"
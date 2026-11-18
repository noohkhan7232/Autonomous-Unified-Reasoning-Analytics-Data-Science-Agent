"""
Default data provider: Yahoo Finance via the `yfinance` package (free, no
API key required). Selected when DATA_PROVIDER=yahoo_finance (the default).
"""

import pandas as pd
import yfinance as yf

from ai.data_collection.base_provider import BaseDataProvider
from ai.data_collection.exceptions import (
    ProviderConnectionError,
    ProviderResponseError,
)
from ai.utils.retry import retry_with_backoff
from ai.utils.validators import normalize_date_range, validate_ticker


class YahooFinanceProvider(BaseDataProvider):
    provider_name = "yahoo_finance"

    @retry_with_backoff(exceptions=(ProviderConnectionError,))
    def get_historical_ohlcv(self, ticker: str, start: str, end: str, interval: str = "1d") -> pd.DataFrame:
        """Return a DataFrame with columns: date, open, high, low, close, volume.

        Raises:
            ValidationError: ticker or date range fails validation.
            ProviderResponseError: Yahoo Finance returned no data (unknown
                ticker, delisted symbol, or unsupported range/interval).
            ProviderConnectionError: network-level failure (retried automatically).
        """
        symbol = validate_ticker(ticker)
        date_range = normalize_date_range(start, end)
        self.logger.info("Fetching OHLCV for %s [%s, interval=%s]", symbol, date_range, interval)

        try:
            df = yf.download(symbol, start=start, end=end, interval=interval, progress=False, auto_adjust=False)
        except Exception as e:
            raise ProviderConnectionError(
                f"failed to fetch historical OHLCV: {e}", provider=self.provider_name,
                context={"ticker": symbol},
            ) from e

        if df is None or df.empty:
            raise ProviderResponseError(
                self.provider_name,
                reason=f"no historical price data returned for ticker '{symbol}' in range {date_range}",
            )

        # yfinance can return a MultiIndex on columns for a single ticker
        # depending on version; flatten it before renaming.
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        df = df.reset_index().rename(
            columns={
                "Date": "date",
                "Open": "open",
                "High": "high",
                "Low": "low",
                "Close": "close",
                "Volume": "volume",
            }
        )
        return df[["date", "open", "high", "low", "close", "volume"]]

    @retry_with_backoff(exceptions=(ProviderConnectionError,))
    def get_company_info(self, ticker: str) -> dict:
        """Return basic company/fundamental info for the ticker.

        Raises:
            ValidationError: ticker fails format validation.
            ProviderResponseError: Yahoo Finance returned no usable info.
            ProviderConnectionError: network-level failure (retried automatically).
        """
        symbol = validate_ticker(ticker)
        self.logger.info("Fetching company info for %s", symbol)

        try:
            info = yf.Ticker(symbol).info
        except Exception as e:
            raise ProviderConnectionError(
                f"failed to fetch company info: {e}", provider=self.provider_name,
                context={"ticker": symbol},
            ) from e

        if not info or len(info) <= 1:
            raise ProviderResponseError(
                self.provider_name, reason=f"no company info returned for ticker '{symbol}'"
            )

        return {
            "symbol": symbol,
            "name": info.get("longName"),
            "sector": info.get("sector"),
            "industry": info.get("industry"),
            "market_cap": info.get("marketCap"),
        }

    def health_check(self) -> bool:
        """Cheap reachability check: pull one day of SPY data."""
        try:
            df = yf.Ticker("SPY").history(period="1d")
            return df is not None and not df.empty
        except Exception as e:
            self.logger.warning("Yahoo Finance health check failed: %s", e)
            return False
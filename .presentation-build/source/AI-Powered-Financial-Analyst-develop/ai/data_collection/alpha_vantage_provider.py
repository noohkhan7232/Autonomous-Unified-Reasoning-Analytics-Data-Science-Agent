"""
Alpha Vantage provider — INTERFACE ONLY in Sprint 1 (SRS FR-1.2: providers
must be swappable via configuration without touching consumers).

Selected when DATA_PROVIDER=alpha_vantage in .env. `get_historical_ohlcv`
and `get_company_info` raise `ProviderNotImplementedError` for now; the
docstrings below document exactly which Alpha Vantage endpoint/params each
will use once implemented, so wiring it up later is a same-file change with
no impact on `DataCollectionManager` or any other consumer.
"""

import pandas as pd
import requests

from ai.data_collection.base_provider import BaseDataProvider
from ai.data_collection.exceptions import ConfigurationError, ProviderNotImplementedError
from ai.utils.config import settings

ALPHA_VANTAGE_BASE_URL = "https://www.alphavantage.co/query"


class AlphaVantageProvider(BaseDataProvider):
    provider_name = "alpha_vantage"

    def __init__(self):
        super().__init__()
        self.api_key = settings.alpha_vantage_api_key

    def _require_api_key(self) -> str:
        if not self.api_key:
            raise ConfigurationError(
                "ALPHA_VANTAGE_API_KEY is not set. Add it to your .env file (see .env.example)."
            )
        return self.api_key

    def get_historical_ohlcv(self, ticker: str, start: str, end: str, interval: str = "1d") -> pd.DataFrame:
        """Planned: function=TIME_SERIES_DAILY_ADJUSTED, symbol=ticker,
        outputsize=full, apikey=... Not implemented in Sprint 1.
        """
        raise ProviderNotImplementedError(self.provider_name, "get_historical_ohlcv")

    def get_company_info(self, ticker: str) -> dict:
        """Planned: function=OVERVIEW, symbol=ticker, apikey=...
        Not implemented in Sprint 1.
        """
        raise ProviderNotImplementedError(self.provider_name, "get_company_info")

    def health_check(self) -> bool:
        """Reports configuration status without exercising unimplemented
        data methods. True only means "key present and endpoint reachable"
        — not that data fetching works yet.
        """
        if not self.api_key:
            self.logger.info("Alpha Vantage health check: no API key configured (expected in Sprint 1).")
            return False
        try:
            response = requests.get(
                ALPHA_VANTAGE_BASE_URL,
                params={
                    "function": "TIME_SERIES_INTRADAY", "symbol": "IBM",
                    "interval": "60min", "apikey": self.api_key,
                },
                timeout=settings.request_timeout_seconds,
            )
            return response.status_code == 200
        except requests.exceptions.RequestException as e:
            self.logger.warning("Alpha Vantage health check failed: %s", e)
            return False
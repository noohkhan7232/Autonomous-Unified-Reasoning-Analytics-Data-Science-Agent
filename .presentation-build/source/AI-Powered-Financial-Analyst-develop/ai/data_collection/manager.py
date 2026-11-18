"""
DataCollectionManager — the single entry point for Module 1 (Data Collection).

A Facade over the provider adapters + storage helpers. Feature Engineering
and any other caller should interact only with this class rather than
importing providers directly (SRS FR-1.2: swappable providers behind a
common interface, invisible to consumers).

    from ai.data_collection import DataCollectionManager

    manager = DataCollectionManager()  # uses DATA_PROVIDER from .env (default: yahoo_finance)
    prices = manager.get_historical_prices("AAPL", "2023-01-01", "2023-12-31")
    info = manager.get_company_info("AAPL")
    news = manager.get_news("Apple Inc", "2024-01-01", "2024-01-31")
"""

from typing import Optional

import pandas as pd

from ai.data_collection import storage
from ai.data_collection.alpha_vantage_provider import AlphaVantageProvider
from ai.data_collection.base_provider import BaseDataProvider
from ai.data_collection.exceptions import DataCollectionError
from ai.data_collection.news_provider import BaseNewsProvider, NewsApiProvider
from ai.data_collection.symbol_search import search_symbols
from ai.data_collection.yahoo_finance_provider import YahooFinanceProvider
from ai.utils.config import settings
from ai.utils.logger import get_logger

_PROVIDER_REGISTRY: dict[str, type[BaseDataProvider]] = {
    "yahoo_finance": YahooFinanceProvider,
    "alpha_vantage": AlphaVantageProvider,
    # "polygon" / "twelve_data" are reserved in .env.example / docs/SRS.md
    # for future providers; register their classes here when implemented.
}


class DataCollectionManager:
    """Facade wiring a market-data provider + a news provider to storage.

    Args:
        data_provider: an instantiated BaseDataProvider. If omitted, resolved
            from settings.data_provider (i.e. DATA_PROVIDER in .env), defaulting
            to Yahoo Finance.
        news_provider: an instantiated BaseNewsProvider. Defaults to NewsApiProvider.
    """

    def __init__(
        self,
        data_provider: Optional[BaseDataProvider] = None,
        news_provider: Optional[BaseNewsProvider] = None,
    ):
        self.logger = get_logger("data_collection.manager")
        self.data_provider = data_provider or self._resolve_data_provider()
        self.news_provider = news_provider or NewsApiProvider()

        self.logger.info(
            "DataCollectionManager initialized (data_provider=%s, news_provider=%s)",
            self.data_provider.provider_name, self.news_provider.provider_name,
        )

    @staticmethod
    def _resolve_data_provider() -> BaseDataProvider:
        provider_cls = _PROVIDER_REGISTRY.get(settings.data_provider)
        if provider_cls is None:
            raise DataCollectionError(
                f"Unknown DATA_PROVIDER '{settings.data_provider}'. "
                f"Available: {list(_PROVIDER_REGISTRY)}"
            )
        return provider_cls()

    # ------------------------------------------------------------------
    # Historical OHLCV prices
    # ------------------------------------------------------------------

    def get_historical_prices(self, ticker: str, start: str, end: str, interval: str = "1d", save: bool = True) -> pd.DataFrame:
        df = self.data_provider.get_historical_ohlcv(ticker, start, end, interval=interval)
        if save:
            storage.save_ohlcv(df, self.data_provider.provider_name, ticker.upper(), start, end)
        return df

    def get_historical_prices_bulk(self, tickers: list[str], start: str, end: str, interval: str = "1d", save: bool = True, skip_errors: bool = True) -> dict[str, pd.DataFrame]:
        results: dict[str, pd.DataFrame] = {}
        for ticker in tickers:
            try:
                results[ticker] = self.get_historical_prices(ticker, start, end, interval=interval, save=save)
            except Exception as e:
                self.logger.error("Failed to download prices for %s: %s", ticker, e)
                if not skip_errors:
                    raise
        return results

    # ------------------------------------------------------------------
    # Company info
    # ------------------------------------------------------------------

    def get_company_info(self, ticker: str, save: bool = True) -> dict:
        info = self.data_provider.get_company_info(ticker)
        if save:
            storage.save_company_info(info, self.data_provider.provider_name, ticker.upper())
        return info

    # ------------------------------------------------------------------
    # News
    # ------------------------------------------------------------------

    def get_news(self, query: str, start: str = None, end: str = None, page_size: int = 50, save: bool = True) -> list[dict]:
        articles = self.news_provider.get_news_articles(query, start=start, end=end, page_size=page_size)
        if save:
            storage.save_news(articles, self.news_provider.provider_name, query, start, end)
        return articles

    # ------------------------------------------------------------------
    # Symbol search — lets a user find the correct ticker by company name
    # (e.g. "physicswallah" -> "PWL.NS") instead of needing to know it
    # upfront. This is what a front-end search box should call.
    # ------------------------------------------------------------------

    def search_symbol(self, query: str, max_results: int = 8) -> list[dict]:
        return search_symbols(query, max_results=max_results)

    # ------------------------------------------------------------------
    # Convenience: download everything for one ticker in one call
    # ------------------------------------------------------------------

    def collect_full_dataset(self, ticker: str, company_name: str = None, start: str = None, end: str = None) -> dict:
        """Download historical prices, company info, and news for one ticker.
        Per-stage failures are caught and reported rather than aborting the
        whole call, so (e.g.) a missing NEWS_API_KEY doesn't block price data.
        """
        news_query = company_name or ticker
        result: dict = {"prices": None, "company_info": None, "news": None, "errors": {}}

        try:
            result["prices"] = self.get_historical_prices(ticker, start, end)
        except DataCollectionError as e:
            self.logger.error("collect_full_dataset: price download failed for %s: %s", ticker, e)
            result["errors"]["prices"] = str(e)

        try:
            result["company_info"] = self.get_company_info(ticker)
        except DataCollectionError as e:
            self.logger.error("collect_full_dataset: company info failed for %s: %s", ticker, e)
            result["errors"]["company_info"] = str(e)

        try:
            result["news"] = self.get_news(news_query, start, end)
        except DataCollectionError as e:
            self.logger.error("collect_full_dataset: news download failed for %s: %s", ticker, e)
            result["errors"]["news"] = str(e)

        return result

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def health_check(self) -> dict[str, bool]:
        """Check reachability/auth of every configured provider."""
        return {
            self.data_provider.provider_name: self.data_provider.health_check(),
            self.news_provider.provider_name: self.news_provider.health_check(),
        }
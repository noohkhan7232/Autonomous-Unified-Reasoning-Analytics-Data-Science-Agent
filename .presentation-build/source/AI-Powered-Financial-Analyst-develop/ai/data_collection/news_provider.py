"""
News provider adapter interface + NewsAPI (https://newsapi.org) implementation.

Kept separate from `BaseDataProvider` (OHLCV/company info) because news
articles are a fundamentally different shape of data — a news provider has
no concept of "historical OHLCV". Configured via NEWS_API_KEY in .env.
"""

from abc import ABC, abstractmethod

import requests

from ai.data_collection.exceptions import (
    ConfigurationError,
    ProviderConnectionError,
    ProviderRateLimitError,
    ProviderResponseError,
)
from ai.utils.cache import FileCache
from ai.utils.config import settings
from ai.utils.logger import get_logger
from ai.utils.retry import retry_with_backoff
from ai.utils.validators import normalize_date_range

NEWS_API_BASE_URL = "https://newsapi.org/v2"


class BaseNewsProvider(ABC):
    """Adapter interface for financial news providers."""

    provider_name: str = "base_news"

    def __init__(self):
        self.logger = get_logger(f"data_collection.{self.provider_name}")

    @abstractmethod
    def get_news_articles(self, query: str, start: str = None, end: str = None, page_size: int = 50) -> list[dict]:
        """Return a list of article dicts: source, author, title,
        description, url, published_at, content.
        """
        raise NotImplementedError

    def health_check(self) -> bool:
        return False


class NewsApiProvider(BaseNewsProvider):
    provider_name = "news_api"

    def __init__(self):
        super().__init__()
        self.api_key = settings.news_api_key
        self._cache = FileCache(namespace=self.provider_name)

    def _require_api_key(self) -> str:
        if not self.api_key:
            raise ConfigurationError(
                "NEWS_API_KEY is not set. Add it to your .env file (see .env.example)."
            )
        return self.api_key

    @retry_with_backoff(exceptions=(ProviderConnectionError, ProviderRateLimitError))
    def get_news_articles(self, query: str, start: str = None, end: str = None, page_size: int = 50) -> list[dict]:
        """Fetch news articles matching `query`, optionally within [start, end].

        Results are cached on disk (storage/cache/news_api/) for
        settings.cache_ttl_seconds to conserve NewsAPI's free-tier quota.

        Raises:
            ConfigurationError: NEWS_API_KEY is missing.
            ProviderRateLimitError: HTTP 429 (retried automatically).
            ProviderConnectionError: network-level failure (retried automatically).
            ProviderResponseError: non-2xx response, or a malformed/empty payload.
        """
        api_key = self._require_api_key()
        date_range = normalize_date_range(start, end) if (start or end) else None

        params = {
            "q": query,
            "language": "en",
            "pageSize": min(page_size, 100),
            "sortBy": "publishedAt",
            "apiKey": api_key,
        }
        if date_range:
            params["from"], params["to"] = date_range.as_strings()

        cache_key = self._cache.make_key(query=query, page_size=page_size, date_range=str(date_range))
        cached = self._cache.get(cache_key)
        if cached is not None:
            self.logger.info("Using cached news results for query='%s'", query)
            return cached

        self.logger.info("Fetching news for query='%s' [%s]", query, date_range or "no date filter")

        try:
            response = requests.get(
                f"{NEWS_API_BASE_URL}/everything", params=params,
                timeout=settings.request_timeout_seconds,
            )
        except requests.exceptions.RequestException as e:
            raise ProviderConnectionError(
                f"failed to reach NewsAPI: {e}", provider=self.provider_name, context={"query": query}
            ) from e

        if response.status_code == 429:
            retry_after = response.headers.get("Retry-After")
            raise ProviderRateLimitError(
                self.provider_name, retry_after_seconds=float(retry_after) if retry_after else None
            )

        if response.status_code != 200:
            raise ProviderResponseError(
                self.provider_name,
                reason=f"NewsAPI returned HTTP {response.status_code}: {response.text[:200]}",
                status_code=response.status_code,
            )

        try:
            payload = response.json()
        except ValueError as e:
            raise ProviderResponseError(
                self.provider_name, reason=f"NewsAPI returned invalid JSON: {e}",
                status_code=response.status_code,
            ) from e

        if payload.get("status") != "ok":
            raise ProviderResponseError(
                self.provider_name, reason=f"NewsAPI error: {payload.get('message', 'unknown error')}",
                status_code=response.status_code,
            )

        articles = [
            {
                "source": (a.get("source") or {}).get("name"),
                "author": a.get("author"),
                "title": a.get("title"),
                "description": a.get("description"),
                "url": a.get("url"),
                "published_at": a.get("publishedAt"),
                "content": a.get("content"),
                "query": query,
            }
            for a in payload.get("articles", [])
        ]

        self._cache.set(cache_key, articles)
        return articles

    def health_check(self) -> bool:
        if not self.api_key:
            self.logger.warning("NewsAPI health check skipped: no API key configured.")
            return False
        try:
            response = requests.get(
                f"{NEWS_API_BASE_URL}/everything",
                params={"q": "stock market", "pageSize": 1, "apiKey": self.api_key},
                timeout=settings.request_timeout_seconds,
            )
            return response.status_code == 200
        except requests.exceptions.RequestException as e:
            self.logger.warning("NewsAPI health check failed: %s", e)
            return False
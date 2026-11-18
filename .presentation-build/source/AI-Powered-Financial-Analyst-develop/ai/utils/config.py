"""
Centralized configuration for the `ai/` package.

Mirrors `backend/app/core/config.py`'s pattern: every environment variable
used anywhere under `ai/` is declared here and nowhere else, so modules
import `settings` instead of calling `os.environ` directly. Reads from the
project-root `.env` (see `.env.example`).
"""

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# ai/utils/config.py -> ai/utils -> ai -> project root
PROJECT_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=str(PROJECT_ROOT / ".env"), extra="ignore")

    # App
    environment: str = "development"
    log_level: str = "INFO"

    # Data providers (see docs/SRS.md FR-1.2)
    data_provider: str = "yahoo_finance"  # yahoo_finance | alpha_vantage | polygon | twelve_data
    alpha_vantage_api_key: str | None = None
    polygon_api_key: str | None = None
    twelve_data_api_key: str | None = None

    # News / Sentiment
    news_api_key: str | None = None

    # Network / resilience (Data Collection module)
    request_timeout_seconds: int = 15
    request_max_retries: int = 3
    request_backoff_factor: float = 2.0

    # Caching (Data Collection module)
    cache_ttl_seconds: int = 3600

    # Storage locations (relative to project root; see storage/README.md, datasets/README.md)
    raw_data_dir: str = "datasets/raw"
    processed_data_dir: str = "datasets/processed"
    cache_dir: str = "storage/cache"
    log_dir: str = "storage/logs"
    eda_reports_dir: str = "storage/reports/eda"

    # Validation
    # Optional leading '^' supports index symbols (e.g. ^NSEI for Nifty 50,
    # ^BSESN for Sensex, ^GSPC for S&P 500, ^DJI for Dow Jones). The suffix
    # accepts both '.' and '-' as separators because Yahoo Finance uses
    # different conventions depending on the exchange/instrument: share
    # classes are hyphenated (BRK-B), while exchange suffixes use a dot
    # (RELIANCE.NS, TCS.BO). ETFs (SPY, QQQ, NIFTYBEES.NS) need no special
    # handling — they match the same pattern as regular equity tickers.
    ticker_pattern: str = r"^\^?[A-Z]{1,10}([.\-][A-Z]{1,3})?$"
    max_date_range_days: int = 3650  # 10 years

    def resolve(self, relative_dir: str, *parts: str) -> Path:
        """Resolve a project-relative directory (e.g. self.raw_data_dir) to
        an absolute Path, appending any extra path parts.
        """
        return PROJECT_ROOT / relative_dir / Path(*parts)


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
"""
Centralized application configuration.

All environment variables are declared here and nowhere else, so the rest of
the codebase imports `settings` instead of calling `os.environ` directly.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # App
    environment: str = "development"
    debug: bool = True
    secret_key: str = "change-me"
    api_v1_prefix: str = "/api/v1"

    # Database
    database_url: str = "postgresql+asyncpg://fin_analyst:change-me@localhost:5432/fin_analyst_db"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # JWT
    jwt_secret_key: str = "change-me-jwt-secret"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    # Data providers
    data_provider: str = "yahoo_finance"
    alpha_vantage_api_key: str | None = None
    polygon_api_key: str | None = None
    twelve_data_api_key: str | None = None

    # LLM providers
    llm_provider: str = "groq"
    gemini_api_key: str | None = None
    groq_api_key: str | None = None
    openrouter_api_key: str | None = None


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

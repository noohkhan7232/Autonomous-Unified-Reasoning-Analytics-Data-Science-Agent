# Module 1 — Data Collection (`ai/data_collection/`)

Implements SRS §3.1 (FR-1.1 – FR-1.4). Pulls historical OHLCV prices,
company fundamentals, and financial news from configurable providers and
persists raw output to `datasets/raw/` for reproducibility — nothing else.
Feature Engineering (`ai/feature_engineering/`, Module 2) starts where this
module stops; this module does not transform, resample, or engineer
anything.

## 1. Why This Module Is Built First

Per `docs/architecture/ARCHITECTURE.md`, every downstream module — Feature
Engineering, ML/Time-Series/Deep-Learning, FinBERT sentiment, the Decision
Support Engine, and the LLM explanation layer — consumes data this module
produces. If that data is inconsistent, incomplete, or silently wrong,
nothing built on top of it can be trusted:

- **Garbage in, garbage out.** A model trained on price data with a silent
  gap (a failed download nobody checked) produces confident-looking but
  meaningless predictions.
- **Downstream needs a stable on-disk contract.** Feature Engineering must
  know exactly where files live and what "no data available" looks like.
  Deciding that now (FR-1.3: raw data keyed by provider + ticker + date
  range) means later modules start from a solid foundation.
- **External APIs are unreliable by nature.** Rate limits, timeouts, and
  unknown tickers are the norm when talking to Yahoo Finance / NewsAPI /
  Alpha Vantage. Retries, caching, and structured error handling belong at
  the source (FR-1.4), not patched into every consumer later.
- **Multiple-provider support is architectural, not a bolt-on** (FR-1.2).
  `BaseDataProvider` / `BaseNewsProvider` exist so swapping or adding a
  vendor later is a one-file change, not a rewrite.

## 2. Architecture

```
              ai/data_collection/manager.py
              DataCollectionManager (Facade)
         ┌──────────────┴──────────────┐
         │                              │
   BaseDataProvider              BaseNewsProvider
   (base_provider.py)             (news_provider.py)
         │                              │
   ┌─────┴─────┐                        │
   ▼           ▼                        ▼
YahooFinance  AlphaVantage          NewsApiProvider
Provider      Provider              (news_provider.py)
(live)        (interface only,
               Sprint 1 scope)

         All providers depend on shared, reusable primitives:
         ai/utils/validators.py   — ticker + date range validation
         ai/utils/retry.py        — retry-with-backoff decorator
         ai/utils/cache.py        — TTL file cache (storage/cache/)
         ai/utils/logger.py       — structured logging (storage/logs/)
         ai/utils/config.py       — settings singleton (.env + pydantic-settings)

         storage.py persists results to datasets/raw/
```

**Design principles:**

1. **Dependency inversion** — `DataCollectionManager` and any future caller
   depend on `BaseDataProvider` / `BaseNewsProvider`, never on a concrete
   provider class (FR-1.2). Swapping `DATA_PROVIDER=yahoo_finance` for
   `alpha_vantage` in `.env` requires zero code changes once Alpha Vantage
   is fully implemented.
2. **Single responsibility** — providers only know how to talk to one
   external API and normalize its response shape. `storage.py` only knows
   how to persist. `manager.py` only knows how to wire providers to storage.
3. **Facade pattern** — `DataCollectionManager` is the one stable entry
   point the rest of the pipeline should import.
4. **Fail loud, fail typed** (FR-1.4) — every failure mode has its own
   exception class in `exceptions.py` carrying structured context, so
   callers catch precisely what they need instead of parsing strings.

## 3. Files

| File | Purpose |
|---|---|
| `__init__.py` | Re-exports `DataCollectionManager` as the module's public entry point. |
| `base_provider.py` | `BaseDataProvider` — abstract interface (`get_historical_ohlcv`, `get_company_info`, `health_check`) every market-data provider implements. |
| `yahoo_finance_provider.py` | `YahooFinanceProvider` — default, live implementation via `yfinance`. No API key required. Validates input, retries on connection failure, raises `ProviderResponseError` on empty/unknown-ticker results. |
| `alpha_vantage_provider.py` | `AlphaVantageProvider` — **interface only** per Sprint 1 scope. `get_historical_ohlcv` / `get_company_info` raise `ProviderNotImplementedError`; docstrings document the exact planned endpoint/params (`TIME_SERIES_DAILY_ADJUSTED`, `OVERVIEW`) so wiring it up later is a same-file change. `health_check()` works today (reports key-configured + endpoint-reachable). |
| `news_provider.py` | `BaseNewsProvider` (interface) + `NewsApiProvider` — live implementation against NewsAPI.org's `/v2/everything`, using `NEWS_API_KEY`. Handles missing keys, HTTP 429 (honors `Retry-After`), and malformed responses. Caches results via `FileCache` to conserve free-tier quota. |
| `manager.py` | `DataCollectionManager` — the Facade. Resolves the active data provider from `DATA_PROVIDER` in `.env` (or accepts an injected provider), wires it plus `NewsApiProvider` to `storage.py`, and exposes `get_historical_prices`, `get_company_info`, `get_news`, bulk variants, `collect_full_dataset`, and `health_check`. |
| `storage.py` | Atomic (temp-file + rename) persistence to `datasets/raw/`, filenames keyed by `{provider}_{ticker}_{start}_{end}_ohlcv.csv`, `{provider}_{ticker}_company_info.json`, `{provider}_{query}_{start}_{end}_news.json` — satisfies FR-1.3 exactly. |
| `exceptions.py` | Typed exception hierarchy: `DataCollectionError` at the root, with `ConfigurationError`, `InvalidTickerError` / `InvalidDateRangeError` (also exposed via `ai.utils.validators.ValidationError`), `ProviderConnectionError`, `ProviderRateLimitError`, `ProviderResponseError`, `ProviderNotImplementedError`, `StorageError`. |

### Shared helpers this module relies on (`ai/utils/`)

| File | Purpose |
|---|---|
| `config.py` | `Settings(BaseSettings)` — mirrors `backend/app/core/config.py`'s pattern. Reads the project-root `.env`; every env var used anywhere in `ai/` is declared once here (`DATA_PROVIDER`, `ALPHA_VANTAGE_API_KEY`, `NEWS_API_KEY`, retry/cache/timeout tuning, storage paths). |
| `logger.py` | `get_logger(__name__)` — one shared console + rotating-file handler (`storage/logs/ai.log`), configured once, used by every provider and the manager. |
| `validators.py` | `validate_ticker`, `is_valid_ticker`, `normalize_date_range` — fast, network-free input validation shared by every provider, so obviously-bad input is rejected before any API call or rate-limit quota is spent. |
| `retry.py` | `@retry_with_backoff(exceptions=(...))` — exponential-backoff retry decorator applied to provider network calls; honors a provider's `retry_after_seconds` when present. |
| `cache.py` | `FileCache(namespace, ttl_seconds)` — simple TTL JSON file cache under `storage/cache/<namespace>/`, used by `NewsApiProvider`. |

## 4. Configuration

All configuration is environment-driven via the project-root `.env` (copy
from `.env.example`), loaded through `ai/utils/config.py`:

| Variable | Default | Purpose |
|---|---|---|
| `DATA_PROVIDER` | `yahoo_finance` | Active market-data provider (`yahoo_finance` \| `alpha_vantage`; `polygon`/`twelve_data` reserved for future providers). |
| `ALPHA_VANTAGE_API_KEY` | _(empty)_ | Required once Alpha Vantage is fully implemented. |
| `NEWS_API_KEY` | _(empty)_ | Required for `get_news()` / `NewsApiProvider`. Get a free key at newsapi.org. |
| `LOG_LEVEL` | `INFO` | Logging verbosity. |
| `REQUEST_TIMEOUT_SECONDS` | `15` | HTTP timeout for provider requests. |
| `REQUEST_MAX_RETRIES` | `3` | Max retry attempts on connection/rate-limit errors. |
| `REQUEST_BACKOFF_FACTOR` | `2.0` | Exponential backoff base multiplier. |
| `CACHE_TTL_SECONDS` | `3600` | How long cached NewsAPI results stay valid. |

## 5. Usage

```python
from ai.data_collection import DataCollectionManager

manager = DataCollectionManager()  # provider resolved from DATA_PROVIDER

# -> datasets/raw/yahoo_finance_AAPL_2023-01-01_2023-12-31_ohlcv.csv
prices = manager.get_historical_prices("AAPL", "2023-01-01", "2023-12-31")

# -> datasets/raw/yahoo_finance_AAPL_company_info.json
info = manager.get_company_info("AAPL")

# -> datasets/raw/news_api_Apple_Inc_2024-01-01_2024-01-31_news.json
news = manager.get_news("Apple Inc", "2024-01-01", "2024-01-31")

# Everything at once, with per-stage error isolation
bundle = manager.collect_full_dataset("AAPL", company_name="Apple Inc")

manager.health_check()  # {"yahoo_finance": True, "news_api": True}
```

## 6. How This Connects to Feature Engineering (Module 2)

Feature Engineering (`ai/feature_engineering/`) reads directly from
`datasets/raw/`:

- **OHLCV CSVs** → technical indicators (MA, EMA, RSI, MACD, Bollinger,
  ATR), lag/rolling-window features, train/test splitting for the
  ML / ARIMA / LSTM-GRU branches (Modules 3–5).
- **Company info JSON** → static/fundamental features (sector, market cap)
  joined onto the per-ticker time-series feature set.
- **News JSON** → input to FinBERT sentiment scoring (Module 6), producing
  a daily sentiment score per ticker that merges back into the same
  feature table.

Because every file here follows the fixed naming convention in
`storage.py`, Feature Engineering never needs to know which provider
produced the data, how retries/caching work, or whether Alpha Vantage is
live yet — only the `datasets/raw/` contract.

## 7. Testing

```bash
pip install -r ai/requirements.txt
pytest ai/tests -v
```

`ai/tests/test_data_collection.py` is deliberately network-free (validates
tickers/date ranges, the file cache, Alpha Vantage's not-implemented
behavior, and Facade wiring) so it runs safely in CI
(`.github/workflows/ci.yml: ai-tests`) without API keys or network access.

## 8. Out of Scope for Sprint 1

Per `docs/MVP.md` and the sprint plan: Feature Engineering, ML/ARIMA/LSTM
models, FinBERT sentiment scoring, the Decision Support Engine, the LLM
explanation/chat layer, the React dashboard, backend APIs, and
authentication. Alpha Vantage is interface-only and makes no live data
calls yet (`health_check()` is the exception — it only confirms
reachability/auth, not data fetching).
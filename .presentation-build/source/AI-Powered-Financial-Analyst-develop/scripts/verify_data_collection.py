"""
scripts/verify_data_collection.py
====================================
One-off script to confirm the Data Collection Module (ai/data_collection/)
actually works against LIVE Yahoo Finance / NewsAPI endpoints on your
machine (this cannot be verified inside the sandbox that built the code,
since that sandbox blocks those hosts).

Usage:
    # from the project root
    pip install -r ai/requirements.txt
    cp .env.example .env          # then add NEWS_API_KEY (get a free one at newsapi.org)
    python scripts/verify_data_collection.py

What it checks, in order:
    1. Provider health check (Yahoo Finance + NewsAPI reachability/auth)
    2. Historical OHLCV download for AAPL -> saved to datasets/raw/
    3. Company info download for AAPL -> saved to datasets/raw/
    4. News download for "Apple Inc" -> saved to datasets/raw/ (skipped
       with a clear message if NEWS_API_KEY isn't set)
    5. Alpha Vantage correctly raises "not implemented" (Sprint 1 scope)

Exits with a non-zero status code if any REQUIRED check fails, so this can
also be wired into a manual pre-flight check before a demo.
"""

import sys
from datetime import date, timedelta
from pathlib import Path

# Allow running this script directly (python scripts/verify_data_collection.py)
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ai.data_collection import DataCollectionManager  # noqa: E402
from ai.data_collection.alpha_vantage_provider import AlphaVantageProvider  # noqa: E402
from ai.data_collection.exceptions import ProviderNotImplementedError  # noqa: E402

PASS = "\033[92mPASS\033[0m"
FAIL = "\033[91mFAIL\033[0m"
SKIP = "\033[93mSKIP\033[0m"


def main() -> int:
    failures = 0
    manager = DataCollectionManager()

    print("=" * 60)
    print("1. Provider health check")
    print("=" * 60)
    health = manager.health_check()
    for provider, ok in health.items():
        print(f"  [{PASS if ok else FAIL}] {provider}")
    if not health.get("yahoo_finance"):
        failures += 1

    print()
    print("=" * 60)
    print("2. Historical OHLCV download (AAPL, last 30 days)")
    print("=" * 60)
    try:
        df = manager.get_historical_prices("AAPL", "2024-01-01", "2024-01-31")
        print(f"  [{PASS}] Downloaded {len(df)} rows. Columns: {list(df.columns)}")
        print(df.head(3).to_string(index=False))
    except Exception as e:
        print(f"  [{FAIL}] {e}")
        failures += 1

    print()
    print("=" * 60)
    print("3. Company info download (AAPL)")
    print("=" * 60)
    try:
        info = manager.get_company_info("AAPL")
        print(f"  [{PASS}] {info}")
    except Exception as e:
        print(f"  [{FAIL}] {e}")
        failures += 1

    print()
    print("=" * 60)
    print("4. News download ('Apple Inc')")
    print("=" * 60)
    # Free NewsAPI plans only allow articles from roughly the last 30 days,
    # so this uses a recent rolling window instead of a fixed historical date.
    news_end = date.today() - timedelta(days=1)
    news_start = news_end - timedelta(days=6)
    try:
        articles = manager.get_news("Apple Inc", news_start.isoformat(), news_end.isoformat())
        print(f"  [{PASS}] Fetched {len(articles)} article(s).")
        if articles:
            print(f"  First headline: {articles[0].get('title')}")
    except Exception as e:
        msg = str(e)
        if "NEWS_API_KEY" in msg:
            print(f"  [{SKIP}] {msg}")
        else:
            print(f"  [{FAIL}] {msg}")
            failures += 1

    print()
    print("=" * 60)
    print("5. Alpha Vantage correctly reports 'not implemented' (Sprint 1 scope)")
    print("=" * 60)
    try:
        AlphaVantageProvider().get_historical_ohlcv("AAPL", "2024-01-01", "2024-01-31")
        print(f"  [{FAIL}] Expected ProviderNotImplementedError but call succeeded.")
        failures += 1
    except ProviderNotImplementedError as e:
        print(f"  [{PASS}] {e}")

    print()
    print("=" * 60)
    print(f"Saved files are under: datasets/raw/")
    print(f"Log output is under:   storage/logs/ai.log")
    print("=" * 60)

    if failures:
        print(f"\n{failures} check(s) failed.")
        return 1

    print("\nAll required checks passed. Data Collection Module is live and working.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
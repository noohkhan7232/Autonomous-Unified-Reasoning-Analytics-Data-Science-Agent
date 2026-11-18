"""
scripts/fetch_global_markets_demo.py
=======================================
Demo script showing how to use ai/utils/market_reference.py to download
US and India indices, ETFs, and individual stocks with the Data
Collection Module.

Usage:
    python scripts/fetch_global_markets_demo.py

Downloads a small sample of each category and saves them to
datasets/raw/ (same as any other DataCollectionManager call).
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ai.data_collection import DataCollectionManager  # noqa: E402
from ai.utils.market_reference import (  # noqa: E402
    INDIA_ETFS,
    INDIA_INDICES,
    US_ETFS,
    US_INDICES,
    with_exchange,
)

START = "2024-01-01"
END = "2024-01-31"


def fetch_and_report(manager: DataCollectionManager, label: str, ticker: str) -> None:
    try:
        df = manager.get_historical_prices(ticker, START, END)
        print(f"  [OK] {label:20s} ({ticker:12s}) -> {len(df)} rows")
    except Exception as e:
        print(f"  [FAIL] {label:20s} ({ticker:12s}) -> {e}")


def main() -> None:
    manager = DataCollectionManager()

    print("=== US Indices ===")
    for name, ticker in US_INDICES.items():
        fetch_and_report(manager, name, ticker)

    print("\n=== India Indices ===")
    for name, ticker in INDIA_INDICES.items():
        fetch_and_report(manager, name, ticker)

    print("\n=== US ETFs ===")
    for name, ticker in US_ETFS.items():
        fetch_and_report(manager, name, ticker)

    print("\n=== India ETFs ===")
    for name, ticker in INDIA_ETFS.items():
        fetch_and_report(manager, name, ticker)

    print("\n=== Individual stocks (built with with_exchange) ===")
    for name, symbol in [("Reliance (NSE)", "reliance"), ("TCS (NSE)", "tcs"), ("Infosys (NSE)", "infy")]:
        ticker = with_exchange(symbol, "nse")
        fetch_and_report(manager, name, ticker)

    print("\nAll saved under datasets/raw/")


if __name__ == "__main__":
    main()
"""
scripts/search_symbol_demo.py
================================
Lets you search for a company name (like Yahoo Finance's own search bar)
and see which ticker symbol(s) match, instead of needing to already know
the exact symbol.

Usage:
    python scripts/search_symbol_demo.py "physicswallah"
    python scripts/search_symbol_demo.py "state bank of india"
    python scripts/search_symbol_demo.py "bajaj finance"

If no query is given, prompts for one interactively.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ai.data_collection import DataCollectionManager  # noqa: E402


def main() -> None:
    query = " ".join(sys.argv[1:]).strip()
    if not query:
        query = input("Search for a company name or ticker: ").strip()

    if not query:
        print("No query given, exiting.")
        return

    manager = DataCollectionManager()
    print(f"\nSearching for '{query}'...\n")

    results = manager.search_symbol(query)

    if not results:
        print("No matches found.")
        return

    print(f"{'Symbol':15s} {'Name':40s} {'Exchange':10s} {'Type':10s}")
    print("-" * 80)
    for r in results:
        name = (r.get("name") or "")[:40]
        print(f"{r.get('symbol', ''):15s} {name:40s} {r.get('exchange', ''):10s} {r.get('type', ''):10s}")

    print(f"\nUse any 'Symbol' above with manager.get_historical_prices(...)")


if __name__ == "__main__":
    main()
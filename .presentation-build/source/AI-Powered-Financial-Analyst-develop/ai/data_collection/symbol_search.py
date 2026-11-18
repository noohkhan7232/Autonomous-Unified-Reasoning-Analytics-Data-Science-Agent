"""
Symbol search — lets a user type a company name ("physicswallah", "sbi",
"bajaj") and get back matching ticker symbols, exactly like Yahoo
Finance's own search bar. Without this, a user would need to already know
the exact ticker (e.g. "PWL.NS") before they could request any data —
this module removes that requirement.

Wraps `yfinance.Search`, which queries Yahoo Finance's own search index
(this is a live network call, unlike ticker/date validation which is
local and instant).
"""

from typing import Any

import yfinance as yf

from ai.data_collection.exceptions import ProviderConnectionError
from ai.utils.logger import get_logger
from ai.utils.retry import retry_with_backoff

logger = get_logger("data_collection.symbol_search")


@retry_with_backoff(exceptions=(ProviderConnectionError,))
def search_symbols(query: str, max_results: int = 8) -> list[dict[str, Any]]:
    """Search Yahoo Finance for tickers matching a company name or partial
    symbol. Returns a normalized list of matches, most-relevant first.

    Example:
        search_symbols("physicswallah")
        -> [{"symbol": "PWL.NS", "name": "PhysicsWallah Ltd", "exchange": "NSI", "type": "EQUITY"}, ...]

    Raises:
        ProviderConnectionError: network-level failure (retried automatically).
    """
    if not query or not query.strip():
        return []

    logger.info("Searching symbols for query='%s'", query)
    try:
        results = yf.Search(query, max_results=max_results).quotes
    except Exception as e:
        raise ProviderConnectionError(
            f"symbol search failed: {e}", provider="yahoo_finance", context={"query": query}
        ) from e

    return [
        {
            "symbol": r.get("symbol"),
            "name": r.get("shortname") or r.get("longname"),
            "exchange": r.get("exchange"),
            "type": r.get("quoteType"),
        }
        for r in results
        if r.get("symbol")
    ]
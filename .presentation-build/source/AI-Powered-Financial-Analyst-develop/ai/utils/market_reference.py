"""
Reference lookup of commonly-used index and ETF symbols for the US and
Indian markets, in Yahoo Finance's ticker format (the format
`ai.data_collection.yahoo_finance_provider` expects).

This is a convenience lookup only — it is NOT an exhaustive list and does
NOT restrict which tickers `DataCollectionManager` will accept. Any ticker
matching `settings.ticker_pattern` (see ai/utils/config.py) works, whether
or not it's listed here; Yahoo Finance covers thousands of global
instruments this module doesn't attempt to catalog.

Usage:
    from ai.utils.market_reference import US_INDICES, INDIA_INDICES

    manager.get_historical_prices(US_INDICES["nasdaq"], "2024-01-01", "2024-12-31")
    manager.get_historical_prices(INDIA_INDICES["nifty50"], "2024-01-01", "2024-12-31")
"""

# ---------------------------------------------------------------------------
# Indices (all use a leading '^' on Yahoo Finance)
# ---------------------------------------------------------------------------

US_INDICES: dict[str, str] = {
    "sp500": "^GSPC",
    "dow_jones": "^DJI",
    "nasdaq": "^IXIC",
    "russell2000": "^RUT",
    "vix": "^VIX",
}

INDIA_INDICES: dict[str, str] = {
    "nifty50": "^NSEI",
    "sensex": "^BSESN",
    "bank_nifty": "^NSEBANK",
    "india_vix": "^INDIAVIX",
    # NOTE: "^CNXMDCP" (Nifty Midcap 100) was removed — confirmed via a live
    # run that Yahoo Finance returns HTTP 404 for it ("Quote not found").
    # Yahoo's coverage of secondary NSE indices is inconsistent and changes
    # over time; verify any additional index symbol with a manual
    # `manager.get_historical_prices(...)` call before relying on it.
}

# ---------------------------------------------------------------------------
# Popular broad-market ETFs (no exchange suffix needed for US-listed ETFs;
# Indian ETFs trade on NSE and use the standard '.NS' suffix)
# ---------------------------------------------------------------------------

US_ETFS: dict[str, str] = {
    "sp500": "SPY",          # SPDR S&P 500
    "nasdaq100": "QQQ",      # Invesco QQQ
    "total_market": "VTI",   # Vanguard Total Stock Market
    "dow_jones": "DIA",      # SPDR Dow Jones
    "emerging_markets": "EEM",
}

INDIA_ETFS: dict[str, str] = {
    "nifty50": "NIFTYBEES.NS",
    "bank_nifty": "BANKBEES.NS",
    "gold": "GOLDBEES.NS",
    # NOTE: "SENSEXBEES.NS" was removed — confirmed via a live run that
    # Yahoo Finance returns HTTP 404 for it ("Quote not found"). No
    # verified Sensex-tracking ETF symbol has been confirmed live yet;
    # add one back here only after confirming it with a manual
    # `manager.get_historical_prices(...)` call.
}

# ---------------------------------------------------------------------------
# Exchange suffixes (append to the raw symbol for Indian equities/ETFs)
# ---------------------------------------------------------------------------

EXCHANGE_SUFFIXES: dict[str, str] = {
    "nse": ".NS",   # National Stock Exchange of India
    "bse": ".BO",   # Bombay Stock Exchange
}


def with_exchange(symbol: str, exchange: str) -> str:
    """Append an exchange suffix to a raw symbol, e.g.
    with_exchange("RELIANCE", "nse") -> "RELIANCE.NS"

    Raises:
        KeyError: if `exchange` isn't a key in EXCHANGE_SUFFIXES.
    """
    return f"{symbol.upper()}{EXCHANGE_SUFFIXES[exchange.lower()]}"
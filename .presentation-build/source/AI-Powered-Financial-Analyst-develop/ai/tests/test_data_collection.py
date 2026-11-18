"""
Tests for ai/data_collection/ and its ai/utils/ dependencies.

Deliberately network-free (no live calls to Yahoo Finance / NewsAPI /
Alpha Vantage) so this runs safely in CI (`pytest ai/tests`, see
.github/workflows/ci.yml) without requiring API keys or network access.
Provider network behavior is exercised manually via examples/ or ad-hoc
scripts, not in the automated suite.
"""

from datetime import date, timedelta

import pytest

from ai.data_collection.alpha_vantage_provider import AlphaVantageProvider
from ai.data_collection.exceptions import ProviderNotImplementedError
from ai.data_collection.manager import DataCollectionManager
from ai.data_collection.yahoo_finance_provider import YahooFinanceProvider
from ai.utils.cache import FileCache
from ai.utils.validators import ValidationError, is_valid_ticker, normalize_date_range, validate_ticker


class TestTickerValidator:
    def test_valid_simple_ticker(self):
        assert is_valid_ticker("AAPL")
        assert validate_ticker("aapl") == "AAPL"

    def test_valid_ticker_with_share_class(self):
        assert is_valid_ticker("BRK.B")
        assert validate_ticker(" brk.b ") == "BRK.B"

    def test_invalid_empty_ticker(self):
        with pytest.raises(ValidationError):
            validate_ticker("")

    def test_invalid_ticker_format(self):
        assert not is_valid_ticker("123456")
        with pytest.raises(ValidationError):
            validate_ticker("hello world")

    def test_us_index_tickers(self):
        assert is_valid_ticker("^GSPC")   # S&P 500
        assert is_valid_ticker("^DJI")    # Dow Jones
        assert is_valid_ticker("^IXIC")   # Nasdaq
        assert validate_ticker("^gspc") == "^GSPC"

    def test_india_index_tickers(self):
        assert is_valid_ticker("^NSEI")     # Nifty 50
        assert is_valid_ticker("^BSESN")    # Sensex
        assert is_valid_ticker("^NSEBANK")  # Bank Nifty
        assert validate_ticker("^nsei") == "^NSEI"

    def test_india_equity_and_etf_tickers(self):
        assert is_valid_ticker("RELIANCE.NS")
        assert is_valid_ticker("TCS.NS")
        assert is_valid_ticker("TATAMOTORS.NS")
        assert is_valid_ticker("RELIANCE.BO")
        assert is_valid_ticker("NIFTYBEES.NS")  # ETF
        assert validate_ticker("reliance.ns") == "RELIANCE.NS"

    def test_us_etf_tickers(self):
        assert is_valid_ticker("SPY")
        assert is_valid_ticker("QQQ")
        assert is_valid_ticker("VTI")

    def test_hyphenated_share_class(self):
        # Yahoo Finance uses a hyphen (not a dot) for share classes, e.g. BRK-B.
        assert is_valid_ticker("BRK-B")
        assert validate_ticker("brk-b") == "BRK-B"


class TestMarketReference:
    def test_us_and_india_indices_are_valid_tickers(self):
        from ai.utils.market_reference import INDIA_INDICES, US_INDICES

        for symbol in {**US_INDICES, **INDIA_INDICES}.values():
            assert is_valid_ticker(symbol), f"{symbol} should be a valid ticker"

    def test_us_and_india_etfs_are_valid_tickers(self):
        from ai.utils.market_reference import INDIA_ETFS, US_ETFS

        for symbol in {**US_ETFS, **INDIA_ETFS}.values():
            assert is_valid_ticker(symbol), f"{symbol} should be a valid ticker"

    def test_with_exchange_helper(self):
        from ai.utils.market_reference import with_exchange

        assert with_exchange("reliance", "nse") == "RELIANCE.NS"
        assert with_exchange("reliance", "bse") == "RELIANCE.BO"


class TestDateUtils:
    def test_default_range_is_about_one_year(self):
        dr = normalize_date_range()
        assert dr.start < dr.end
        assert dr.days <= 367  # accounts for leap years

    def test_explicit_range(self):
        dr = normalize_date_range("2023-01-01", "2023-01-31")
        assert dr.start == date(2023, 1, 1)
        assert dr.end == date(2023, 1, 31)
        assert dr.days == 31

    def test_start_after_end_raises(self):
        with pytest.raises(ValidationError):
            normalize_date_range("2023-02-01", "2023-01-01")

    def test_future_end_date_raises(self):
        future = date.today() + timedelta(days=30)
        with pytest.raises(ValidationError):
            normalize_date_range(end=future)


class TestFileCache:
    def test_set_and_get_roundtrip(self):
        cache = FileCache(namespace="test_namespace", ttl_seconds=60)
        key = cache.make_key(a=1, b="two")
        cache.set(key, {"hello": "world"})
        assert cache.get(key) == {"hello": "world"}
        cache.clear()

    def test_missing_key_returns_none(self):
        cache = FileCache(namespace="test_namespace_missing", ttl_seconds=60)
        assert cache.get("nonexistent_key") is None


class TestAlphaVantageInterfaceOnly:
    """Alpha Vantage is interface-only in Sprint 1 (SRS scope) — confirm it
    fails predictably rather than silently, and never makes a network call.
    """

    def test_get_historical_ohlcv_not_implemented(self):
        provider = AlphaVantageProvider()
        with pytest.raises(ProviderNotImplementedError):
            provider.get_historical_ohlcv("AAPL", "2023-01-01", "2023-12-31")

    def test_get_company_info_not_implemented(self):
        provider = AlphaVantageProvider()
        with pytest.raises(ProviderNotImplementedError):
            provider.get_company_info("AAPL")

    def test_health_check_false_without_api_key(self, monkeypatch):
        monkeypatch.setattr("ai.data_collection.alpha_vantage_provider.settings.alpha_vantage_api_key", None)
        provider = AlphaVantageProvider()
        assert provider.health_check() is False


class TestDataCollectionManagerWiring:
    """Confirms the Facade wires providers correctly and that invalid input
    is rejected before any network call is attempted (SRS FR-1.4).
    """

    def test_default_provider_is_yahoo_finance(self):
        manager = DataCollectionManager()
        assert isinstance(manager.data_provider, YahooFinanceProvider)
        assert manager.data_provider.provider_name == "yahoo_finance"

    def test_alpha_vantage_can_be_injected(self):
        manager = DataCollectionManager(data_provider=AlphaVantageProvider())
        assert isinstance(manager.data_provider, AlphaVantageProvider)

    def test_invalid_ticker_rejected_before_network_call(self):
        manager = DataCollectionManager()
        with pytest.raises(ValidationError):
            manager.get_historical_prices("not a ticker", "2023-01-01", "2023-12-31", save=False)
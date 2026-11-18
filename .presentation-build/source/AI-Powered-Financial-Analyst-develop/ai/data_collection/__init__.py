"""
Data Collection (Module 1)
============================
Pulls historical OHLCV prices, company fundamentals, and financial news
from configurable providers and persists raw output to `datasets/raw/`.

Public API:
    from ai.data_collection import DataCollectionManager

    manager = DataCollectionManager()
    prices = manager.get_historical_prices("AAPL", "2023-01-01", "2023-12-31")
"""

from ai.data_collection.manager import DataCollectionManager

__all__ = ["DataCollectionManager"]
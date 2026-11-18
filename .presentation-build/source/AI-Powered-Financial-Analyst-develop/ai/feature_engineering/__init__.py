"""
ai/feature_engineering — Sprint 2: transforms cleaned raw OHLCV data
(ai/data_collection output) into a model-ready, feature-rich dataset for
Sprint 3+ (ML / Time Series / Deep Learning / Decision Support).

Public entry point: `FeatureEngineeringPipeline`.

    from ai.feature_engineering import FeatureEngineeringPipeline

    pipeline = FeatureEngineeringPipeline()
    result = pipeline.run(ticker="AAPL")
    result.dataframe  # the processed, feature-rich DataFrame
"""

from ai.feature_engineering.config import DEFAULT_CONFIG, FeatureEngineeringConfig
from ai.feature_engineering.exceptions import (
    FeatureComputationError,
    FeatureEngineeringError,
    InsufficientDataError,
    RawDataNotFoundError,
    SchemaValidationError,
    StorageError,
)
from ai.feature_engineering.pipeline import FeatureEngineeringPipeline, FeatureEngineeringResult

__all__ = [
    "FeatureEngineeringPipeline",
    "FeatureEngineeringResult",
    "FeatureEngineeringConfig",
    "DEFAULT_CONFIG",
    "FeatureEngineeringError",
    "RawDataNotFoundError",
    "SchemaValidationError",
    "InsufficientDataError",
    "FeatureComputationError",
    "StorageError",
]
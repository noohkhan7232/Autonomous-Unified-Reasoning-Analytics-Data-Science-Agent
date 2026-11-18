"""
`ai/feature_engineering/pipeline.py` — Sprint 2 orchestrator.

Single entry point (Facade + Pipeline pattern, mirroring
`ai.data_collection.manager.DataCollectionManager`): given a ticker (or an
already-loaded raw DataFrame), runs every Sprint 2 phase in order and
returns a `FeatureEngineeringResult` with the processed DataFrame and every
artifact path written to disk.
"""

import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import pandas as pd

from ai.feature_engineering import eda, storage
from ai.feature_engineering.config import DEFAULT_CONFIG, FeatureEngineeringConfig
from ai.feature_engineering.data_loader import load_raw_ohlcv
from ai.feature_engineering.features import build_generators
from ai.feature_engineering.features.base import FeatureDefinition
from ai.feature_engineering.preprocessing import clean_ohlcv
from ai.feature_engineering.selection import FeatureSelectionReport, analyze_features
from ai.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class FeatureEngineeringResult:
    ticker: str
    version: str
    dataframe: pd.DataFrame
    feature_definitions: list[FeatureDefinition]
    selection_report: FeatureSelectionReport
    eda_json_path: Path
    eda_md_path: Path
    processed_csv_path: Path
    metadata_json_path: Path
    summary_csv_path: Path
    feature_report_md_path: Path
    duration_seconds: float = 0.0
    rows_in: int = 0
    rows_out: int = 0
    columns_out: int = 0


class FeatureEngineeringPipeline:
    """Runs Phase 1 (EDA) -> Phase 2 (preprocessing) -> Phase 3+4 (feature
    generation) -> selection analysis -> storage, for a single ticker.
    """

    def __init__(self, config: FeatureEngineeringConfig = DEFAULT_CONFIG):
        self.config = config
        self.generators = build_generators(config)
        self.logger = logger

    def run(
        self,
        ticker: Optional[str] = None,
        raw_path: Optional[Path] = None,
        raw_df: Optional[pd.DataFrame] = None,
        version: Optional[str] = None,
    ) -> FeatureEngineeringResult:
        """Execute the full pipeline.

        Args:
            ticker: ticker to look up under `datasets/raw/` (ignored if `raw_df` given).
            raw_path: explicit raw CSV path (ignored if `raw_df` given).
            raw_df: an already-loaded raw OHLCV DataFrame (bypasses the loader entirely).
            version: run/version identifier for output filenames; defaults to a UTC timestamp.

        Returns:
            FeatureEngineeringResult with the processed DataFrame and every output path.
        """
        start = time.monotonic()
        version = version or datetime.now(timezone.utc).strftime("v%Y%m%dT%H%M%SZ")

        self.logger.info("Sprint 2 pipeline starting for ticker=%s version=%s", ticker, version)

        raw_df = raw_df if raw_df is not None else load_raw_ohlcv(ticker=ticker, path=raw_path)
        resolved_ticker = ticker or str(raw_df["ticker"].iloc[0])
        rows_in = len(raw_df)

        # --- Phase 2: preprocessing (also feeds the Phase 1 data-quality section) ---
        clean_df, cleaning_report = clean_ohlcv(raw_df)

        # --- Phase 1: EDA (profiles the raw data, annotated with what cleaning changed) ---
        eda_report = eda.profile_raw_data(raw_df, resolved_ticker, cleaning_report)
        eda_json_path, eda_md_path = eda.save_eda_report(eda_report)

        # --- Phase 3 + 4: feature generation ---
        feature_df = clean_df
        for generator in self.generators:
            feature_df = generator.generate(feature_df)

        if self.config.drop_warmup_nan_rows:
            before = len(feature_df)
            feature_df = feature_df.dropna().reset_index(drop=True)
            self.logger.info("drop_warmup_nan_rows: %d -> %d rows", before, len(feature_df))

        # --- Feature selection analysis (report-only, no columns dropped) ---
        selection_report = analyze_features(feature_df, self.config)

        # --- Metadata ---
        definitions = [d for gen in self.generators for d in gen.describe()]

        # --- Storage ---
        processed_csv_path = storage.save_processed_dataset(feature_df, resolved_ticker, version)
        metadata_json_path = storage.save_feature_metadata(definitions, resolved_ticker, version)
        summary_csv_path = storage.save_feature_summary_csv(feature_df, resolved_ticker, version)
        feature_report_md_path = storage.save_feature_report(definitions, selection_report, resolved_ticker, version)

        duration = time.monotonic() - start
        self.logger.info(
            "Sprint 2 pipeline finished for %s in %.2fs: %d rows -> %d rows, %d columns",
            resolved_ticker, duration, rows_in, len(feature_df), feature_df.shape[1],
        )

        return FeatureEngineeringResult(
            ticker=resolved_ticker,
            version=version,
            dataframe=feature_df,
            feature_definitions=definitions,
            selection_report=selection_report,
            eda_json_path=eda_json_path,
            eda_md_path=eda_md_path,
            processed_csv_path=processed_csv_path,
            metadata_json_path=metadata_json_path,
            summary_csv_path=summary_csv_path,
            feature_report_md_path=feature_report_md_path,
            duration_seconds=duration,
            rows_in=rows_in,
            rows_out=len(feature_df),
            columns_out=feature_df.shape[1],
        )
"""
Raw data loading for `ai/feature_engineering/`.

Reads the CSVs Sprint 1's `ai.data_collection.storage.save_ohlcv` writes to
`datasets/raw/{provider}_{ticker}_{start}_{end}_ohlcv.csv`, with columns
`date, open, high, low, close, volume` (see
`ai/data_collection/yahoo_finance_provider.py`). There is no `Adj Close` or
`Ticker` column in the actual Sprint 1 output — the ticker is only present in
the filename — so this loader adds a `ticker` column itself rather than
assuming it exists in the CSV.
"""

import re
from pathlib import Path
from typing import Optional

import pandas as pd

from ai.feature_engineering.exceptions import RawDataNotFoundError, SchemaValidationError
from ai.utils.config import settings
from ai.utils.logger import get_logger
from ai.utils.validators import validate_ticker

logger = get_logger(__name__)

REQUIRED_RAW_COLUMNS = ("date", "open", "high", "low", "close", "volume")

# Matches {provider}_{ticker}_{start}_{end}_ohlcv.csv, e.g.
# "yahoo_finance_AAPL_2023-01-01_2023-12-31_ohlcv.csv"
_RAW_OHLCV_FILENAME_RE = re.compile(
    r"^(?P<provider>[a-z_]+)_(?P<ticker>.+?)_(?P<start>\d{4}-\d{2}-\d{2})_(?P<end>\d{4}-\d{2}-\d{2})_ohlcv\.csv$"
)


def _raw_data_dir() -> Path:
    return settings.resolve(settings.raw_data_dir)


def find_raw_ohlcv_files(ticker: str) -> list[Path]:
    """Return every raw OHLCV file under `datasets/raw/` for `ticker`,
    across any provider/date range, sorted by end date (most recent last).
    """
    ticker = validate_ticker(ticker)
    raw_dir = _raw_data_dir()
    matches: list[tuple[str, Path]] = []
    if not raw_dir.exists():
        return []

    for path in raw_dir.glob("*_ohlcv.csv"):
        m = _RAW_OHLCV_FILENAME_RE.match(path.name)
        if m and m.group("ticker").upper() == ticker:
            matches.append((m.group("end"), path))

    matches.sort(key=lambda pair: pair[0])
    return [path for _, path in matches]


def latest_raw_ohlcv_path(ticker: str) -> Path:
    """Return the most recent raw OHLCV file for `ticker`.

    Raises:
        RawDataNotFoundError: no matching file exists under `datasets/raw/`.
    """
    files = find_raw_ohlcv_files(ticker)
    if not files:
        raise RawDataNotFoundError(ticker, _raw_data_dir())
    return files[-1]


def _validate_schema(df: pd.DataFrame, source: Path) -> None:
    missing = [c for c in REQUIRED_RAW_COLUMNS if c not in df.columns]
    if missing:
        raise SchemaValidationError(
            f"raw OHLCV file '{source}' is missing required column(s)", missing_columns=missing
        )


def load_raw_ohlcv(ticker: Optional[str] = None, path: Optional[Path] = None) -> pd.DataFrame:
    """Load a raw OHLCV CSV into a DataFrame, tagging it with a `ticker` column.

    Args:
        ticker: looked up via `find_raw_ohlcv_files` if `path` is not given
            (uses the most recent file for that ticker).
        path: an explicit CSV path, bypassing ticker lookup. Useful for
            scripts/tests that don't want to depend on `datasets/raw/` layout.

    Raises:
        ValueError: neither `ticker` nor `path` was provided.
        RawDataNotFoundError: no raw file found for `ticker`.
        SchemaValidationError: the CSV is missing required OHLCV columns.
    """
    if path is None and ticker is None:
        raise ValueError("load_raw_ohlcv requires either `ticker` or `path`")

    resolved_ticker = validate_ticker(ticker) if ticker else None
    source = Path(path) if path is not None else latest_raw_ohlcv_path(resolved_ticker)

    logger.info("Loading raw OHLCV data from %s", source)
    df = pd.read_csv(source)
    _validate_schema(df, source)

    if "ticker" not in df.columns:
        inferred_ticker = resolved_ticker
        if inferred_ticker is None:
            m = _RAW_OHLCV_FILENAME_RE.match(Path(source).name)
            inferred_ticker = m.group("ticker").upper() if m else "UNKNOWN"
        df["ticker"] = inferred_ticker

    logger.info("Loaded %d raw rows for %s from %s", len(df), df["ticker"].iloc[0] if len(df) else "?", source)
    return df
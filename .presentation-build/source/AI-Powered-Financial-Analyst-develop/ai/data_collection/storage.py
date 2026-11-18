"""
Persistence helpers for `ai/data_collection/`.

Satisfies SRS FR-1.3: raw pulled data is persisted to `datasets/raw/`,
keyed by provider + ticker + date range (or provider + query + date range
for news), for reproducibility. Writes are atomic (temp file + rename) so a
crash mid-write never leaves a corrupt file where downstream code (Feature
Engineering) expects a valid one.
"""

import json
import os
from pathlib import Path
from typing import Any, Union

import pandas as pd

from ai.data_collection.exceptions import StorageError
from ai.utils.config import settings
from ai.utils.logger import get_logger

logger = get_logger(__name__)


def _raw_data_dir() -> Path:
    path = settings.resolve(settings.raw_data_dir)
    path.mkdir(parents=True, exist_ok=True)
    return path


def _atomic_write(path: Path, write_fn) -> None:
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    try:
        write_fn(tmp_path)
        os.replace(tmp_path, path)
    except OSError as e:
        raise StorageError(f"failed writing '{path}': {e}")
    finally:
        if tmp_path.exists():
            try:
                tmp_path.unlink()
            except OSError:
                pass


def save_ohlcv(df: pd.DataFrame, provider: str, ticker: str, start: str, end: str) -> Path:
    """Save OHLCV data to datasets/raw/{provider}_{ticker}_{start}_{end}_ohlcv.csv"""
    filename = f"{provider}_{ticker}_{start}_{end}_ohlcv.csv"
    path = _raw_data_dir() / filename
    _atomic_write(path, lambda tmp: df.to_csv(tmp, index=False))
    logger.info("Saved %d OHLCV rows to %s", len(df), path)
    return path


def _write_json(tmp_path: Path, data: Union[dict, list]) -> None:
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, default=str)


def save_company_info(info: dict, provider: str, ticker: str) -> Path:
    """Save company info to datasets/raw/{provider}_{ticker}_company_info.json"""
    filename = f"{provider}_{ticker}_company_info.json"
    path = _raw_data_dir() / filename
    _atomic_write(path, lambda tmp: _write_json(tmp, info))
    logger.info("Saved company info to %s", path)
    return path


def save_news(articles: list[dict], provider: str, query: str, start: str = None, end: str = None) -> Path:
    """Save news articles to datasets/raw/{provider}_{query}_{start}_{end}_news.json
    (or datasets/raw/{provider}_{query}_latest_news.json if no date range given).
    """
    safe_query = query.replace(" ", "_")
    suffix = f"{start}_{end}" if (start and end) else "latest"
    filename = f"{provider}_{safe_query}_{suffix}_news.json"
    path = _raw_data_dir() / filename
    _atomic_write(path, lambda tmp: _write_json(tmp, articles))
    logger.info("Saved %d news article(s) to %s", len(articles), path)
    return path
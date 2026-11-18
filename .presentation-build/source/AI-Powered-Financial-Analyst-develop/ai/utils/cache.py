"""
Simple, dependency-free, TTL-based file cache backed by `storage/cache/`
(see storage/README.md). Used by rate-limited providers (NewsAPI, Alpha
Vantage) to avoid re-spending quota on repeated identical requests during
development.
"""

import hashlib
import json
import time
from pathlib import Path
from typing import Any, Optional

from ai.utils.config import settings
from ai.utils.logger import get_logger

logger = get_logger(__name__)


class FileCache:
    """A namespaced, TTL-based cache backed by JSON files under storage/cache/<namespace>/."""

    def __init__(self, namespace: str, ttl_seconds: Optional[int] = None):
        self.namespace = namespace
        self.ttl_seconds = ttl_seconds if ttl_seconds is not None else settings.cache_ttl_seconds
        self.dir_path: Path = settings.resolve(settings.cache_dir, namespace)
        self.dir_path.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def make_key(**kwargs: Any) -> str:
        raw = json.dumps(kwargs, sort_keys=True, default=str)
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:24]

    def _path_for(self, key: str) -> Path:
        return self.dir_path / f"{key}.json"

    def get(self, key: str) -> Optional[Any]:
        path = self._path_for(key)
        if not path.exists():
            return None
        try:
            with open(path, "r", encoding="utf-8") as f:
                envelope = json.load(f)
        except (json.JSONDecodeError, OSError) as e:
            logger.warning("Cache file '%s' is unreadable (%s); ignoring.", path, e)
            return None

        if time.time() - envelope.get("cached_at", 0) > self.ttl_seconds:
            return None
        return envelope.get("value")

    def set(self, key: str, value: Any) -> None:
        path = self._path_for(key)
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump({"cached_at": time.time(), "value": value}, f)
        except (OSError, TypeError) as e:
            # Caching is a best-effort optimization; never let a write
            # failure break the actual data collection flow.
            logger.warning("Failed to write cache entry '%s': %s", path, e)

    def clear(self) -> int:
        removed = 0
        for file in self.dir_path.glob("*.json"):
            try:
                file.unlink()
                removed += 1
            except OSError as e:
                logger.warning("Could not remove cache file '%s': %s", file, e)
        return removed
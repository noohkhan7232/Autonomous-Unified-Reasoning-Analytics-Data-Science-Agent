"""
Centralized logging setup for the `ai/` package.

Every module under `ai/` gets its logger via `get_logger(__name__)` instead
of calling `logging.getLogger` directly, so log format, level, and handlers
(console + rotating file under `storage/logs/`) stay consistent everywhere
and are configured exactly once.
"""

import logging
import sys
from logging.handlers import RotatingFileHandler

from ai.utils.config import settings

_LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

_configured = False


def _configure_root_logger() -> None:
    global _configured
    if _configured:
        return

    root = logging.getLogger("ai")
    root.setLevel(settings.log_level)
    root.propagate = False

    formatter = logging.Formatter(_LOG_FORMAT, datefmt=_DATE_FORMAT)

    console_handler = logging.StreamHandler(stream=sys.stdout)
    console_handler.setFormatter(formatter)
    root.addHandler(console_handler)

    try:
        log_dir = settings.resolve(settings.log_dir)
        log_dir.mkdir(parents=True, exist_ok=True)
        file_handler = RotatingFileHandler(
            filename=str(log_dir / "ai.log"),
            maxBytes=5_242_880,  # 5 MB
            backupCount=5,
            encoding="utf-8",
        )
        file_handler.setFormatter(formatter)
        root.addHandler(file_handler)
    except OSError as e:
        root.warning("Could not attach file log handler (%s). Logging to console only.", e)

    _configured = True


def get_logger(name: str) -> logging.Logger:
    """Return a namespaced logger, e.g. get_logger(__name__), that inherits
    the shared console + rotating-file handlers configured on the 'ai' logger.
    """
    _configure_root_logger()
    return logging.getLogger(f"ai.{name}" if not name.startswith("ai.") else name)
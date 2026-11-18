"""
Reusable retry-with-exponential-backoff decorator, used by any `ai/` module
that makes network calls (Data Collection providers today; future modules
calling external LLM/NLP APIs can reuse it too).
"""

import time
from functools import wraps
from typing import Callable, Tuple, Type, TypeVar

from ai.utils.config import settings
from ai.utils.logger import get_logger

logger = get_logger(__name__)

F = TypeVar("F", bound=Callable)


def retry_with_backoff(
    exceptions: Tuple[Type[BaseException], ...] = (Exception,),
    *,
    max_retries: int | None = None,
    backoff_factor: float | None = None,
) -> Callable[[F], F]:
    """Retry the decorated function with exponential backoff on the given
    exception types. Any other exception propagates immediately.

    Delay before attempt N (N > 1) is `backoff_factor * 2 ** (N - 2)` seconds.
    Defaults come from `settings.request_max_retries` / `request_backoff_factor`.
    """
    resolved_max_retries = max_retries if max_retries is not None else settings.request_max_retries
    resolved_backoff = backoff_factor if backoff_factor is not None else settings.request_backoff_factor

    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args, **kwargs):
            attempt = 1
            while True:
                try:
                    return func(*args, **kwargs)
                except exceptions as exc:
                    if attempt > resolved_max_retries:
                        logger.error("'%s' failed after %d attempt(s): %s", func.__name__, attempt, exc)
                        raise

                    retry_after = getattr(exc, "retry_after_seconds", None)
                    delay = float(retry_after) if retry_after else resolved_backoff * (2 ** (attempt - 1))

                    logger.warning(
                        "'%s' raised %s (attempt %d/%d). Retrying in %.1fs...",
                        func.__name__, exc.__class__.__name__, attempt, resolved_max_retries, delay,
                    )
                    time.sleep(delay)
                    attempt += 1

        return wrapper  # type: ignore[return-value]

    return decorator
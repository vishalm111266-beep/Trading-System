"""Retry logic for data operations."""

from __future__ import annotations

import logging
import time
from collections.abc import Callable
from functools import wraps
from typing import Any

from trading_system.data.exceptions import DataSourceError

logger = logging.getLogger(__name__)


class RetryExhausted(DataSourceError):
    """Raised when all retry attempts are spent."""


def with_retry[F: Callable[..., Any]](
    func: F,
    *,
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
) -> F:
    """Wrap *func* with exponential-backoff retry on ``DataSourceError``."""
    if max_attempts < 1:
        msg = "max_attempts must be >= 1"
        raise ValueError(msg)

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        attempt = 0
        current_delay = delay
        last_exc: DataSourceError | None = None
        while attempt < max_attempts:
            try:
                return func(*args, **kwargs)
            except DataSourceError as exc:
                last_exc = exc
                attempt += 1
                if attempt < max_attempts:
                    logger.debug(
                        "attempt %d/%d failed, retrying in %.1fs",
                        attempt,
                        max_attempts,
                        current_delay,
                    )
                    time.sleep(current_delay)
                    current_delay *= backoff
        raise RetryExhausted(
            f"failed after {max_attempts} attempts"
        ) from last_exc

    return wrapper  # type: ignore[return-value]

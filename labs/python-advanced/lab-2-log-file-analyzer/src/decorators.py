"""Decorators: @timer, @log_call, and lru_cache alias."""

import functools
import logging
import time
from collections.abc import Callable
from typing import Any, TypeVar

logger = logging.getLogger(__name__)

F = TypeVar("F", bound=Callable[..., Any])


def timer(fn: F) -> F:
    """Measure and log wall-clock execution time of *fn*."""
    @functools.wraps(fn)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        t0 = time.perf_counter()
        result = fn(*args, **kwargs)
        elapsed = time.perf_counter() - t0
        logger.info("[timer] %s finished in %.4fs", fn.__qualname__, elapsed)
        return result
    return wrapper  # type: ignore[return-value]


def log_call(fn: F) -> F:
    """Trace every call to *fn* with its arguments."""
    @functools.wraps(fn)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        logger.debug("[call] %s args=%s kwargs=%s", fn.__qualname__, args, kwargs)
        result = fn(*args, **kwargs)
        logger.debug("[return] %s -> %r", fn.__qualname__, result)
        return result
    return wrapper  # type: ignore[return-value]


# Convenience re-export so callers can do: from src.decorators import cache
cache = functools.lru_cache

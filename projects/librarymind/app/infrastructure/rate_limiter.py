"""Token-bucket rate limiter and its exception, re-exported from app.exceptions."""

import threading
import time
import logging

from app.exceptions import RateLimitError  # noqa: F401  (re-exported for callers)

logger = logging.getLogger(__name__)


class RateLimiter:
    """Thread-safe token-bucket rate limiter.

    Tokens are added continuously at ``requests_per_minute / 60`` per
    second, up to a maximum of ``requests_per_minute``.  Each call to
    :meth:`acquire` consumes one token.  If no token is available the
    call raises :class:`~app.exceptions.RateLimitError` immediately
    (non-blocking).

    Args:
        requests_per_minute: Maximum sustained request rate.

    Example:
        >>> limiter = RateLimiter(requests_per_minute=20)
        >>> limiter.acquire()   # succeeds
        >>> # exhaust the bucket, then:
        >>> limiter.acquire()   # raises RateLimitError
    """

    def __init__(self, requests_per_minute: int) -> None:
        self.capacity    = float(requests_per_minute)
        self.tokens      = float(requests_per_minute)
        self.refill_rate = requests_per_minute / 60.0   # tokens per second
        self.last_refill = time.time()
        self.lock        = threading.Lock()

    def _refill(self) -> None:
        """Add tokens proportional to elapsed time since last refill.

        Must be called while ``self.lock`` is held.
        """
        now     = time.time()
        elapsed = now - self.last_refill
        self.tokens      = min(self.capacity,
                               self.tokens + elapsed * self.refill_rate)
        self.last_refill = now

    def acquire(self) -> None:
        """Consume one token, blocking on lock but not on capacity.

        Refills the bucket based on elapsed time, then either removes
        one token (success) or raises immediately (bucket empty).

        Raises:
            RateLimitError: When no tokens are available.
        """
        with self.lock:
            self._refill()
            if self.tokens >= 1.0:
                self.tokens -= 1.0
                logger.debug(
                    f"Rate limiter: token acquired. "
                    f"Remaining: {self.tokens:.1f}"
                )
            else:
                raise RateLimitError(
                    "Rate limit exceeded. "
                    "Please wait before making another request."
                )

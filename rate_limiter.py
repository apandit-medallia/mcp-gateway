import asyncio
from enum import Enum
from time import monotonic


class RateLimitMode(str, Enum):
    REJECT = "reject"
    WAIT = "wait"


class RateLimiter:
    """
    Simple fixed-window rate limiter.

    Example:
        RateLimiter(
            max_requests=5,
            window_seconds=10,
            mode=RateLimitMode.REJECT
        )
    """

    def __init__(
        self,
        max_requests: int,
        window_seconds: int,
        mode: RateLimitMode = RateLimitMode.REJECT,
    ):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.mode = mode

        self.window_start = monotonic()
        self.request_count = 0

        self._lock = asyncio.Lock()

    async def check_rate_limit(self) -> bool:
        """
        Returns:
            True  -> request may continue
            False -> request should be rejected
        """

        async with self._lock:

            now = monotonic()

            # New window?
            if now - self.window_start >= self.window_seconds:
                self.window_start = now
                self.request_count = 0

            # Still capacity
            if self.request_count < self.max_requests:
                self.request_count += 1
                return False

            # Reject immediately
            if self.mode == RateLimitMode.REJECT:
                return True

            # Wait until window resets
            sleep_time = self.window_seconds - (now - self.window_start)

        # Don't hold the lock while sleeping
        if sleep_time > 0:
            await asyncio.sleep(sleep_time)

        async with self._lock:
            self.window_start = monotonic()
            self.request_count = 1

        return False

    @property
    def remaining(self):
        return max(0, self.max_requests - self.request_count)

    @property
    def reset_in(self):
        return max(
            0,
            self.window_seconds - (monotonic() - self.window_start),
        )

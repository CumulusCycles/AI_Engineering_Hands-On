"""In-process sliding-window rate limiter for auth endpoints."""

from __future__ import annotations

import time
from collections import defaultdict
from threading import Lock

from fastapi import HTTPException, Request, status


class _SlidingWindowCounter:
    """Per-key sliding window rate limiter (thread-safe, in-process)."""

    def __init__(self) -> None:
        self._lock = Lock()
        self._hits: dict[str, list[float]] = defaultdict(list)

    def is_allowed(self, key: str, max_requests: int, window_seconds: int) -> bool:
        now = time.monotonic()
        cutoff = now - window_seconds
        with self._lock:
            timestamps = self._hits[key]
            # Prune expired entries
            self._hits[key] = [t for t in timestamps if t > cutoff]
            if len(self._hits[key]) >= max_requests:
                return False
            self._hits[key].append(now)
            return True

    def reset(self) -> None:
        with self._lock:
            self._hits.clear()


_counter = _SlidingWindowCounter()


def _parse_rate_limit(spec: str) -> tuple[int, int]:
    """Parse '5/minute' into (max_requests=5, window_seconds=60)."""
    parts = spec.strip().split("/")
    if len(parts) != 2:
        raise ValueError(f"Invalid rate limit spec: {spec!r}")
    count = int(parts[0])
    unit = parts[1].lower().strip()
    unit_map = {"second": 1, "minute": 60, "hour": 3600, "day": 86400}
    if unit not in unit_map:
        raise ValueError(f"Unknown rate limit unit: {unit!r}")
    return count, unit_map[unit]


def _client_ip(request: Request) -> str:
    """Extract client IP for rate-limit keying."""
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    client = request.client
    return client.host if client else "unknown"


def check_rate_limit(request: Request, rate_limit_spec: str) -> None:
    """Raise 429 if the client IP has exceeded the configured rate limit."""
    max_requests, window_seconds = _parse_rate_limit(rate_limit_spec)
    key = _client_ip(request)
    if not _counter.is_allowed(key, max_requests, window_seconds):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Try again later.",
            headers={"Retry-After": str(window_seconds)},
        )


def reset_rate_limiter() -> None:
    """Clear all rate-limit state (for test isolation)."""
    _counter.reset()

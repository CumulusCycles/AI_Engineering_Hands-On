from __future__ import annotations

import logging
from collections.abc import Callable
from time import perf_counter
from typing import TypeVar

from openai import APIConnectionError, APIStatusError, OpenAIError

logger = logging.getLogger(__name__)

T = TypeVar("T")

# HTTP statuses we treat as worth one extra attempt.
_TRANSIENT_HTTP_STATUSES: frozenset[int] = frozenset({408, 425, 429, 500, 502, 503, 504})


def is_transient_openai_error(exc: BaseException) -> bool:
    """Return True if the exception is a retryable OpenAI network or HTTP error."""

    if isinstance(exc, APIConnectionError):
        return True
    if isinstance(exc, APIStatusError):
        return exc.status_code in _TRANSIENT_HTTP_STATUSES
    return False


def call_with_transient_retry(
    operation: Callable[[], T],
    *,
    max_attempts: int,
    after_attempt: Callable[[int, float, BaseException | None, T | None], None] | None = None,
) -> tuple[T, int]:
    """Retry an OpenAI call on transient errors, returning (result, attempts_used)."""

    if max_attempts < 1:
        msg = "max_attempts must be >= 1"
        raise ValueError(msg)

    for attempt in range(1, max_attempts + 1):
        t0 = perf_counter()
        try:
            result = operation()
            elapsed_ms = (perf_counter() - t0) * 1000
            if after_attempt is not None:
                after_attempt(attempt, elapsed_ms, None, result)
            return result, attempt
        except OpenAIError as exc:
            elapsed_ms = (perf_counter() - t0) * 1000
            if after_attempt is not None:
                after_attempt(attempt, elapsed_ms, exc, None)
            if attempt >= max_attempts or not is_transient_openai_error(exc):
                raise
            logger.warning(
                "OpenAI transient error (attempt %s/%s), retrying: %s",
                attempt,
                max_attempts,
                exc,
            )
    raise AssertionError("call_with_transient_retry: unreachable")  # pragma: no cover

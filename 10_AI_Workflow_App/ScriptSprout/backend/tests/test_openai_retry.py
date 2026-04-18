"""Transient OpenAI retry helper."""

from __future__ import annotations

from unittest.mock import MagicMock

import httpx
import pytest
from openai import (
    APIConnectionError,
    BadRequestError,
    InternalServerError,
    OpenAIError,
    RateLimitError,
)

from app.services.openai_retry import call_with_transient_retry, is_transient_openai_error


def _resp(status: int) -> httpx.Response:
    req = httpx.Request("POST", "https://api.openai.com/v1/responses")
    return httpx.Response(status, request=req)


def test_is_transient_connection() -> None:
    req = httpx.Request("POST", "https://api.openai.com/x")
    assert is_transient_openai_error(APIConnectionError(message="x", request=req)) is True


def test_is_transient_429_and_500() -> None:
    r429 = _resp(429)
    assert is_transient_openai_error(RateLimitError("rl", response=r429, body=None)) is True
    r500 = _resp(500)
    assert is_transient_openai_error(InternalServerError("ise", response=r500, body=None)) is True


def test_not_transient_400() -> None:
    r400 = _resp(400)
    assert is_transient_openai_error(BadRequestError("bad", response=r400, body=None)) is False


def test_after_attempt_callback_per_try() -> None:
    events: list[tuple[int, bool]] = []

    def after(a: int, _ms: float, exc: BaseException | None, res: str | None) -> None:
        events.append((a, exc is None and res is not None))

    def flaky() -> str:
        if len(events) == 0:
            raise RateLimitError("once", response=_resp(429), body=None)
        return "ok"

    result, attempt = call_with_transient_retry(
        flaky,
        max_attempts=2,
        after_attempt=after,
    )
    assert result == "ok"
    assert attempt == 2
    assert events == [(1, False), (2, True)]


def test_retry_succeeds_second_attempt() -> None:
    calls: list[int] = []

    def flaky() -> str:
        calls.append(1)
        if len(calls) == 1:
            raise RateLimitError("once", response=_resp(429), body=None)
        return "ok"

    result, attempt = call_with_transient_retry(flaky, max_attempts=2)
    assert result == "ok"
    assert attempt == 2
    assert len(calls) == 2


def test_no_retry_on_bad_request() -> None:
    def bad() -> str:
        raise BadRequestError("nope", response=_resp(400), body=None)

    with pytest.raises(BadRequestError):
        call_with_transient_retry(bad, max_attempts=2)


def test_exhausts_attempts_on_persistent_503() -> None:
    count = 0

    def always_503() -> str:
        nonlocal count
        count += 1
        raise InternalServerError("x", response=_resp(503), body=None)

    with pytest.raises(InternalServerError):
        call_with_transient_retry(always_503, max_attempts=2)
    assert count == 2


def test_max_attempts_one_no_retry() -> None:
    calls = 0

    def once_429() -> str:
        nonlocal calls
        calls += 1
        raise RateLimitError("rl", response=_resp(429), body=None)

    with pytest.raises(RateLimitError):
        call_with_transient_retry(once_429, max_attempts=1)
    assert calls == 1


def test_max_attempts_invalid() -> None:
    with pytest.raises(ValueError, match="max_attempts"):
        call_with_transient_retry(MagicMock(return_value=1), max_attempts=0)


def test_generic_openai_error_not_retried() -> None:
    class Weird(OpenAIError):
        pass

    def boom() -> str:
        raise Weird("weird")

    with pytest.raises(Weird):
        call_with_transient_retry(boom, max_attempts=2)

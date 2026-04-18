"""Unit tests for ``openai_route_errors`` (503 client + 502 exception mapping)."""

from __future__ import annotations

import logging
from unittest.mock import MagicMock, patch

import httpx
import pytest
from fastapi import status
from openai import APIConnectionError, APIStatusError, InternalServerError, OpenAIError

from app.api.openai_route_errors import (
    OPENAI_ROUTE_SDK_EXCEPTIONS,
    ensure_openai_client,
    http_exception_from_openai_route_error,
)


class _BareOpenAIError(OpenAIError):
    """Subclass that is :class:`OpenAIError` but not :class:`APIStatusError` / connection."""

    pass


def _httpx_resp(code: int) -> httpx.Response:
    """Build a minimal :class:`httpx.Response` for OpenAI SDK error constructors.

    Args:
        code: HTTP status code.

    Returns:
        Response with a synthetic request attached.
    """

    req = httpx.Request("POST", "https://api.openai.com/v1/test")
    return httpx.Response(code, request=req)


def test_openai_route_sdk_exceptions_tuple() -> None:
    """Exported tuple includes runtime + SDK base types used by routes."""

    assert RuntimeError in OPENAI_ROUTE_SDK_EXCEPTIONS
    assert APIStatusError in OPENAI_ROUTE_SDK_EXCEPTIONS
    assert APIConnectionError in OPENAI_ROUTE_SDK_EXCEPTIONS
    assert OpenAIError in OPENAI_ROUTE_SDK_EXCEPTIONS
    assert len(OPENAI_ROUTE_SDK_EXCEPTIONS) == 4


def test_ensure_openai_client_returns_client() -> None:
    """When ``build_openai_client`` succeeds, return its value."""

    mock_client = MagicMock()
    with patch(
        "app.api.openai_route_errors.build_openai_client",
        return_value=mock_client,
    ):
        out = ensure_openai_client(MagicMock())
    assert out is mock_client


def test_ensure_openai_client_503_when_value_error() -> None:
    """Missing/invalid key path surfaces **503** with stable ``detail``."""

    with patch(
        "app.api.openai_route_errors.build_openai_client",
        side_effect=ValueError("OpenAI API key is not configured"),
    ):
        with pytest.raises(Exception) as ei:
            ensure_openai_client(MagicMock())
    exc = ei.value
    assert exc.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
    assert exc.detail == "OpenAI API key not configured"


def test_http_maps_runtime_error_to_502_detail_from_message() -> None:
    """``RuntimeError`` uses ``str(exc)`` when ``runtime_error_detail`` is omitted."""

    he = http_exception_from_openai_route_error(RuntimeError("embed failed"))
    assert he.status_code == status.HTTP_502_BAD_GATEWAY
    assert he.detail == "embed failed"


def test_http_maps_runtime_error_fixed_detail_and_logs_warning() -> None:
    """Optional fixed detail and warning when ``logger`` is passed."""

    log = MagicMock(spec=logging.Logger)
    he = http_exception_from_openai_route_error(
        RuntimeError("raw"),
        logger=log,
        log_context="nlp",
        runtime_error_detail="Could not parse structured parameters from model output",
    )
    assert he.detail == "Could not parse structured parameters from model output"
    log.warning.assert_called_once()


def test_http_maps_api_status_error_to_502() -> None:
    """``APIStatusError`` subclasses map to generic OpenAI failure copy."""

    err = InternalServerError("upstream", response=_httpx_resp(500), body=None)
    he = http_exception_from_openai_route_error(err)
    assert he.status_code == status.HTTP_502_BAD_GATEWAY
    assert he.detail == "OpenAI request failed"


def test_http_maps_api_status_error_logs_warning() -> None:
    """Status errors optionally emit a warning with context prefix."""

    log = MagicMock(spec=logging.Logger)
    err = InternalServerError("x", response=_httpx_resp(502), body=None)
    http_exception_from_openai_route_error(err, logger=log, log_context="smoke")
    log.warning.assert_called_once()
    args = log.warning.call_args[0]
    assert "smoke" in args[0] or "smoke" in str(args)


def test_http_maps_connection_error_to_unreachable() -> None:
    """Connection failures use the unreachable client message."""

    req = httpx.Request("POST", "https://api.openai.com/x")
    err = APIConnectionError(message="timeout", request=req)
    he = http_exception_from_openai_route_error(err)
    assert he.status_code == status.HTTP_502_BAD_GATEWAY
    assert he.detail == "OpenAI unreachable"


def test_http_maps_openai_error_logs_exception() -> None:
    """Generic ``OpenAIError`` uses **502** and may call ``logger.exception``."""

    log = MagicMock(spec=logging.Logger)
    err = _BareOpenAIError("bare")
    he = http_exception_from_openai_route_error(
        err,
        logger=log,
        openai_error_log_message="unit_test_openai_fail",
    )
    assert he.detail == "OpenAI request failed"
    log.exception.assert_called_once_with("unit_test_openai_fail")


def test_http_openai_error_logger_falls_back_message() -> None:
    """Without ``openai_error_log_message``, logger uses ``log_context`` then default."""

    log = MagicMock(spec=logging.Logger)
    err = _BareOpenAIError("bare")
    http_exception_from_openai_route_error(err, logger=log, log_context="my_route")
    log.exception.assert_called_once_with("my_route")


def test_http_unhandled_type_raises_type_error() -> None:
    """Unsupported exception types surface ``TypeError`` for fast failure."""

    with pytest.raises(TypeError, match="unhandled exception type"):
        http_exception_from_openai_route_error(ValueError("not mapped"))

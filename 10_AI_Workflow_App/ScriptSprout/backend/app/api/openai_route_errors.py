"""Map OpenAI SDK and service :class:`RuntimeError` failures to FastAPI :class:`HTTPException`."""

from __future__ import annotations

import logging

from fastapi import HTTPException, status
from openai import APIConnectionError, APIStatusError, OpenAI, OpenAIError

from app.config import Settings
from app.services.openai_client import build_openai_client

# Tuple for ``except`` clauses on routes that call OpenAI-backed services.
OPENAI_ROUTE_SDK_EXCEPTIONS: tuple[type[BaseException], ...] = (
    RuntimeError,
    APIStatusError,
    APIConnectionError,
    OpenAIError,
)


def ensure_openai_client(settings: Settings) -> OpenAI:
    """Build an OpenAI client or raise 503 if the API key is not configured."""

    try:
        return build_openai_client(settings)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="OpenAI API key not configured",
        ) from None


def http_exception_from_openai_route_error(
    exc: BaseException,
    *,
    logger: logging.Logger | None = None,
    log_context: str | None = None,
    runtime_error_detail: str | None = None,
    openai_error_log_message: str | None = None,
) -> HTTPException:
    """Convert an OpenAI SDK or RuntimeError exception into an appropriate HTTPException."""

    prefix = f"{log_context}: " if log_context else ""

    if isinstance(exc, RuntimeError):
        detail = runtime_error_detail if runtime_error_detail is not None else str(exc)
        if logger is not None:
            logger.warning("%s%s", prefix, exc)
        return HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=detail)

    if isinstance(exc, APIStatusError):
        if logger is not None:
            logger.warning(
                "%sAPIStatusError status=%s",
                prefix,
                getattr(exc, "status_code", None),
            )
        return HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="OpenAI request failed",
        )

    if isinstance(exc, APIConnectionError):
        return HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="OpenAI unreachable",
        )

    if isinstance(exc, OpenAIError):
        if logger is not None:
            msg = openai_error_log_message or log_context or "OpenAI request failed"
            logger.exception(msg)
        return HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="OpenAI request failed",
        )

    msg = f"unhandled exception type for OpenAI route mapping: {type(exc)!r}"
    raise TypeError(msg)

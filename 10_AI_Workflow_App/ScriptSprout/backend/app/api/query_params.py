"""Shared normalization for optional string query parameters (OpenAPI + handlers)."""

from __future__ import annotations

# OpenAPI text for optional ``status`` filters on content list endpoints (author + admin).
OPTIONAL_STATUS_QUERY_DESCRIPTION = (
    "Workflow status filter. Whitespace is trimmed; empty or whitespace-only values are treated "
    "as no filter."
)


def normalize_optional_query_str(value: str | None) -> str | None:
    """Normalize input into canonical application format.

    Args:
        value: Input value used to perform this operation.

    Returns:
        Result generated for the caller.

    """

    if value is None:
        return None
    stripped = value.strip()
    return stripped if stripped else None

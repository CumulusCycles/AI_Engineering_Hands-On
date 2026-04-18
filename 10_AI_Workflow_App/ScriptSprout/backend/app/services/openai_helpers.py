"""Shared helpers for OpenAI response handling."""

from __future__ import annotations

from typing import Any


def usage_tokens(resp: Any) -> tuple[int | None, int | None]:
    """Extract input and output token counts from an OpenAI response.

    Returns (None, None) when usage data is unavailable.
    """

    u = getattr(resp, "usage", None)
    if u is None:
        return None, None
    ti = getattr(u, "input_tokens", None)
    to = getattr(u, "output_tokens", None)
    if not isinstance(ti, int):
        ti = None
    if not isinstance(to, int):
        to = None
    return ti, to

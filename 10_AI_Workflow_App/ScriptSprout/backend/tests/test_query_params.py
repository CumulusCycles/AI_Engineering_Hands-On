"""Tests for :mod:`app.api.query_params` optional string normalization."""

from __future__ import annotations

from app.api.query_params import normalize_optional_query_str


def test_normalize_optional_query_str_none() -> None:
    assert normalize_optional_query_str(None) is None


def test_normalize_optional_query_str_empty_and_whitespace() -> None:
    assert normalize_optional_query_str("") is None
    assert normalize_optional_query_str("   ") is None
    assert normalize_optional_query_str("\t\n") is None


def test_normalize_optional_query_str_strips_and_keeps() -> None:
    assert normalize_optional_query_str("  draft  ") == "draft"
    assert normalize_optional_query_str("ready") == "ready"

"""Deterministic follow-up prompts."""

from __future__ import annotations

from app.services.missing_field_follow_up import build_missing_field_follow_ups


def test_follow_up_order_and_kinds() -> None:
    rows = build_missing_field_follow_ups(
        ["video_length_minutes", "subject", "genre"],
    )
    assert [r.field for r in rows] == ["subject", "genre", "video_length_minutes"]
    assert rows[0].input_kind == "text"
    assert rows[1].input_kind == "single_select"
    assert rows[1].suggested_options is not None
    assert rows[2].input_kind == "number"


def test_follow_up_empty() -> None:
    assert build_missing_field_follow_ups([]) == []

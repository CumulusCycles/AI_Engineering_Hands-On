"""Unit tests for :func:`app.api.deps.get_owned_content_or_404`."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException, status

from app.api.deps import get_owned_content_or_404


def test_get_owned_content_or_404_returns_row_for_owner(monkeypatch: pytest.MonkeyPatch) -> None:
    """When the row exists and ``author_id`` matches, return the ORM instance."""

    user = MagicMock()
    user.id = 7
    row = MagicMock()
    row.author_id = 7

    monkeypatch.setattr(
        "app.api.deps.get_content_item_by_id",
        lambda _db, cid: row if cid == 42 else None,
    )

    out = get_owned_content_or_404(content_id=42, user=user, db=MagicMock())
    assert out is row


def test_get_owned_content_or_404_404_when_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    """Missing primary key yields **404** with a stable message (no leak)."""

    monkeypatch.setattr("app.api.deps.get_content_item_by_id", lambda _db, _cid: None)

    with pytest.raises(HTTPException) as ei:
        get_owned_content_or_404(content_id=99, user=MagicMock(id=1), db=MagicMock())

    assert ei.value.status_code == status.HTTP_404_NOT_FOUND
    assert ei.value.detail == "Content not found"


def test_get_owned_content_or_404_404_when_other_author(monkeypatch: pytest.MonkeyPatch) -> None:
    """Existing row owned by another user is treated like **404** for the caller."""

    row = MagicMock()
    row.author_id = 2
    monkeypatch.setattr("app.api.deps.get_content_item_by_id", lambda _db, _cid: row)

    user = MagicMock()
    user.id = 9

    with pytest.raises(HTTPException) as ei:
        get_owned_content_or_404(content_id=1, user=user, db=MagicMock())

    assert ei.value.status_code == status.HTTP_404_NOT_FOUND
    assert ei.value.detail == "Content not found"

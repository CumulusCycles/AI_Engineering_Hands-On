"""Serve thumbnail and audio BLOBs (author-only GET)."""

from __future__ import annotations

from fastapi.testclient import TestClient


def _register_login(client: TestClient, username: str, password: str) -> None:
    r = client.post("/api/auth/register", json={"username": username, "password": password})
    assert r.status_code == 201
    r2 = client.post("/api/auth/login", json={"username": username, "password": password})
    assert r2.status_code == 200


def test_get_thumbnail_and_audio_when_present(client: TestClient) -> None:
    _register_login(client, "media_author_a", "Password123")
    create = client.post(
        "/api/content/",
        json={"prompt": "A short tale", "genre": "fantasy"},
    )
    assert create.status_code == 201
    cid = create.json()["id"]

    from app.db.models import ContentItem

    SessionLocal = client.app.state.SessionLocal
    with SessionLocal() as db:
        row = db.get(ContentItem, cid)
        assert row is not None
        row.thumbnail_blob = b"\x89PNG\r\n\x1a\n\x00"
        row.thumbnail_mime_type = "image/png"
        row.audio_blob = b"ID3fake"
        row.audio_mime_type = "audio/mpeg"
        db.commit()

    r_thumb = client.get(f"/api/content/{cid}/thumbnail")
    assert r_thumb.status_code == 200
    assert r_thumb.headers["content-type"].startswith("image/png")
    assert r_thumb.content == b"\x89PNG\r\n\x1a\n\x00"

    r_audio = client.get(f"/api/content/{cid}/audio")
    assert r_audio.status_code == 200
    assert r_audio.headers["content-type"].startswith("audio/mpeg")
    assert r_audio.content == b"ID3fake"


def test_get_thumbnail_404_when_missing(client: TestClient) -> None:
    _register_login(client, "media_author_b", "Password123")
    create = client.post("/api/content/", json={"prompt": "x"})
    assert create.status_code == 201
    cid = create.json()["id"]
    r = client.get(f"/api/content/{cid}/thumbnail")
    assert r.status_code == 404


def test_get_media_not_found_for_other_author(client: TestClient) -> None:
    _register_login(client, "media_owner", "Password123")
    create = client.post("/api/content/", json={"prompt": "owned"})
    assert create.status_code == 201
    cid = create.json()["id"]
    SessionLocal = client.app.state.SessionLocal
    from app.db.models import ContentItem

    with SessionLocal() as db:
        row = db.get(ContentItem, cid)
        assert row is not None
        row.thumbnail_blob = b"x"
        row.thumbnail_mime_type = "image/png"
        db.commit()

    client.post("/api/auth/logout")
    _register_login(client, "media_stranger", "Password456")

    r = client.get(f"/api/content/{cid}/thumbnail")
    assert r.status_code == 404

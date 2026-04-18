"""Thumbnail generation workflow (mocked OpenAI Images API)."""

from __future__ import annotations

import base64
from io import BytesIO
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient
from PIL import Image
from sqlalchemy import select

from app.db.models import AuditEvent, ContentItem, ModelCall


def _register_login_author(ac: TestClient, username: str, password: str) -> None:
    r = ac.post("/api/auth/register", json={"username": username, "password": password})
    assert r.status_code == 201
    r2 = ac.post("/api/auth/login", json={"username": username, "password": password})
    assert r2.status_code == 200


def _seed_story_and_pass(application, content_id: int) -> None:
    SessionLocal = application.state.SessionLocal
    with SessionLocal() as db:
        row = db.get(ContentItem, content_id)
        assert row is not None
        row.synopsis = "Approved synopsis."
        row.title = "A Shy Astronaut"
        row.description = "A gentle description for a short narration."
        row.story_text = "Once upon a time, a shy astronaut listened to the stars."
        row.guardrails_enabled = True
        row.status = "guardrails_passed"
        db.commit()


def test_generate_thumbnail_persists_blob_and_tracks_events(
    monkeypatch,
    tmp_path,
) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test-dummy-key-for-pytest")
    monkeypatch.setenv("SQLITE_PATH", str(tmp_path / "test.db"))
    monkeypatch.setenv("CHROMA_PATH", str(tmp_path / "chroma"))
    monkeypatch.delenv("ADMIN_USERNAME", raising=False)
    monkeypatch.delenv("ADMIN_PASSWORD", raising=False)

    from app.config import get_settings

    get_settings.cache_clear()
    from app.main import create_app

    application = create_app()

    with TestClient(application) as ac:
        _register_login_author(ac, "thumb_author_1", "Password123")

        create = ac.post(
            "/api/content/",
            json={
                "prompt": "A space bedtime story",
                "genre": "science_fiction",
                "guardrails_enabled": True,
                "guardrails_max_loops": 2,
            },
        )
        assert create.status_code == 201
        content_id = create.json()["id"]

        _seed_story_and_pass(application, content_id)

        buf = BytesIO()
        Image.new("RGBA", (16, 16), (10, 20, 30, 255)).save(buf, format="PNG")
        fake_png = buf.getvalue()
        fake_img_resp = MagicMock()
        fake_img_resp.id = "img_resp_1"
        fake_img_resp.model = "gpt-image-1"
        fake_img_resp.data = [MagicMock(b64_json=base64.b64encode(fake_png).decode("ascii"))]

        with patch("app.services.openai_client.OpenAI") as mock_cls:
            instance = MagicMock()
            instance.images.generate.return_value = fake_img_resp
            mock_cls.return_value = instance

            r = ac.post(f"/api/content/{content_id}/generate-thumbnail")

        instance.images.generate.assert_called()

    assert r.status_code == 200
    body = r.json()
    assert body["content_id"] == content_id
    assert body["status"] == "thumbnail_generated"
    assert body["thumbnail_mime_type"] == "image/png"
    assert body["attempts_used"] == 1
    assert body["thumbnail_bytes_base64"]

    SessionLocal = application.state.SessionLocal
    with SessionLocal() as db:
        row = db.get(ContentItem, content_id)
        assert row is not None
        assert row.thumbnail_blob is not None
        assert row.thumbnail_blob.startswith(b"\x89PNG\r\n\x1a\n")
        assert row.thumbnail_mime_type == "image/png"
        assert row.status == "thumbnail_generated"

        event_id = db.scalar(
            select(AuditEvent.id).where(
                (AuditEvent.user_id == row.author_id)
                & (AuditEvent.event_type == "generate_thumbnail")
                & (AuditEvent.entity_type == "content_item")
                & (AuditEvent.entity_id == content_id)
            )
        )
        assert event_id is not None

        thumb_calls = list(
            db.scalars(
                select(ModelCall).where(
                    (ModelCall.user_id == row.author_id) & (ModelCall.purpose == "thumbnail")
                )
            ).all()
        )
        assert len(thumb_calls) == 1
        assert thumb_calls[0].operation_type == "images_generate"


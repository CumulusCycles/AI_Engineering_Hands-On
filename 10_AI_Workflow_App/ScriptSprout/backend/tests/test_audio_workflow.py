"""Audio narration workflow (mocked OpenAI TTS API)."""

from __future__ import annotations

from base64 import b64decode
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient
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
        row.title = "A Ferry Mystery"
        row.description = "A cozy story that can be narrated."
        row.story_text = "A foggy ferry horn sounded as Mina solved the mystery."
        row.guardrails_enabled = True
        row.status = "guardrails_passed"
        db.commit()


def test_generate_audio_persists_blob_and_tracks_events(monkeypatch, tmp_path) -> None:
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
        _register_login_author(ac, "audio_author_1", "Password123")

        create = ac.post(
            "/api/content/",
            json={
                "prompt": "A ferry mystery for bedtime",
                "genre": "mystery",
                "guardrails_enabled": True,
                "guardrails_max_loops": 2,
            },
        )
        assert create.status_code == 201
        content_id = create.json()["id"]

        _seed_story_and_pass(application, content_id)

        fake_audio = b"ID3FAKE-MP3-BYTES"
        fake_audio_resp = MagicMock()
        fake_audio_resp.id = "aud_resp_1"
        fake_audio_resp.read.return_value = fake_audio

        with patch("app.services.openai_client.OpenAI") as mock_cls:
            instance = MagicMock()
            instance.audio.speech.create.return_value = fake_audio_resp
            mock_cls.return_value = instance

            r = ac.post(
                f"/api/content/{content_id}/generate-audio",
                json={"voice_key": "female_us"},
            )

        instance.audio.speech.create.assert_called()

    assert r.status_code == 200
    body = r.json()
    assert body["content_id"] == content_id
    assert body["status"] == "audio_generated"
    assert body["audio_mime_type"] == "audio/mpeg"
    assert body["audio_voice"] == "nova"
    assert body["attempts_used"] == 1
    assert b64decode(body["audio_bytes_base64"]) == fake_audio

    SessionLocal = application.state.SessionLocal
    with SessionLocal() as db:
        row = db.get(ContentItem, content_id)
        assert row is not None
        assert row.audio_blob == fake_audio
        assert row.audio_mime_type == "audio/mpeg"
        assert row.audio_voice == "nova"
        assert row.audio_generated_at is not None
        assert row.status == "audio_generated"

        event_id = db.scalar(
            select(AuditEvent.id).where(
                (AuditEvent.user_id == row.author_id)
                & (AuditEvent.event_type == "generate_audio")
                & (AuditEvent.entity_type == "content_item")
                & (AuditEvent.entity_id == content_id)
            )
        )
        assert event_id is not None

        audio_calls = list(
            db.scalars(
                select(ModelCall).where(
                    (ModelCall.user_id == row.author_id)
                    & (ModelCall.purpose == "audio_narration")
                )
            ).all()
        )
        assert len(audio_calls) == 1
        assert audio_calls[0].operation_type == "audio_speech_create"


def test_generate_audio_rejects_unknown_voice_key(monkeypatch, tmp_path) -> None:
    """POST with an invalid voice_key returns 400 instead of 500."""
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
        _register_login_author(ac, "voice_author", "Password123")

        create = ac.post(
            "/api/content/",
            json={
                "prompt": "A short story for voice test",
                "genre": "fantasy",
                "guardrails_enabled": True,
                "guardrails_max_loops": 2,
            },
        )
        assert create.status_code == 201
        content_id = create.json()["id"]

        _seed_story_and_pass(application, content_id)

        r = ac.post(
            f"/api/content/{content_id}/generate-audio",
            json={"voice_key": "nonexistent_voice"},
        )

    assert r.status_code == 422
    assert "voice_key" in r.json()["detail"].lower()
    get_settings.cache_clear()

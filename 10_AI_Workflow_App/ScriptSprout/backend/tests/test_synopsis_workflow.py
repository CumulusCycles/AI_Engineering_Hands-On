"""Synopsis generation + approve/regenerate + audit_events."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient
from sqlalchemy import select

from app.db.models import AuditEvent, ContentItem


def _register_login_author(ac: TestClient, username: str, password: str) -> None:
    r = ac.post("/api/auth/register", json={"username": username, "password": password})
    assert r.status_code == 201
    r2 = ac.post("/api/auth/login", json={"username": username, "password": password})
    assert r2.status_code == 200


def test_generate_synopsis_creates_audit_event_and_updates_content(
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
        _register_login_author(ac, "syn_author_1", "Password123")

        # Create a content item first.
        create = ac.post(
            "/api/content/",
            json={"prompt": "A shy fox learns to sing", "genre": "fantasy"},
        )
        assert create.status_code == 201
        content_id = create.json()["id"]

        fake_resp = MagicMock()
        fake_resp.id = "resp_syn_1"
        fake_resp.model = "gpt-4o-mini"
        fake_resp.output_text = "A shy fox finds its courage and sings at the forest talent show."
        fake_resp.status = "completed"
        fake_resp.usage = None

        with patch("app.services.openai_client.OpenAI") as mock_cls:
            instance = MagicMock()
            instance.responses.create.return_value = fake_resp
            mock_cls.return_value = instance
            r = ac.post(f"/api/content/{content_id}/generate-synopsis")

    get_settings.cache_clear()

    assert r.status_code == 200
    body = r.json()
    assert body["content_id"] == content_id
    assert body["status"] == "synopsis_generated"
    assert "shy fox" in body["synopsis"].lower()
    assert body["attempts_used"] == 1

    SessionLocal = application.state.SessionLocal
    with SessionLocal() as db:
        row = db.get(ContentItem, content_id)
        assert row is not None
        assert row.synopsis is not None
        assert row.status == "synopsis_generated"

        generated_event_id = db.scalar(
            select(AuditEvent.id).where(
                (AuditEvent.user_id == row.author_id)
                & (AuditEvent.event_type == "generate_synopsis")
                & (AuditEvent.entity_type == "content_item")
                & (AuditEvent.entity_id == content_id),
            )
        )
        assert generated_event_id is not None


def test_approve_and_regenerate_synopsis_tracks_audit_events(monkeypatch, tmp_path) -> None:
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
        _register_login_author(ac, "syn_author_2", "Password123")
        create = ac.post(
            "/api/content/",
            json={"prompt": "Space story", "genre": "science_fiction"},
        )
        assert create.status_code == 201
        content_id = create.json()["id"]

        fake_resp_1 = MagicMock()
        fake_resp_1.id = "resp_syn_1"
        fake_resp_1.model = "gpt-4o-mini"
        fake_resp_1.output_text = "First synopsis."
        fake_resp_1.status = "completed"
        fake_resp_1.usage = None

        fake_resp_2 = MagicMock()
        fake_resp_2.id = "resp_syn_2"
        fake_resp_2.model = "gpt-4o-mini"
        fake_resp_2.output_text = "Second synopsis."
        fake_resp_2.status = "completed"
        fake_resp_2.usage = None

        with patch("app.services.openai_client.OpenAI") as mock_cls:
            instance = MagicMock()
            # generate-synopsis and regenerate-step
            instance.responses.create.side_effect = [fake_resp_1, fake_resp_2]
            mock_cls.return_value = instance

            gen = ac.post(f"/api/content/{content_id}/generate-synopsis")
            assert gen.status_code == 200
            app = ac.post(
                f"/api/content/{content_id}/approve-step",
                json={"step": "synopsis"},
            )
            assert app.status_code == 200

            regen = ac.post(
                f"/api/content/{content_id}/regenerate-step",
                json={"step": "synopsis"},
            )
            assert regen.status_code == 200

    SessionLocal = application.state.SessionLocal
    with SessionLocal() as db:
        row = db.get(ContentItem, content_id)
        assert row is not None
        assert row.synopsis == "Second synopsis."
        assert row.status == "synopsis_generated"

        approved = db.scalar(
            select(AuditEvent.id).where(
                (AuditEvent.user_id == row.author_id)
                & (AuditEvent.event_type == "approve_synopsis")
                & (AuditEvent.entity_id == content_id),
            )
        )
        assert approved is not None

        regenerated = db.scalar(
            select(AuditEvent.id).where(
                (AuditEvent.user_id == row.author_id)
                & (AuditEvent.event_type == "regenerate_synopsis")
                & (AuditEvent.entity_id == content_id),
            )
        )
        assert regenerated is not None


def test_openapi_includes_synopsis_step_schemas(client: TestClient) -> None:
    r = client.get("/openapi.json")
    assert r.status_code == 200
    schemas = r.json().get("components", {}).get("schemas", {})
    assert "GenerateSynopsisResponse" in schemas
    assert "ApproveStepRequest" in schemas
    assert "RegenerateStepRequest" in schemas


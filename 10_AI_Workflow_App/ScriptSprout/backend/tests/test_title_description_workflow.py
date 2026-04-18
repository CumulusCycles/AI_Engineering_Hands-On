"""Title + description generation + approve/regenerate + audit_events."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import httpx
from fastapi.testclient import TestClient
from openai import RateLimitError
from sqlalchemy import select

from app.db.models import AuditEvent, ContentItem, ModelCall


def _register_login_author(ac: TestClient, username: str, password: str) -> None:
    r = ac.post("/api/auth/register", json={"username": username, "password": password})
    assert r.status_code == 201
    r2 = ac.post("/api/auth/login", json={"username": username, "password": password})
    assert r2.status_code == 200


def test_generate_title_creates_audit_event_and_updates_content(
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
        _register_login_author(ac, "title_author_1", "Password123")

        create = ac.post(
            "/api/content/",
            json={"prompt": "Space story", "genre": "science_fiction"},
        )
        assert create.status_code == 201
        content_id = create.json()["id"]

        fake_synopsis = MagicMock()
        fake_synopsis.id = "resp_syn_1"
        fake_synopsis.model = "gpt-4o-mini"
        fake_synopsis.output_text = "A shy astronaut finds courage on a tiny moon."
        fake_synopsis.status = "completed"
        fake_synopsis.usage = None

        fake_title = MagicMock()
        fake_title.id = "resp_title_1"
        fake_title.model = "gpt-4o-mini"
        fake_title.output_text = "A Shy Astronaut’s Tiny Moon Courage"
        fake_title.status = "completed"
        fake_title.usage = None

        with patch("app.services.openai_client.OpenAI") as mock_cls:
            instance = MagicMock()
            # generate-synopsis then generate-title
            instance.responses.create.side_effect = [fake_synopsis, fake_title]
            mock_cls.return_value = instance

            gen = ac.post(f"/api/content/{content_id}/generate-synopsis")
            assert gen.status_code == 200

            app = ac.post(
                f"/api/content/{content_id}/approve-step",
                json={"step": "synopsis"},
            )
            assert app.status_code == 200

            title = ac.post(f"/api/content/{content_id}/generate-title")
            assert title.status_code == 200

    assert title.status_code == 200
    body = title.json()
    assert body["content_id"] == content_id
    assert body["status"] == "title_generated"
    assert "astronaut" in body["title"].lower()
    assert body["attempts_used"] == 1

    SessionLocal = application.state.SessionLocal
    with SessionLocal() as db:
        row = db.get(ContentItem, content_id)
        assert row is not None
        assert row.title is not None
        assert row.status == "title_generated"

        generated_event_id = db.scalar(
            select(AuditEvent.id).where(
                (AuditEvent.user_id == row.author_id)
                & (AuditEvent.event_type == "generate_title")
                & (AuditEvent.entity_type == "content_item")
                & (AuditEvent.entity_id == content_id),
            )
        )
        assert generated_event_id is not None


def test_title_and_description_approval_and_regeneration_tracks_audit_events(
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
        _register_login_author(ac, "title_author_2", "Password123")

        create = ac.post(
            "/api/content/",
            json={"prompt": "Ocean bedtime mystery", "genre": "mystery"},
        )
        assert create.status_code == 201
        content_id = create.json()["id"]

        fake_synopsis = MagicMock()
        fake_synopsis.id = "resp_syn_1"
        fake_synopsis.model = "gpt-4o-mini"
        fake_synopsis.output_text = "On a foggy ferry, a curious kid uncovers a gentle mystery."
        fake_synopsis.status = "completed"
        fake_synopsis.usage = None

        fake_title_1 = MagicMock()
        fake_title_1.id = "resp_title_1"
        fake_title_1.model = "gpt-4o-mini"
        fake_title_1.output_text = "The Foggy Ferry Mystery"
        fake_title_1.status = "completed"
        fake_title_1.usage = None

        fake_desc_1 = MagicMock()
        fake_desc_1.id = "resp_desc_1"
        fake_desc_1.model = "gpt-4o-mini"
        fake_desc_1.output_text = (
            "Welcome aboard! A curious kid follows clues through misty decks.\n\n"
            "A warm mystery unfolds with kindness at its heart."
        )
        fake_desc_1.status = "completed"
        fake_desc_1.usage = None

        fake_title_2 = MagicMock()
        fake_title_2.id = "resp_title_2"
        fake_title_2.model = "gpt-4o-mini"
        fake_title_2.output_text = "Kind Clues on the Foggy Ferry"
        fake_title_2.status = "completed"
        fake_title_2.usage = None

        fake_desc_2 = MagicMock()
        fake_desc_2.id = "resp_desc_2"
        fake_desc_2.model = "gpt-4o-mini"
        fake_desc_2.output_text = (
            "A gentle mystery on open waters. Our curious kid uses kindness as a compass.\n\n"
            "Expect cozy suspense and a hopeful ending."
        )
        fake_desc_2.status = "completed"
        fake_desc_2.usage = None

        with patch("app.services.openai_client.OpenAI") as mock_cls:
            instance = MagicMock()
            # 1) generate-synopsis, 2) generate-title, 3) generate-description
            # 4) regenerate-title, 5) regenerate-description
            instance.responses.create.side_effect = [
                fake_synopsis,
                fake_title_1,
                fake_desc_1,
                fake_title_2,
                fake_desc_2,
            ]
            mock_cls.return_value = instance

            gen_syn = ac.post(f"/api/content/{content_id}/generate-synopsis")
            assert gen_syn.status_code == 200

            approve_syn = ac.post(
                f"/api/content/{content_id}/approve-step",
                json={"step": "synopsis"},
            )
            assert approve_syn.status_code == 200

            gen_title = ac.post(f"/api/content/{content_id}/generate-title")
            assert gen_title.status_code == 200

            approve_title = ac.post(
                f"/api/content/{content_id}/approve-step",
                json={"step": "title"},
            )
            assert approve_title.status_code == 200

            gen_desc = ac.post(f"/api/content/{content_id}/generate-description")
            assert gen_desc.status_code == 200

            approve_desc = ac.post(
                f"/api/content/{content_id}/approve-step",
                json={"step": "description"},
            )
            assert approve_desc.status_code == 200

            # Title regen should clear description.
            regen_title = ac.post(
                f"/api/content/{content_id}/regenerate-step",
                json={"step": "title"},
            )
            assert regen_title.status_code == 200

            approve_title_2 = ac.post(
                f"/api/content/{content_id}/approve-step",
                json={"step": "title"},
            )
            assert approve_title_2.status_code == 200

            regen_desc = ac.post(
                f"/api/content/{content_id}/regenerate-step",
                json={"step": "description"},
            )
            assert regen_desc.status_code == 200

            approve_desc_2 = ac.post(
                f"/api/content/{content_id}/approve-step",
                json={"step": "description"},
            )
            assert approve_desc_2.status_code == 200

    SessionLocal = application.state.SessionLocal
    with SessionLocal() as db:
        row = db.get(ContentItem, content_id)
        assert row is not None
        assert row.title == "Kind Clues on the Foggy Ferry"
        assert row.description is not None
        assert row.status == "description_approved"

        def _has_event(event_type: str) -> bool:
            eid = db.scalar(
                select(AuditEvent.id).where(
                    (AuditEvent.user_id == row.author_id)
                    & (AuditEvent.event_type == event_type)
                    & (AuditEvent.entity_type == "content_item")
                    & (AuditEvent.entity_id == content_id),
                )
            )
            return eid is not None

        assert _has_event("approve_title")
        assert _has_event("generate_description")
        assert _has_event("approve_description")
        assert _has_event("regenerate_title")
        assert _has_event("regenerate_description")
        assert _has_event("approve_description")


def test_openapi_includes_title_and_description_schemas(client: TestClient) -> None:
    r = client.get("/openapi.json")
    assert r.status_code == 200
    schemas = r.json().get("components", {}).get("schemas", {})
    assert "GenerateTitleResponse" in schemas
    assert "GenerateDescriptionResponse" in schemas


def test_generate_title_retries_transient_429_and_logs_model_calls(
    monkeypatch,
    tmp_path,
) -> None:
    """Integration-style check: transient OpenAI errors still produce 2 model_call rows."""

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
        _register_login_author(ac, "title_modelcall_author", "Password123")

        create = ac.post(
            "/api/content/",
            json={"prompt": "Space story", "genre": "science_fiction"},
        )
        assert create.status_code == 201
        content_id = create.json()["id"]

        fake_synopsis = MagicMock()
        fake_synopsis.id = "resp_syn_1"
        fake_synopsis.model = "gpt-4o-mini"
        fake_synopsis.output_text = "Approved synopsis."
        fake_synopsis.status = "completed"
        fake_synopsis.usage = None

        # Build a transient OpenAI-style 429 error (same pattern as openai_smoke tests).
        req = httpx.Request("POST", "https://api.openai.com/v1/responses")
        rl = RateLimitError(
            "rate limit",
            response=httpx.Response(429, request=req),
            body=None,
        )

        fake_title = MagicMock()
        fake_title.id = "resp_title_2"
        fake_title.model = "gpt-4o-mini"
        fake_title.output_text = "A Shy Astronaut Finds Courage"
        fake_title.status = "completed"
        fake_title.usage = None

        with patch("app.services.openai_client.OpenAI") as mock_cls:
            instance = MagicMock()
            # generate-synopsis (1 call) then generate-title (2 calls: error + success)
            instance.responses.create.side_effect = [fake_synopsis, rl, fake_title]
            mock_cls.return_value = instance

            gen_syn = ac.post(f"/api/content/{content_id}/generate-synopsis")
            assert gen_syn.status_code == 200

            approve_syn = ac.post(
                f"/api/content/{content_id}/approve-step",
                json={"step": "synopsis"},
            )
            assert approve_syn.status_code == 200

            gen_title = ac.post(f"/api/content/{content_id}/generate-title")
            assert gen_title.status_code == 200
            assert gen_title.json()["status"] == "title_generated"
            assert gen_title.json()["attempts_used"] == 2

    SessionLocal = application.state.SessionLocal
    with SessionLocal() as db:
        row = db.get(ContentItem, content_id)
        assert row is not None
        title_calls = list(
            db.scalars(
                select(ModelCall).where(
                    (ModelCall.user_id == row.author_id)
                    & (ModelCall.purpose == "title")
                )
            ).all()
        )
        assert len(title_calls) == 2
        # One attempt should fail, the other should succeed.
        assert {c.attempt_index for c in title_calls} == {1, 2}
        assert any(not c.success for c in title_calls)
        assert any(c.success for c in title_calls)


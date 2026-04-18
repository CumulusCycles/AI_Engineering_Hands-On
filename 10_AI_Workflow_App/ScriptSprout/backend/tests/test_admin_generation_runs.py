"""Admin inspection for generation run tracking."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient
from sqlalchemy import select

from app.db.models import ContentItem, GenerationRun, GuardrailsEvent
from app.schemas.story_generation import GuardrailsCheckParsed


def _register_login_author(ac: TestClient, username: str, password: str) -> None:
    r = ac.post("/api/auth/register", json={"username": username, "password": password})
    assert r.status_code == 201
    r2 = ac.post("/api/auth/login", json={"username": username, "password": password})
    assert r2.status_code == 200


def _seed_story_inputs(application, content_id: int) -> None:
    SessionLocal = application.state.SessionLocal
    with SessionLocal() as db:
        row = db.get(ContentItem, content_id)
        assert row is not None
        row.synopsis = "Approved synopsis."
        row.title = "A Shy Astronaut"
        row.description = "A gentle description for a short narration."
        row.status = "description_approved"
        db.commit()


def test_admin_can_inspect_generation_run_events(
    monkeypatch,
    tmp_path,
) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test-dummy-key-for-pytest")
    monkeypatch.setenv("SQLITE_PATH", str(tmp_path / "test.db"))
    monkeypatch.setenv("CHROMA_PATH", str(tmp_path / "chroma"))
    monkeypatch.setenv("ADMIN_USERNAME", "seedadmin")
    monkeypatch.setenv("ADMIN_PASSWORD", "seedpassword123")

    from app.config import get_settings

    get_settings.cache_clear()
    from app.main import create_app

    application = create_app()

    with TestClient(application) as ac:
        _register_login_author(ac, "story_author_event_1", "Password123")

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

        _seed_story_inputs(application, content_id)

        fake_story_resp = MagicMock()
        fake_story_resp.id = "resp_story_event_1"
        fake_story_resp.model = "gpt-4o-mini"
        fake_story_resp.output_text = (
            "Once upon a time, the astronaut listened to safe stars."
        )
        fake_story_resp.usage = None

        fake_guardrails_resp_1 = MagicMock()
        fake_guardrails_resp_1.id = "resp_guard_event_1_1"
        fake_guardrails_resp_1.model = "gpt-4o-mini"
        fake_guardrails_resp_1.output_parsed = GuardrailsCheckParsed(
            passed=False, failure_reason="Inappropriate tone for audience."
        )
        fake_guardrails_resp_1.usage = None

        fake_guardrails_resp_2 = MagicMock()
        fake_guardrails_resp_2.id = "resp_guard_event_1_2"
        fake_guardrails_resp_2.model = "gpt-4o-mini"
        fake_guardrails_resp_2.output_parsed = GuardrailsCheckParsed(
            passed=True, failure_reason=None
        )
        fake_guardrails_resp_2.usage = None

        with patch("app.services.openai_client.OpenAI") as mock_cls:
            instance = MagicMock()
            instance.responses.create.return_value = fake_story_resp
            instance.responses.parse.side_effect = [
                fake_guardrails_resp_1,
                fake_guardrails_resp_2,
            ]
            mock_cls.return_value = instance

            r = ac.post(f"/api/content/{content_id}/generate-story")

        assert r.status_code == 200
        body = r.json()
        assert body["status"] == "guardrails_passed"
        assert body["generation_run_id"] is not None

        generation_run_id = body["generation_run_id"]

        SessionLocal = application.state.SessionLocal
        with SessionLocal() as db:
            gen_row = db.scalar(
                select(GenerationRun).where(GenerationRun.id == generation_run_id)
            )
            assert gen_row is not None
            assert gen_row.status == "guardrails_passed"

            events = list(
                db.scalars(
                    select(GuardrailsEvent).where(
                        GuardrailsEvent.run_id == generation_run_id
                    )
                ).all()
            )
            assert len(events) == 2
            assert [e.attempt_index for e in events] == [1, 2]

        # Switch to admin session for the admin inspection route.
        ac.post("/api/auth/logout")
        r_login_admin = ac.post(
            "/api/auth/login",
            json={"username": "seedadmin", "password": "seedpassword123"},
        )
        assert r_login_admin.status_code == 200

        r_admin = ac.get(f"/api/admin/generation-runs/{generation_run_id}")
        assert r_admin.status_code == 200
        detail = r_admin.json()
        assert detail["id"] == generation_run_id
        assert detail["status"] == "guardrails_passed"
        assert detail["story_attempts_used"] == 2
        assert detail["guardrails_attempts_used"] == 2
        assert [e["attempt_index"] for e in detail["events"]] == [1, 2]


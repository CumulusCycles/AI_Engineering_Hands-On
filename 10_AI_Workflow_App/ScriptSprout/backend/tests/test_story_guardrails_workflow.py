"""Story generation + guardrails parse workflow (mocked OpenAI)."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient
from sqlalchemy import select

from app.db.models import (
    AuditEvent,
    ContentItem,
    GenerationRun,
    GuardrailsEvent,
    ModelCall,
)
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


def test_generate_story_guardrails_pass_tracks_audit_and_model_calls(
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
        _register_login_author(ac, "story_author_1", "Password123")

        create = ac.post(
            "/api/content/",
            json={
                "prompt": "A space bedtime story",
                "genre": "science_fiction",
                "guardrails_enabled": True,
                "guardrails_max_loops": 3,
            },
        )
        assert create.status_code == 201
        content_id = create.json()["id"]

        _seed_story_inputs(application, content_id)

        fake_story_resp = MagicMock()
        fake_story_resp.id = "resp_story_1"
        fake_story_resp.model = "gpt-4o-mini"
        fake_story_resp.output_text = "Once upon a time, a shy astronaut listened to the stars."
        fake_story_resp.usage = None

        fake_guardrails_resp = MagicMock()
        fake_guardrails_resp.id = "resp_guard_1"
        fake_guardrails_resp.model = "gpt-4o-mini"
        fake_guardrails_resp.output_parsed = GuardrailsCheckParsed(passed=True, failure_reason=None)
        fake_guardrails_resp.usage = None

        with patch("app.services.openai_client.OpenAI") as mock_cls:
            instance = MagicMock()
            instance.responses.create.return_value = fake_story_resp
            instance.responses.parse.return_value = fake_guardrails_resp
            mock_cls.return_value = instance

            r = ac.post(f"/api/content/{content_id}/generate-story")

    assert r.status_code == 200
    body = r.json()
    assert body["content_id"] == content_id
    assert body["status"] == "guardrails_passed"
    assert body["story_attempts_used"] == 1
    assert body["guardrails_attempts_used"] == 1
    assert "stars" in body["story_text"].lower()

    SessionLocal = application.state.SessionLocal
    with SessionLocal() as db:
        row = db.get(ContentItem, content_id)
        assert row is not None
        assert row.story_text is not None
        assert row.status == "guardrails_passed"

        gen_run = db.scalar(
            select(GenerationRun).where(GenerationRun.content_id == content_id)
        )
        assert gen_run is not None
        assert gen_run.status == "guardrails_passed"
        assert gen_run.story_attempts_used == 1
        assert gen_run.guardrails_attempts_used == 1
        assert gen_run.failure_reason is None

        guardrail_events = list(
            db.scalars(
                select(GuardrailsEvent).where(GuardrailsEvent.run_id == gen_run.id)
            ).all()
        )
        assert len(guardrail_events) == 1
        assert guardrail_events[0].passed is True
        assert guardrail_events[0].failure_reason is None
        assert guardrail_events[0].attempt_index == 1

        event_id = db.scalar(
            select(AuditEvent.id).where(
                (AuditEvent.user_id == row.author_id)
                & (AuditEvent.event_type == "generate_story")
                & (AuditEvent.entity_type == "content_item")
                & (AuditEvent.entity_id == content_id)
            )
        )
        assert event_id is not None

        story_calls = list(
            db.scalars(
                select(ModelCall).where(
                    (ModelCall.user_id == row.author_id)
                    & (ModelCall.purpose == "story")
                )
            ).all()
        )

        guardrail_calls = list(
            db.scalars(
                select(ModelCall).where(
                    (ModelCall.user_id == row.author_id)
                    & (ModelCall.purpose == "guardrails_check")
                )
            ).all()
        )
        assert len(story_calls) == 1
        assert len(guardrail_calls) == 1
        assert story_calls[0].attempt_index == 1
        assert guardrail_calls[0].attempt_index == 1


def test_generate_story_guardrails_fail_tracks_audit_and_model_calls(
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
        _register_login_author(ac, "story_author_2", "Password123")

        create = ac.post(
            "/api/content/",
            json={
                "prompt": "A space bedtime story",
                "genre": "science_fiction",
                "guardrails_enabled": True,
                "guardrails_max_loops": 3,
            },
        )
        assert create.status_code == 201
        content_id = create.json()["id"]

        _seed_story_inputs(application, content_id)

        fake_story_resp = MagicMock()
        fake_story_resp.id = "resp_story_2"
        fake_story_resp.model = "gpt-4o-mini"
        fake_story_resp.output_text = "Once upon a time, the astronaut made a risky joke."
        fake_story_resp.usage = None

        fake_guardrails_resp = MagicMock()
        fake_guardrails_resp.id = "resp_guard_2"
        fake_guardrails_resp.model = "gpt-4o-mini"
        fake_guardrails_resp.output_parsed = GuardrailsCheckParsed(
            passed=False, failure_reason="Inappropriate tone for audience."
        )
        fake_guardrails_resp.usage = None

        with patch("app.services.openai_client.OpenAI") as mock_cls:
            instance = MagicMock()
            instance.responses.create.return_value = fake_story_resp
            # Always fail guardrails so we exercise the retry loop.
            instance.responses.parse.return_value = fake_guardrails_resp
            mock_cls.return_value = instance

            r = ac.post(f"/api/content/{content_id}/generate-story")

    assert r.status_code == 200
    body = r.json()
    assert body["content_id"] == content_id
    assert body["status"] == "guardrails_failed"
    assert body["story_attempts_used"] == 3
    assert body["guardrails_attempts_used"] == 3

    SessionLocal = application.state.SessionLocal
    with SessionLocal() as db:
        row = db.get(ContentItem, content_id)
        assert row is not None
        assert row.story_text is not None
        assert row.status == "guardrails_failed"

        gen_run = db.scalar(
            select(GenerationRun).where(GenerationRun.content_id == content_id)
        )
        assert gen_run is not None
        assert gen_run.status == "guardrails_failed"
        assert gen_run.story_attempts_used == 3
        assert gen_run.guardrails_attempts_used == 3
        assert gen_run.failure_reason == "Inappropriate tone for audience."

        guardrail_events = list(
            db.scalars(
                select(GuardrailsEvent).where(GuardrailsEvent.run_id == gen_run.id)
            ).all()
        )
        assert len(guardrail_events) == 3
        assert all(e.passed is False for e in guardrail_events)
        assert [e.attempt_index for e in guardrail_events] == [1, 2, 3]

        event_id = db.scalar(
            select(AuditEvent.id).where(
                (AuditEvent.user_id == row.author_id)
                & (AuditEvent.event_type == "generate_story")
                & (AuditEvent.entity_type == "content_item")
                & (AuditEvent.entity_id == content_id)
            )
        )
        assert event_id is not None

        guardrail_calls = list(
            db.scalars(
                select(ModelCall).where(
                    (ModelCall.user_id == row.author_id)
                    & (ModelCall.purpose == "guardrails_check")
                )
            ).all()
        )
        assert len(guardrail_calls) == 3
        assert all(c.attempt_index == 1 for c in guardrail_calls)

        story_calls = list(
            db.scalars(
                select(ModelCall).where(
                    (ModelCall.user_id == row.author_id)
                    & (ModelCall.purpose == "story")
                )
            ).all()
        )
        assert len(story_calls) == 3
        assert all(c.attempt_index == 1 for c in story_calls)


def test_generate_story_guardrails_retry_then_pass_tracks_audit_and_model_calls(
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
        _register_login_author(ac, "story_author_3", "Password123")

        create = ac.post(
            "/api/content/",
            json={
                "prompt": "A space bedtime story",
                "genre": "science_fiction",
                "guardrails_enabled": True,
                "guardrails_max_loops": 3,
            },
        )
        assert create.status_code == 201
        content_id = create.json()["id"]

        _seed_story_inputs(application, content_id)

        fake_story_resp = MagicMock()
        fake_story_resp.id = "resp_story_3"
        fake_story_resp.model = "gpt-4o-mini"
        fake_story_resp.output_text = "Once upon a time, the astronaut listened to safe stars."
        fake_story_resp.usage = None

        fake_guardrails_resp_1 = MagicMock()
        fake_guardrails_resp_1.id = "resp_guard_3_1"
        fake_guardrails_resp_1.model = "gpt-4o-mini"
        fake_guardrails_resp_1.output_parsed = GuardrailsCheckParsed(
            passed=False, failure_reason="Inappropriate tone for audience."
        )
        fake_guardrails_resp_1.usage = None

        fake_guardrails_resp_2 = MagicMock()
        fake_guardrails_resp_2.id = "resp_guard_3_2"
        fake_guardrails_resp_2.model = "gpt-4o-mini"
        fake_guardrails_resp_2.output_parsed = GuardrailsCheckParsed(
            passed=True, failure_reason=None
        )
        fake_guardrails_resp_2.usage = None

        with patch("app.services.openai_client.OpenAI") as mock_cls:
            instance = MagicMock()
            instance.responses.create.return_value = fake_story_resp
            instance.responses.parse.side_effect = [fake_guardrails_resp_1, fake_guardrails_resp_2]
            mock_cls.return_value = instance

            r = ac.post(f"/api/content/{content_id}/generate-story")

    assert r.status_code == 200
    body = r.json()
    assert body["content_id"] == content_id
    assert body["status"] == "guardrails_passed"
    assert body["story_attempts_used"] == 2
    assert body["guardrails_attempts_used"] == 2

    SessionLocal = application.state.SessionLocal
    with SessionLocal() as db:
        row = db.get(ContentItem, content_id)
        assert row is not None
        assert row.story_text is not None
        assert row.status == "guardrails_passed"

        gen_run = db.scalar(
            select(GenerationRun).where(GenerationRun.content_id == content_id)
        )
        assert gen_run is not None
        assert gen_run.status == "guardrails_passed"
        assert gen_run.story_attempts_used == 2
        assert gen_run.guardrails_attempts_used == 2
        assert gen_run.failure_reason is None

        guardrail_events = list(
            db.scalars(
                select(GuardrailsEvent).where(GuardrailsEvent.run_id == gen_run.id)
            ).all()
        )
        assert len(guardrail_events) == 2
        assert guardrail_events[0].passed is False
        assert guardrail_events[0].failure_reason == "Inappropriate tone for audience."
        assert guardrail_events[0].attempt_index == 1
        assert guardrail_events[1].passed is True
        assert guardrail_events[1].failure_reason is None
        assert guardrail_events[1].attempt_index == 2

        guardrail_calls = list(
            db.scalars(
                select(ModelCall).where(
                    (ModelCall.user_id == row.author_id)
                    & (ModelCall.purpose == "guardrails_check")
                )
            ).all()
        )
        story_calls = list(
            db.scalars(
                select(ModelCall).where(
                    (ModelCall.user_id == row.author_id)
                    & (ModelCall.purpose == "story")
                )
            ).all()
        )
        assert len(guardrail_calls) == 2
        assert len(story_calls) == 2


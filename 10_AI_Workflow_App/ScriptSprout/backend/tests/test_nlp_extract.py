"""Author NLP extraction route."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import httpx
from fastapi.testclient import TestClient
from openai import RateLimitError
from sqlalchemy import select

from app.db.models import ModelCall
from app.schemas.story_parameters import StoryParametersParsed


def _register_login_author(client: TestClient, username: str, password: str) -> None:
    assert client.post(
        "/api/auth/register",
        json={"username": username, "password": password},
    ).status_code == 201
    assert client.post(
        "/api/auth/login",
        json={"username": username, "password": password},
    ).status_code == 200


def _mock_parsed_response(parsed: StoryParametersParsed) -> MagicMock:
    pr = MagicMock()
    pr.output_parsed = parsed
    pr.id = "resp_extract_1"
    pr.model = "gpt-4o-mini"
    pr.usage = None
    return pr


def test_extract_story_parameters_200_complete(client: TestClient, monkeypatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test-dummy-key-for-pytest")
    from app.config import get_settings

    get_settings.cache_clear()
    from app.main import create_app

    application = create_app()
    parsed = StoryParametersParsed(
        subject="A shy fox learns to sing",
        genre="fantasy",
        age_group="kids",
        video_length_minutes=12,
        target_word_count=None,
        missing_fields=[],
    )
    fake_pr = _mock_parsed_response(parsed)

    with TestClient(application) as ac:
        _register_login_author(ac, "nlp_author_a", "Password123")
        with patch("app.services.openai_client.OpenAI") as mock_cls:
            instance = MagicMock()
            instance.responses.parse.return_value = fake_pr
            mock_cls.return_value = instance
            r = ac.post(
                "/api/nlp/extract-story-parameters",
                json={"prompt": "12 min cozy fantasy for kids about a fox"},
            )
    get_settings.cache_clear()

    assert r.status_code == 200
    body = r.json()
    assert body["subject"] == "A shy fox learns to sing"
    assert body["genre"] == "fantasy"
    assert body["age_group"] == "kids"
    assert body["video_length_minutes"] == 12
    assert body["is_complete"] is True
    assert body["missing_fields"] == []
    assert body["follow_up"] == []
    assert body["attempts_used"] == 1
    assert body["openai_response_id"] == "resp_extract_1"


def test_extract_story_parameters_incomplete(client: TestClient, monkeypatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test-dummy-key-for-pytest")
    from app.config import get_settings

    get_settings.cache_clear()
    from app.main import create_app

    application = create_app()
    parsed = StoryParametersParsed(
        subject="Something vague about space",
        genre=None,
        age_group=None,
        video_length_minutes=None,
        missing_fields=["genre", "age_group"],
    )
    fake_pr = _mock_parsed_response(parsed)

    with TestClient(application) as ac:
        _register_login_author(ac, "nlp_author_b", "Password123")
        with patch("app.services.openai_client.OpenAI") as mock_cls:
            instance = MagicMock()
            instance.responses.parse.return_value = fake_pr
            mock_cls.return_value = instance
            r = ac.post(
                "/api/nlp/extract-story-parameters",
                json={"prompt": "space story"},
            )
    get_settings.cache_clear()

    assert r.status_code == 200
    body = r.json()
    assert body["is_complete"] is False
    assert "genre" in body["missing_fields"]
    assert "age_group" in body["missing_fields"]
    assert "video_length_minutes" in body["missing_fields"]
    fu = body["follow_up"]
    assert len(fu) == len(body["missing_fields"])
    by_field = {x["field"]: x for x in fu}
    assert by_field["genre"]["input_kind"] == "single_select"
    assert by_field["genre"]["suggested_options"] is not None
    assert "fantasy" in by_field["genre"]["suggested_options"]
    assert by_field["age_group"]["input_kind"] == "single_select"
    assert by_field["video_length_minutes"]["input_kind"] == "number"


def test_extract_story_parameters_unauthenticated(client: TestClient, monkeypatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test-dummy-key-for-pytest")
    from app.config import get_settings

    get_settings.cache_clear()
    from app.main import create_app

    application = create_app()
    with TestClient(application) as ac:
        r = ac.post(
            "/api/nlp/extract-story-parameters",
            json={"prompt": "x"},
        )
    get_settings.cache_clear()
    assert r.status_code == 401


def test_extract_story_parameters_admin_forbidden(client_with_admin: TestClient) -> None:
    client_with_admin.post(
        "/api/auth/login",
        json={"username": "seedadmin", "password": "seedpassword123"},
    )
    r = client_with_admin.post(
        "/api/nlp/extract-story-parameters",
        json={"prompt": "admin tries extract"},
    )
    assert r.status_code == 403


def test_extract_story_parameters_503_no_key(client: TestClient, monkeypatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    from app.config import get_settings

    get_settings.cache_clear()
    from app.main import create_app

    application = create_app()
    with TestClient(application) as ac:
        _register_login_author(ac, "nlp_author_c", "Password123")
        r = ac.post(
            "/api/nlp/extract-story-parameters",
            json={"prompt": "x"},
        )
    get_settings.cache_clear()
    assert r.status_code == 503


def test_extract_logs_model_call_row(client: TestClient, monkeypatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test-dummy-key-for-pytest")
    from app.config import get_settings

    get_settings.cache_clear()
    from app.main import create_app

    application = create_app()
    parsed = StoryParametersParsed(
        subject="x",
        genre="mystery",
        age_group="adult",
        video_length_minutes=5,
        missing_fields=[],
    )
    fake_pr = _mock_parsed_response(parsed)

    with TestClient(application) as ac:
        _register_login_author(ac, "nlp_author_d", "Password123")
        with patch("app.services.openai_client.OpenAI") as mock_cls:
            instance = MagicMock()
            instance.responses.parse.return_value = fake_pr
            mock_cls.return_value = instance
            ac.post(
                "/api/nlp/extract-story-parameters",
                json={"prompt": "5 min mystery for adults"},
            )
        SessionLocal = application.state.SessionLocal
        with SessionLocal() as db:
            row = db.scalars(
                select(ModelCall).where(ModelCall.purpose == "extract_story_parameters"),
            ).first()
            assert row is not None
            assert row.operation_type == "responses_parse"
            assert row.success is True
    get_settings.cache_clear()


def test_extract_retry_writes_two_model_calls(client: TestClient, monkeypatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test-dummy-key-for-pytest")
    from app.config import get_settings

    get_settings.cache_clear()
    from app.main import create_app

    application = create_app()
    parsed = StoryParametersParsed(
        subject="ok",
        genre="adventure",
        age_group="teen",
        video_length_minutes=8,
        missing_fields=[],
    )
    fake_pr = _mock_parsed_response(parsed)
    req = httpx.Request("POST", "https://api.openai.com/v1/responses")
    rl = RateLimitError("rl", response=httpx.Response(429, request=req), body=None)

    with TestClient(application) as ac:
        _register_login_author(ac, "nlp_author_e", "Password123")
        with patch("app.services.openai_client.OpenAI") as mock_cls:
            instance = MagicMock()
            instance.responses.parse.side_effect = [rl, fake_pr]
            mock_cls.return_value = instance
            r = ac.post(
                "/api/nlp/extract-story-parameters",
                json={"prompt": "8 min teen adventure"},
            )
    get_settings.cache_clear()

    assert r.status_code == 200
    assert r.json()["attempts_used"] == 2


def test_extract_no_structured_output_502(client: TestClient, monkeypatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test-dummy-key-for-pytest")
    from app.config import get_settings

    get_settings.cache_clear()
    from app.main import create_app

    application = create_app()
    fake_pr = MagicMock()
    fake_pr.output_parsed = None
    fake_pr.id = "resp_bad"
    fake_pr.model = "gpt-4o-mini"
    fake_pr.usage = None

    with TestClient(application) as ac:
        _register_login_author(ac, "nlp_author_f", "Password123")
        with patch("app.services.openai_client.OpenAI") as mock_cls:
            instance = MagicMock()
            instance.responses.parse.return_value = fake_pr
            mock_cls.return_value = instance
            r = ac.post(
                "/api/nlp/extract-story-parameters",
                json={"prompt": "x"},
            )
    get_settings.cache_clear()
    assert r.status_code == 502


def test_openapi_includes_nlp_schemas(client: TestClient) -> None:
    r = client.get("/openapi.json")
    assert r.status_code == 200
    schemas = r.json().get("components", {}).get("schemas", {})
    assert "ExtractStoryParametersRequest" in schemas
    assert "StoryParametersExtractResponse" in schemas
    assert "MissingFieldFollowUp" in schemas


def test_genre_alias_science_fiction() -> None:
    from app.services.story_parameter_extraction import _normalize_genre

    assert _normalize_genre("Sci-Fi") == "science_fiction"

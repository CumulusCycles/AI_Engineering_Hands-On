"""Admin OpenAI smoke route (mocked OpenAI; no real API calls)."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import httpx
from fastapi.testclient import TestClient
from openai import RateLimitError


def test_openai_smoke_503_when_api_key_missing(client_with_admin: TestClient, monkeypatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    from app.config import get_settings

    get_settings.cache_clear()
    from app.main import create_app

    application = create_app()
    with TestClient(application) as ac:
        ac.post(
            "/api/auth/login",
            json={"username": "seedadmin", "password": "seedpassword123"},
        )
        r = ac.post("/api/admin/openai/smoke", json={"prompt": "hi"})
    get_settings.cache_clear()
    assert r.status_code == 503
    assert r.json()["code"] == "http_503"


def test_openai_smoke_200_mocked(client_with_admin: TestClient, monkeypatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test-dummy-key-for-pytest")
    from app.config import get_settings

    get_settings.cache_clear()
    from app.main import create_app

    application = create_app()
    fake_usage = MagicMock()
    fake_usage.model_dump = MagicMock(
        return_value={"input_tokens": 1, "output_tokens": 2},
    )
    fake_resp = MagicMock()
    fake_resp.id = "resp_test_1"
    fake_resp.model = "gpt-4o-mini"
    fake_resp.output_text = "pong"
    fake_resp.status = "completed"
    fake_resp.usage = fake_usage

    with TestClient(application) as ac:
        ac.post(
            "/api/auth/login",
            json={"username": "seedadmin", "password": "seedpassword123"},
        )
        with patch(
            "app.services.openai_client.OpenAI",
        ) as mock_cls:
            instance = MagicMock()
            instance.responses.create.return_value = fake_resp
            mock_cls.return_value = instance
            r = ac.post("/api/admin/openai/smoke", json={"prompt": "ping"})
    get_settings.cache_clear()

    assert r.status_code == 200
    body = r.json()
    assert body["response_id"] == "resp_test_1"
    assert body["model"] == "gpt-4o-mini"
    assert body["output_text"] == "pong"
    assert body["status"] == "completed"
    assert body["usage"] == {"input_tokens": 1, "output_tokens": 2}
    assert body["attempts_used"] == 1


def test_openai_smoke_forbidden_for_author(client: TestClient) -> None:
    client.post(
        "/api/auth/register",
        json={"username": "author_smoke", "password": "Password123"},
    )
    client.post(
        "/api/auth/login",
        json={"username": "author_smoke", "password": "Password123"},
    )
    r = client.post("/api/admin/openai/smoke", json={})
    assert r.status_code == 403


def test_openai_smoke_retries_transient_429_then_success(
    client_with_admin: TestClient, monkeypatch
) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test-dummy-key-for-pytest")
    from app.config import get_settings

    get_settings.cache_clear()
    from app.main import create_app

    application = create_app()
    fake_usage = MagicMock()
    fake_usage.model_dump = MagicMock(return_value={})
    fake_resp = MagicMock()
    fake_resp.id = "resp_after_retry"
    fake_resp.model = "gpt-4o-mini"
    fake_resp.output_text = "ok"
    fake_resp.status = "completed"
    fake_resp.usage = fake_usage

    req = httpx.Request("POST", "https://api.openai.com/v1/responses")
    rl = RateLimitError("rate limit", response=httpx.Response(429, request=req), body=None)

    with TestClient(application) as ac:
        ac.post(
            "/api/auth/login",
            json={"username": "seedadmin", "password": "seedpassword123"},
        )
        with patch("app.services.openai_client.OpenAI") as mock_cls:
            instance = MagicMock()
            instance.responses.create.side_effect = [rl, fake_resp]
            mock_cls.return_value = instance
            r = ac.post("/api/admin/openai/smoke", json={"prompt": "ping"})
    get_settings.cache_clear()

    assert r.status_code == 200
    assert r.json()["attempts_used"] == 2
    assert instance.responses.create.call_count == 2


def test_openapi_includes_openai_smoke_schemas(client: TestClient) -> None:
    r = client.get("/openapi.json")
    assert r.status_code == 200
    schemas = r.json().get("components", {}).get("schemas", {})
    assert "OpenAiSmokeRequest" in schemas
    assert "OpenAiSmokeResponse" in schemas

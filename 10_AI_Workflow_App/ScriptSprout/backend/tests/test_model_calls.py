"""model_calls table + admin list."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import httpx
from fastapi.testclient import TestClient
from openai import RateLimitError
from sqlalchemy import select

from app.db.models import ModelCall


def test_smoke_inserts_one_model_call_row(client_with_admin: TestClient, monkeypatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test-dummy-key-for-pytest")
    from app.config import get_settings

    get_settings.cache_clear()
    from app.main import create_app

    application = create_app()
    fake_usage = MagicMock()
    fake_usage.input_tokens = 3
    fake_usage.output_tokens = 4
    fake_usage.model_dump = MagicMock(return_value={})
    fake_resp = MagicMock()
    fake_resp.id = "resp_mc1"
    fake_resp.model = "gpt-4o-mini"
    fake_resp.output_text = "hi"
    fake_resp.status = "completed"
    fake_resp.usage = fake_usage

    with TestClient(application) as ac:
        ac.post(
            "/api/auth/login",
            json={"username": "seedadmin", "password": "seedpassword123"},
        )
        with patch("app.services.openai_client.OpenAI") as mock_cls:
            instance = MagicMock()
            instance.responses.create.return_value = fake_resp
            mock_cls.return_value = instance
            r = ac.post("/api/admin/openai/smoke", json={"prompt": "x"})
        assert r.status_code == 200

        r2 = ac.get("/api/admin/model-calls/")
    get_settings.cache_clear()

    assert r2.status_code == 200
    page = r2.json()
    assert page["total"] >= 1
    assert len(page["items"]) >= 1
    top = page["items"][0]
    assert top["success"] is True
    assert top["purpose"] == "admin_openai_smoke"
    assert top["operation_type"] == "responses_create"
    assert top["attempt_index"] == 1
    assert top["token_input"] == 3
    assert top["token_output"] == 4


def test_smoke_retry_writes_two_model_call_rows(client_with_admin: TestClient, monkeypatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test-dummy-key-for-pytest")
    from app.config import get_settings

    get_settings.cache_clear()
    from app.main import create_app

    application = create_app()
    fake_usage = MagicMock()
    fake_usage.input_tokens = 1
    fake_usage.output_tokens = 1
    fake_resp = MagicMock()
    fake_resp.id = "resp_ok"
    fake_resp.model = "gpt-4o-mini"
    fake_resp.output_text = "ok"
    fake_resp.status = "completed"
    fake_resp.usage = fake_usage

    req = httpx.Request("POST", "https://api.openai.com/v1/responses")
    rl = RateLimitError("rl", response=httpx.Response(429, request=req), body=None)

    with TestClient(application) as ac:
        ac.post(
            "/api/auth/login",
            json={"username": "seedadmin", "password": "seedpassword123"},
        )
        with patch("app.services.openai_client.OpenAI") as mock_cls:
            instance = MagicMock()
            instance.responses.create.side_effect = [rl, fake_resp]
            mock_cls.return_value = instance
            ac.post("/api/admin/openai/smoke", json={"prompt": "x"})

        r = ac.get("/api/admin/model-calls/", params={"limit": 10})
    get_settings.cache_clear()

    assert r.status_code == 200
    smoke_items = [x for x in r.json()["items"] if x["purpose"] == "admin_openai_smoke"]
    assert len(smoke_items) == 2
    by_attempt = {x["attempt_index"]: x for x in smoke_items}
    assert by_attempt[1]["success"] is False
    assert by_attempt[1]["error_type"] == "RateLimitError"
    assert by_attempt[2]["success"] is True


def test_model_calls_list_forbidden_for_author(client: TestClient) -> None:
    client.post(
        "/api/auth/register",
        json={"username": "author_mc", "password": "Password123"},
    )
    client.post(
        "/api/auth/login",
        json={"username": "author_mc", "password": "Password123"},
    )
    assert client.get("/api/admin/model-calls/").status_code == 403


def test_openapi_includes_model_call_schemas(client: TestClient) -> None:
    r = client.get("/openapi.json")
    assert r.status_code == 200
    schemas = r.json().get("components", {}).get("schemas", {})
    assert "ModelCallListItem" in schemas
    assert "ModelCallListPage" in schemas


def test_model_call_row_persisted_in_db(client_with_admin: TestClient, monkeypatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test-dummy-key-for-pytest")
    from app.config import get_settings

    get_settings.cache_clear()
    from app.main import create_app

    application = create_app()
    fake_resp = MagicMock()
    fake_resp.id = "resp_db"
    fake_resp.model = "gpt-4o-mini"
    fake_resp.output_text = "z"
    fake_resp.status = "completed"
    fake_resp.usage = None

    with TestClient(application) as ac:
        ac.post(
            "/api/auth/login",
            json={"username": "seedadmin", "password": "seedpassword123"},
        )
        with patch("app.services.openai_client.OpenAI") as mock_cls:
            instance = MagicMock()
            instance.responses.create.return_value = fake_resp
            mock_cls.return_value = instance
            ac.post("/api/admin/openai/smoke", json={"prompt": "z"})
        SessionLocal = application.state.SessionLocal
        with SessionLocal() as db:
            row = db.scalars(
                select(ModelCall).where(ModelCall.purpose == "admin_openai_smoke"),
            ).first()
            assert row is not None
            assert row.success is True
    get_settings.cache_clear()

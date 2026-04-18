"""Admin NLP orchestration route."""

from __future__ import annotations

from datetime import UTC
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from app.schemas.admin_nlp_query import AdminQueryPlanParsed
from app.services.admin_nlp_orchestration import _parse_metrics_iso


def _login_admin(c: TestClient) -> None:
    assert c.post(
        "/api/auth/login",
        json={"username": "seedadmin", "password": "seedpassword123"},
    ).status_code == 200


def _mock_parse_resp(plan: AdminQueryPlanParsed) -> MagicMock:
    pr = MagicMock()
    pr.output_parsed = plan
    pr.id = "resp_admin_nlp_1"
    pr.model = "gpt-5-nano"
    pr.usage = None
    return pr


def test_parse_metrics_iso_none_blank() -> None:
    assert _parse_metrics_iso(None) is None
    assert _parse_metrics_iso("") is None
    assert _parse_metrics_iso("   ") is None


def test_parse_metrics_iso_valid_z_suffix() -> None:
    dt = _parse_metrics_iso("2025-03-01T12:00:00Z")
    assert dt is not None
    assert dt.year == 2025 and dt.month == 3 and dt.day == 1
    assert dt.tzinfo == UTC


def test_parse_metrics_iso_invalid_returns_none() -> None:
    assert _parse_metrics_iso("not-a-date") is None
    assert _parse_metrics_iso("2025-99-99T00:00:00Z") is None


def test_admin_nlp_query_requires_auth(client: TestClient) -> None:
    r = client.post("/api/admin/nlp-query", json={"query": "How many stories?"})
    assert r.status_code == 401


def test_admin_nlp_query_author_forbidden(client: TestClient) -> None:
    client.post(
        "/api/auth/register",
        json={"username": "nlpq_author", "password": "Password123"},
    )
    client.post(
        "/api/auth/login",
        json={"username": "nlpq_author", "password": "Password123"},
    )
    r = client.post("/api/admin/nlp-query", json={"query": "How many stories?"})
    assert r.status_code == 403


def test_admin_nlp_query_503_without_key(client_with_admin: TestClient, monkeypatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    from app.config import get_settings

    get_settings.cache_clear()
    from app.main import create_app

    application = create_app()
    with TestClient(application) as ac:
        _login_admin(ac)
        r = ac.post("/api/admin/nlp-query", json={"query": "How many stories this week?"})
    get_settings.cache_clear()
    assert r.status_code == 503


def test_admin_nlp_query_metrics_only_mocked_openai(
    client_with_admin: TestClient,
    monkeypatch,
) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test-dummy-key-for-pytest")
    from app.config import get_settings

    get_settings.cache_clear()
    from app.main import create_app

    application = create_app()
    plan = AdminQueryPlanParsed(
        run_metrics=True,
        run_semantic_search=False,
        metrics_start_iso=None,
        metrics_end_iso=None,
        semantic_query=None,
        semantic_limit=10,
        semantic_genre=None,
        semantic_status=None,
        brief_summary="Weekly content aggregates.",
    )
    fake_pr = _mock_parse_resp(plan)

    with TestClient(application) as ac:
        _login_admin(ac)
        with patch("app.services.openai_client.OpenAI") as mock_cls:
            instance = MagicMock()
            instance.responses.parse.return_value = fake_pr
            mock_cls.return_value = instance
            r = ac.post(
                "/api/admin/nlp-query",
                json={"query": "How many stories this week by genre?"},
            )
    get_settings.cache_clear()

    assert r.status_code == 200
    body = r.json()
    assert body["query"] == "How many stories this week by genre?"
    assert body["plan_summary"] == "Weekly content aggregates."
    assert body["metrics"] is not None
    assert body["metrics"]["window"]["used_default_window"] is True
    assert "content" in body["metrics"]
    assert body["semantic_search"] is None
    assert body["parse_attempts_used"] == 1


def test_admin_nlp_query_forces_metrics_when_no_tools(
    client_with_admin: TestClient,
    monkeypatch,
) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test-dummy-key-for-pytest")
    from app.config import get_settings

    get_settings.cache_clear()
    from app.main import create_app

    application = create_app()
    plan = AdminQueryPlanParsed(
        run_metrics=False,
        run_semantic_search=False,
        metrics_start_iso=None,
        metrics_end_iso=None,
        semantic_query=None,
        semantic_limit=5,
        semantic_genre=None,
        semantic_status=None,
        brief_summary="Unclear intent",
    )
    fake_pr = _mock_parse_resp(plan)

    with TestClient(application) as ac:
        _login_admin(ac)
        with patch("app.services.openai_client.OpenAI") as mock_cls:
            instance = MagicMock()
            instance.responses.parse.return_value = fake_pr
            mock_cls.return_value = instance
            r = ac.post("/api/admin/nlp-query", json={"query": "Hello"})
    get_settings.cache_clear()

    assert r.status_code == 200
    body = r.json()
    assert body["metrics"] is not None
    assert "metrics default window" in body["plan_summary"].lower()


def test_admin_nlp_query_semantic_empty_index_mocked(
    client_with_admin: TestClient,
    monkeypatch,
) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test-dummy-key-for-pytest")
    from app.config import get_settings

    get_settings.cache_clear()
    from app.main import create_app

    application = create_app()
    plan = AdminQueryPlanParsed(
        run_metrics=False,
        run_semantic_search=True,
        metrics_start_iso=None,
        metrics_end_iso=None,
        semantic_query="robots on Mars",
        semantic_limit=3,
        semantic_genre=None,
        semantic_status=None,
        brief_summary="Thematic search.",
    )
    fake_pr = _mock_parse_resp(plan)

    with TestClient(application) as ac:
        _login_admin(ac)
        with patch("app.services.openai_client.OpenAI") as mock_cls:
            instance = MagicMock()
            instance.responses.parse.return_value = fake_pr
            mock_cls.return_value = instance
            r = ac.post(
                "/api/admin/nlp-query",
                json={"query": "Find stories about robots on Mars"},
            )
    get_settings.cache_clear()

    assert r.status_code == 200
    body = r.json()
    assert body["metrics"] is None
    assert body["semantic_search"] is not None
    assert body["semantic_search"]["items"] == []
    assert body["semantic_search"]["attempts_used"] == 0


def test_admin_nlp_query_invalid_metrics_iso_falls_back_to_default_window(
    client_with_admin: TestClient,
    monkeypatch,
) -> None:
    """Unparsable model metrics_*_iso must not 500; use default window like omitted bounds."""

    monkeypatch.setenv("OPENAI_API_KEY", "sk-test-dummy-key-for-pytest")
    from app.config import get_settings

    get_settings.cache_clear()
    from app.main import create_app

    application = create_app()
    plan = AdminQueryPlanParsed(
        run_metrics=True,
        run_semantic_search=False,
        metrics_start_iso="yesterday",
        metrics_end_iso="nope",
        semantic_query=None,
        semantic_limit=10,
        semantic_genre=None,
        semantic_status=None,
        brief_summary="Broken dates from model.",
    )
    fake_pr = _mock_parse_resp(plan)

    with TestClient(application) as ac:
        _login_admin(ac)
        with patch("app.services.openai_client.OpenAI") as mock_cls:
            instance = MagicMock()
            instance.responses.parse.return_value = fake_pr
            mock_cls.return_value = instance
            r = ac.post(
                "/api/admin/nlp-query",
                json={"query": "Counts with bad ISO from parse"},
            )
    get_settings.cache_clear()

    assert r.status_code == 200
    body = r.json()
    assert body["metrics"] is not None
    assert body["metrics"]["window"]["used_default_window"] is True

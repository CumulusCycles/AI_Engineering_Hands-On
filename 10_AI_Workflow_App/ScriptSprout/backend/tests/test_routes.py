"""Tests for health, meta, and OpenAPI routes (plus 404 envelope).

See also `test_auth.py`, `test_rbac.py`, `test_content.py`, `test_admin_content.py`.
When you add or change routes under `app/api/routes/`, extend these tests or add a focused module.
"""

import pytest
from fastapi.testclient import TestClient


def test_get_health_ok(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "scriptsprout"}


def test_openapi_json_exposes_health_and_error_schemas(client: TestClient) -> None:
    response = client.get("/openapi.json")
    assert response.status_code == 200
    body = response.json()
    assert "openapi" in body
    schemas = body.get("components", {}).get("schemas", {})
    assert "HealthResponse" in schemas
    assert "ErrorResponse" in schemas


def test_unknown_path_returns_error_envelope(client: TestClient) -> None:
    response = client.get("/no-such-route-for-test")
    assert response.status_code == 404
    assert response.json() == {
        "detail": "Not Found",
        "code": "http_404",
    }


def test_db_status_without_admin_credentials(client: TestClient) -> None:
    response = client.get("/api/meta/db-status")
    assert response.status_code == 200
    assert response.json() == {
        "database_reachable": True,
        "has_users": False,
    }


def test_db_status_with_seeded_admin(client_with_admin: TestClient) -> None:
    response = client_with_admin.get("/api/meta/db-status")
    assert response.status_code == 200
    body = response.json()
    assert body["database_reachable"] is True
    assert body["has_users"] is True


def test_validation_error_includes_multiple_fields(client: TestClient) -> None:
    """422 ``detail`` lists more than one issue when several fields fail validation."""

    r = client.post("/api/auth/register", json={"username": "a", "password": "short"})
    assert r.status_code == 422
    detail = r.json()["detail"]
    assert "username" in detail
    assert "password" in detail
    assert ";" in detail


def test_openapi_includes_db_status_schema(client: TestClient) -> None:
    response = client.get("/openapi.json")
    assert response.status_code == 200
    schemas = response.json().get("components", {}).get("schemas", {})
    assert "DbStatusResponse" in schemas


def test_security_headers_present_on_responses(client: TestClient) -> None:
    """Every response must include X-Content-Type-Options, X-Frame-Options, Referrer-Policy."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "DENY"
    assert response.headers["Referrer-Policy"] == "strict-origin-when-cross-origin"


def test_chroma_status_ok(client: TestClient) -> None:
    response = client.get("/api/meta/chroma-status")
    assert response.status_code == 200
    body = response.json()
    assert body["chroma_reachable"] is True
    assert body["collection_name"] == "content_semantic_index"
    assert body["document_count"] == 0
    assert body["planned_embedding_model"] == "text-embedding-3-small"
    assert "persist_path" in body


@pytest.mark.parametrize("path", ["/api/meta/db-status", "/api/meta/chroma-status"])
def test_meta_routes_hidden_when_expose_meta_false(tmp_path, monkeypatch, path: str) -> None:
    """Without EXPOSE_META_WITHOUT_AUTH, meta endpoints return 404 (safe default)."""

    monkeypatch.setenv("SQLITE_PATH", str(tmp_path / "meta_lock.db"))
    monkeypatch.setenv("CHROMA_PATH", str(tmp_path / "meta_chroma"))
    monkeypatch.delenv("EXPOSE_META_WITHOUT_AUTH", raising=False)
    monkeypatch.delenv("ADMIN_USERNAME", raising=False)
    monkeypatch.delenv("ADMIN_PASSWORD", raising=False)

    from app.config import get_settings

    get_settings.cache_clear()
    from app.main import create_app

    app = create_app()
    with TestClient(app) as ac:
        r = ac.get(path)
        assert r.status_code == 404
        assert r.json().get("code") == "http_404"
    get_settings.cache_clear()


def test_openapi_includes_chroma_status_schema(client: TestClient) -> None:
    response = client.get("/openapi.json")
    assert response.status_code == 200
    schemas = response.json().get("components", {}).get("schemas", {})
    assert "ChromaStatusResponse" in schemas


def test_openapi_includes_semantic_index_schema(client: TestClient) -> None:
    response = client.get("/openapi.json")
    assert response.status_code == 200
    schemas = response.json().get("components", {}).get("schemas", {})
    assert "UpsertSemanticIndexResponse" in schemas


def test_openapi_includes_semantic_search_schemas(client: TestClient) -> None:
    response = client.get("/openapi.json")
    assert response.status_code == 200
    body = response.json()
    assert "/api/search/semantic" in body.get("paths", {})
    schemas = body.get("components", {}).get("schemas", {})
    assert "SemanticSearchRequest" in schemas
    assert "SemanticSearchResponse" in schemas


def test_openapi_includes_admin_metrics_schema(client: TestClient) -> None:
    response = client.get("/openapi.json")
    assert response.status_code == 200
    body = response.json()
    assert "/api/admin/metrics" in body.get("paths", {})
    schemas = body.get("components", {}).get("schemas", {})
    assert "AdminMetricsResponse" in schemas
    assert "MetricsTimeWindow" in schemas


def test_openapi_includes_admin_nlp_query_schema(client: TestClient) -> None:
    response = client.get("/openapi.json")
    assert response.status_code == 200
    body = response.json()
    assert "/api/admin/nlp-query" in body.get("paths", {})
    schemas = body.get("components", {}).get("schemas", {})
    assert "AdminNlpQueryRequest" in schemas
    assert "AdminNlpQueryResponse" in schemas

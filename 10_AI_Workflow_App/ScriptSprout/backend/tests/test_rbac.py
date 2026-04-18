"""Role-based access: admin-only routes."""

from __future__ import annotations

from fastapi.testclient import TestClient


def test_admin_ping_without_session_returns_401(client: TestClient) -> None:
    r = client.get("/api/admin/ping")
    assert r.status_code == 401
    assert r.json()["code"] == "http_401"


def test_admin_ping_author_session_returns_403(client: TestClient) -> None:
    client.post(
        "/api/auth/register",
        json={"username": "author_rbac", "password": "Password123"},
    )
    client.post(
        "/api/auth/login",
        json={"username": "author_rbac", "password": "Password123"},
    )
    r = client.get("/api/admin/ping")
    assert r.status_code == 403
    assert r.json()["code"] == "http_403"
    assert "Insufficient" in r.json()["detail"]


def test_admin_ping_admin_session_returns_200(client_with_admin: TestClient) -> None:
    client_with_admin.post(
        "/api/auth/login",
        json={"username": "seedadmin", "password": "seedpassword123"},
    )
    r = client_with_admin.get("/api/admin/ping")
    assert r.status_code == 200
    assert r.json() == {"scope": "admin", "message": "ok"}


def test_openapi_includes_admin_ping_schema(client: TestClient) -> None:
    r = client.get("/openapi.json")
    assert r.status_code == 200
    schemas = r.json().get("components", {}).get("schemas", {})
    assert "AdminPingResponse" in schemas


def test_openapi_admin_tag_describes_surface(client: TestClient) -> None:
    """The bundled **admin** tag text should reflect real routers, not only ping + content."""

    r = client.get("/openapi.json")
    assert r.status_code == 200
    tags = r.json().get("tags") or []
    admin = next(t for t in tags if t.get("name") == "admin")
    desc = (admin.get("description") or "").lower()
    assert "cleanse" in desc
    assert "metrics" in desc
    assert "nlp-query" in desc
    assert "generation-runs" in desc
    assert "model-calls" in desc

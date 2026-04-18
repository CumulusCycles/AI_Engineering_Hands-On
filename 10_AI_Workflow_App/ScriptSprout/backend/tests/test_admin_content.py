"""Admin read-only content browse."""

from __future__ import annotations

from fastapi.testclient import TestClient


def test_admin_content_list_empty_when_no_rows(client_with_admin: TestClient) -> None:
    assert (
        client_with_admin.post(
            "/api/auth/login",
            json={"username": "seedadmin", "password": "seedpassword123"},
        ).status_code
        == 200
    )
    r = client_with_admin.get("/api/admin/content/")
    assert r.status_code == 200
    body = r.json()
    assert body["items"] == []
    assert body["total"] == 0
    assert body["limit"] == 100
    assert body["offset"] == 0


def test_admin_sees_author_content_list_and_detail(client_with_admin: TestClient) -> None:
    assert (
        client_with_admin.post(
            "/api/auth/register",
            json={"username": "writer_one", "password": "Password123"},
        ).status_code
        == 201
    )
    assert (
        client_with_admin.post(
            "/api/auth/login",
            json={"username": "writer_one", "password": "Password123"},
        ).status_code
        == 200
    )
    r = client_with_admin.post(
        "/api/content/",
        json={"prompt": "admin should see this prompt text"},
    )
    assert r.status_code == 201
    cid = r.json()["id"]
    client_with_admin.post("/api/auth/logout")

    assert (
        client_with_admin.post(
            "/api/auth/login",
            json={"username": "seedadmin", "password": "seedpassword123"},
        ).status_code
        == 200
    )
    r = client_with_admin.get("/api/admin/content/")
    assert r.status_code == 200
    page = r.json()
    assert page["total"] == 1
    assert len(page["items"]) == 1
    item = page["items"][0]
    assert item["id"] == cid
    assert item["author_username"] == "writer_one"
    assert "admin should see" in item["prompt_preview"]

    r = client_with_admin.get(f"/api/admin/content/{cid}")
    assert r.status_code == 200
    detail = r.json()
    assert detail["id"] == cid
    assert detail["author_username"] == "writer_one"
    assert detail["source_prompt"] == "admin should see this prompt text"


def test_admin_content_list_filter_by_author_id(client_with_admin: TestClient) -> None:
    client_with_admin.post(
        "/api/auth/register",
        json={"username": "writer_two", "password": "Password123"},
    )
    client_with_admin.post(
        "/api/auth/login",
        json={"username": "writer_two", "password": "Password123"},
    )
    r = client_with_admin.post("/api/content/", json={"prompt": "only writer two"})
    assert r.status_code == 201
    aid = r.json()["author_id"]
    client_with_admin.post("/api/auth/logout")
    assert (
        client_with_admin.post(
            "/api/auth/login",
            json={"username": "seedadmin", "password": "seedpassword123"},
        ).status_code
        == 200
    )
    r = client_with_admin.get("/api/admin/content/", params={"author_id": aid})
    assert r.status_code == 200
    assert r.json()["total"] == 1


def test_admin_content_list_status_normalized(client_with_admin: TestClient) -> None:
    """Admin ``status`` query uses the same trim / blank-as-none rules as author list."""

    assert (
        client_with_admin.post(
            "/api/auth/register",
            json={"username": "status_norm_writer", "password": "Password123"},
        ).status_code
        == 201
    )
    assert (
        client_with_admin.post(
            "/api/auth/login",
            json={"username": "status_norm_writer", "password": "Password123"},
        ).status_code
        == 200
    )
    assert client_with_admin.post("/api/content/", json={"prompt": "x"}).status_code == 201
    client_with_admin.post("/api/auth/logout")
    assert (
        client_with_admin.post(
            "/api/auth/login",
            json={"username": "seedadmin", "password": "seedpassword123"},
        ).status_code
        == 200
    )
    r = client_with_admin.get("/api/admin/content/", params={"status": "  draft  "})
    assert r.status_code == 200
    assert r.json()["total"] == 1
    r = client_with_admin.get("/api/admin/content/", params={"status": "   "})
    assert r.status_code == 200
    assert r.json()["total"] == 1


def test_author_forbidden_admin_content_routes(client: TestClient) -> None:
    client.post(
        "/api/auth/register",
        json={"username": "solo_writer", "password": "Password123"},
    )
    client.post(
        "/api/auth/login",
        json={"username": "solo_writer", "password": "Password123"},
    )
    r = client.get("/api/admin/content/")
    assert r.status_code == 403
    r = client.get("/api/admin/content/1")
    assert r.status_code == 403


def test_admin_content_detail_not_found(client_with_admin: TestClient) -> None:
    assert (
        client_with_admin.post(
            "/api/auth/login",
            json={"username": "seedadmin", "password": "seedpassword123"},
        ).status_code
        == 200
    )
    r = client_with_admin.get("/api/admin/content/999999")
    assert r.status_code == 404


def test_openapi_includes_admin_content_schemas(client: TestClient) -> None:
    r = client.get("/openapi.json")
    assert r.status_code == 200
    body = r.json()
    schemas = body.get("components", {}).get("schemas", {})
    assert "AdminContentListItem" in schemas
    assert "AdminContentListPage" in schemas
    assert "AdminContentItemDetail" in schemas
    status_param = next(
        p
        for p in body["paths"]["/api/admin/content/"]["get"].get("parameters", [])
        if p.get("name") == "status"
    )
    assert "trim" in status_param.get("description", "").lower()

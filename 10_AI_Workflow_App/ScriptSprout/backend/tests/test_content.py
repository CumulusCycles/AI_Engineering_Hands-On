"""Content items: author API list/detail behavior."""

from __future__ import annotations

from fastapi.testclient import TestClient

from app.schemas.content import PROMPT_PREVIEW_MAX_LEN


def _register_login_author(client: TestClient, username: str, password: str) -> None:
    assert (
        client.post(
            "/api/auth/register",
            json={"username": username, "password": password},
        ).status_code
        == 201
    )
    assert (
        client.post(
            "/api/auth/login",
            json={"username": username, "password": password},
        ).status_code
        == 200
    )


def test_create_list_get_with_prompt_shell(client: TestClient) -> None:
    _register_login_author(client, "content_author", "Password123")
    payload = {
        "prompt": "A cozy mystery on a ferry",
        "genre": "mystery",
        "guardrails_max_loops": 5,
    }
    r = client.post("/api/content/", json=payload)
    assert r.status_code == 201
    body = r.json()
    assert body["author_id"] >= 1
    assert body["source_prompt"] == payload["prompt"]
    assert body["genre"] == "mystery"
    assert body["status"] == "draft"
    assert body["guardrails_enabled"] is True
    assert body["guardrails_max_loops"] == 5
    assert body["has_thumbnail"] is False
    assert body["has_audio"] is False
    cid = body["id"]

    r = client.get("/api/content/")
    assert r.status_code == 200
    page = r.json()
    assert page["total"] == 1
    assert page["limit"] == 100
    assert page["offset"] == 0
    assert len(page["items"]) == 1
    item = page["items"][0]
    assert item["id"] == cid
    assert item["prompt_preview"] == payload["prompt"]
    assert "source_prompt" not in item

    r = client.get(f"/api/content/{cid}")
    assert r.status_code == 200
    assert r.json()["id"] == cid
    assert r.json()["source_prompt"] == payload["prompt"]


def test_create_accepts_legacy_source_prompt(client: TestClient) -> None:
    _register_login_author(client, "legacy_author", "Password123")
    r = client.post(
        "/api/content/",
        json={"source_prompt": "legacy field still works"},
    )
    assert r.status_code == 201
    assert r.json()["source_prompt"] == "legacy field still works"


def test_create_requires_prompt_or_source_prompt(client: TestClient) -> None:
    _register_login_author(client, "empty_prompt_author", "Password123")
    r = client.post("/api/content/", json={"genre": "x"})
    assert r.status_code == 422


def test_list_status_filter(client: TestClient) -> None:
    _register_login_author(client, "filter_author", "Password123")
    client.post("/api/content/", json={"prompt": "one"})
    client.post("/api/content/", json={"prompt": "two"})
    r = client.get("/api/content/", params={"status": "draft"})
    assert r.status_code == 200
    assert r.json()["total"] == 2
    r = client.get("/api/content/", params={"status": "  draft  "})
    assert r.status_code == 200
    assert r.json()["total"] == 2
    r = client.get("/api/content/", params={"status": "ready"})
    assert r.status_code == 200
    assert r.json()["total"] == 0
    assert r.json()["items"] == []


def test_list_status_whitespace_only_means_no_filter(client: TestClient) -> None:
    """Blank ``status`` after trim must not over-filter (matches shared normalizer)."""

    _register_login_author(client, "blank_status_author", "Password123")
    client.post("/api/content/", json={"prompt": "only draft rows"})
    r = client.get("/api/content/", params={"status": "   "})
    assert r.status_code == 200
    assert r.json()["total"] == 1


def test_prompt_preview_truncates(client: TestClient) -> None:
    _register_login_author(client, "long_prompt_author", "Password123")
    long_text = "x" * (PROMPT_PREVIEW_MAX_LEN + 50)
    r = client.post("/api/content/", json={"prompt": long_text})
    assert r.status_code == 201
    r = client.get("/api/content/")
    preview = r.json()["items"][0]["prompt_preview"]
    assert len(preview) == PROMPT_PREVIEW_MAX_LEN
    assert preview.endswith("…")


def test_get_content_not_found(client: TestClient) -> None:
    _register_login_author(client, "solo_author", "Password123")
    r = client.get("/api/content/99999")
    assert r.status_code == 404
    assert r.json()["code"] == "http_404"


def test_get_other_author_content_not_found(client: TestClient) -> None:
    _register_login_author(client, "author_alpha", "Password123")
    r = client.post("/api/content/", json={"prompt": "alpha story"})
    assert r.status_code == 201
    cid = r.json()["id"]
    client.post("/api/auth/logout")

    _register_login_author(client, "author_beta", "Password123")
    r = client.get(f"/api/content/{cid}")
    assert r.status_code == 404
    assert r.json()["code"] == "http_404"


def test_admin_cannot_access_content_routes(client_with_admin: TestClient) -> None:
    assert (
        client_with_admin.post(
            "/api/auth/login",
            json={"username": "seedadmin", "password": "seedpassword123"},
        ).status_code
        == 200
    )
    r = client_with_admin.post("/api/content/", json={"prompt": "admin tries"})
    assert r.status_code == 403
    r = client_with_admin.get("/api/content/")
    assert r.status_code == 403


def test_content_requires_login(client: TestClient) -> None:
    r = client.get("/api/content/")
    assert r.status_code == 401
    r = client.post("/api/content/", json={"prompt": "x"})
    assert r.status_code == 401


def test_openapi_includes_content_schemas(client: TestClient) -> None:
    r = client.get("/openapi.json")
    assert r.status_code == 200
    body = r.json()
    schemas = body.get("components", {}).get("schemas", {})
    assert "ContentCreate" in schemas
    assert "ContentListItem" in schemas
    assert "ContentListPage" in schemas
    assert "ContentItemDetail" in schemas
    status_param = next(
        p
        for p in body["paths"]["/api/content/"]["get"].get("parameters", [])
        if p.get("name") == "status"
    )
    assert "trim" in status_param.get("description", "").lower()

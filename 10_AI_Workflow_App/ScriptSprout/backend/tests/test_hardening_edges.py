"""Additional auth/ownership hardening checks for protected content routes."""

from __future__ import annotations

from fastapi.testclient import TestClient


def _register_login(client: TestClient, username: str, password: str) -> None:
    assert client.post(
        "/api/auth/register",
        json={"username": username, "password": password},
    ).status_code == 201
    assert client.post(
        "/api/auth/login",
        json={"username": username, "password": password},
    ).status_code == 200


def test_stale_cookie_rejected_for_protected_content_routes(tmp_path, monkeypatch) -> None:
    """A stale session cookie must fail with 401 on protected content routes."""

    monkeypatch.setenv("SQLITE_PATH", str(tmp_path / "sess.db"))
    monkeypatch.setenv("CHROMA_PATH", str(tmp_path / "chroma"))
    monkeypatch.delenv("ADMIN_USERNAME", raising=False)
    monkeypatch.delenv("ADMIN_PASSWORD", raising=False)

    from app.config import get_settings

    get_settings.cache_clear()
    from app.main import create_app

    application = create_app()
    creds = {"username": "stale_user", "password": "Password123"}
    with TestClient(application) as client:
        assert client.post("/api/auth/register", json=creds).status_code == 201
        assert client.post("/api/auth/login", json=creds).status_code == 200
        stale_session = client.cookies.get("scriptsprout_session")
        assert stale_session
        # second login revokes prior sessions
        assert client.post("/api/auth/login", json=creds).status_code == 200
        client.cookies.clear()

        r = client.get(
            "/api/content/",
            headers={"Cookie": f"scriptsprout_session={stale_session}"},
        )
        assert r.status_code == 401

        r2 = client.post(
            "/api/content/",
            json={"prompt": "should fail"},
            headers={"Cookie": f"scriptsprout_session={stale_session}"},
        )
        assert r2.status_code == 401

    get_settings.cache_clear()


def test_other_author_cannot_run_generate_or_mutate_routes(client: TestClient) -> None:
    """Ownership checks should return 404 for non-owner workflow actions."""

    _register_login(client, "owner_user", "Password123")
    create = client.post("/api/content/", json={"prompt": "owner prompt"})
    assert create.status_code == 201
    cid = create.json()["id"]

    client.post("/api/auth/logout")
    _register_login(client, "stranger_user", "Password456")

    protected_calls = [
        ("post", f"/api/content/{cid}/generate-synopsis", None),
        ("post", f"/api/content/{cid}/generate-title", None),
        ("post", f"/api/content/{cid}/generate-description", None),
        ("post", f"/api/content/{cid}/generate-story", None),
        ("post", f"/api/content/{cid}/generate-thumbnail", None),
        ("post", f"/api/content/{cid}/generate-audio", {}),
        ("post", f"/api/content/{cid}/approve-step", {"step": "synopsis"}),
        ("post", f"/api/content/{cid}/regenerate-step", {"step": "synopsis"}),
        ("get", f"/api/content/{cid}/thumbnail", None),
        ("get", f"/api/content/{cid}/audio", None),
        ("post", f"/api/content/{cid}/semantic-index", None),
    ]
    for method, path, payload in protected_calls:
        if method == "get":
            resp = client.get(path)
        elif payload is None:
            resp = client.post(path)
        else:
            resp = client.post(path, json=payload)
        assert resp.status_code == 404

"""Auth routes: register, login (cookie), me, logout."""

from __future__ import annotations

from unittest.mock import patch

from fastapi.testclient import TestClient
from sqlalchemy import select

from app.auth.password import hash_password
from app.db.models import User

_FIXED_TOKEN = "fixed-test-token-for-verification"


def test_register_login_me_logout_flow(client: TestClient) -> None:
    r = client.post(
        "/api/auth/register",
        json={"username": "author_one", "password": "Secretpass1"},
    )
    assert r.status_code == 201
    body = r.json()
    assert body["username"] == "author_one"
    assert body["role"] == "author"
    assert body["verification_required"] is True

    with patch("app.api.routes.auth.secrets.token_urlsafe", return_value=_FIXED_TOKEN):
        r = client.post(
            "/api/auth/email-verification/request",
            json={"username": "author_one", "email": "author_one@example.com"},
        )
    assert r.status_code == 200
    body = r.json()
    assert body["preview_token"] == _FIXED_TOKEN

    r = client.post(
        "/api/auth/email-verification/confirm",
        json={"username": "author_one", "token": _FIXED_TOKEN},
    )
    assert r.status_code == 200

    r = client.post(
        "/api/auth/login",
        json={"username": "author_one", "password": "Secretpass1"},
    )
    assert r.status_code == 200
    assert r.json()["username"] == "author_one"
    assert "scriptsprout_session" in r.cookies

    r = client.get("/api/auth/me")
    assert r.status_code == 200
    assert r.json()["username"] == "author_one"

    r = client.post("/api/auth/logout")
    assert r.status_code == 204

    r = client.get("/api/auth/me")
    assert r.status_code == 401


def test_register_duplicate_username_conflict(client: TestClient) -> None:
    payload = {"username": "dup_user", "password": "Password123"}
    assert client.post("/api/auth/register", json=payload).status_code == 201
    r = client.post("/api/auth/register", json=payload)
    assert r.status_code == 409
    assert r.json()["code"] == "http_409"


def test_login_invalid_credentials(client: TestClient) -> None:
    client.post(
        "/api/auth/register",
        json={"username": "user_two", "password": "Password123"},
    )
    r = client.post(
        "/api/auth/login",
        json={"username": "user_two", "password": "wrongpassword"},
    )
    assert r.status_code == 401
    assert r.json()["code"] == "http_401"


def test_login_blocked_until_email_verified_when_required(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("SQLITE_PATH", str(tmp_path / "verify.db"))
    monkeypatch.setenv("CHROMA_PATH", str(tmp_path / "chroma"))
    monkeypatch.setenv("EXPOSE_META_WITHOUT_AUTH", "true")
    monkeypatch.setenv("AUTHOR_EMAIL_VERIFICATION_REQUIRED", "true")
    monkeypatch.delenv("ADMIN_USERNAME", raising=False)
    monkeypatch.delenv("ADMIN_PASSWORD", raising=False)

    from app.config import get_settings

    get_settings.cache_clear()
    from app.main import create_app

    application = create_app()
    with TestClient(application) as client:
        creds = {"username": "needs_verify", "password": "Password123"}
        assert client.post("/api/auth/register", json=creds).status_code == 201
        blocked = client.post("/api/auth/login", json=creds)
        assert blocked.status_code == 403
        assert "verification" in blocked.json()["detail"].lower()

        with patch("app.api.routes.auth.secrets.token_urlsafe", return_value=_FIXED_TOKEN):
            req = client.post(
                "/api/auth/email-verification/request",
                json={"username": "needs_verify", "email": "needs_verify@example.com"},
            )
        assert req.json()["preview_token"] == _FIXED_TOKEN
        assert (
            client.post(
                "/api/auth/email-verification/confirm",
                json={"username": "needs_verify", "token": _FIXED_TOKEN},
            ).status_code
            == 200
        )
        assert client.post("/api/auth/login", json=creds).status_code == 200
    get_settings.cache_clear()


def test_me_without_session_returns_401(client: TestClient) -> None:
    r = client.get("/api/auth/me")
    assert r.status_code == 401


def test_logout_without_cookie_is_idempotent(client: TestClient) -> None:
    r = client.post("/api/auth/logout")
    assert r.status_code == 204


def test_login_revokes_prior_sessions_for_same_user(tmp_path, monkeypatch) -> None:
    """A second login invalidates earlier session cookies for that account."""

    monkeypatch.setenv("SQLITE_PATH", str(tmp_path / "sess.db"))
    monkeypatch.setenv("CHROMA_PATH", str(tmp_path / "chroma"))
    monkeypatch.delenv("ADMIN_USERNAME", raising=False)
    monkeypatch.delenv("ADMIN_PASSWORD", raising=False)

    from app.config import get_settings

    get_settings.cache_clear()
    from app.main import create_app

    application = create_app()
    login_json = {"username": "solo", "password": "Password123"}
    with TestClient(application) as client:
        assert client.post("/api/auth/register", json=login_json).status_code == 201
        assert client.post("/api/auth/login", json=login_json).status_code == 200
        stale_session = client.cookies.get("scriptsprout_session")
        assert stale_session
        assert client.get("/api/auth/me").status_code == 200

        assert client.post("/api/auth/login", json=login_json).status_code == 200
        assert client.get("/api/auth/me").status_code == 200

        client.cookies.clear()
        r_stale = client.get(
            "/api/auth/me",
            headers={"Cookie": f"scriptsprout_session={stale_session}"},
        )
        assert r_stale.status_code == 401

    get_settings.cache_clear()


def test_openapi_includes_user_response_schema(client: TestClient) -> None:
    r = client.get("/openapi.json")
    assert r.status_code == 200
    schemas = r.json().get("components", {}).get("schemas", {})
    assert "UserResponse" in schemas


def test_seeded_admin_can_login_and_me(client_with_admin: TestClient) -> None:
    r = client_with_admin.post(
        "/api/auth/login",
        json={"username": "seedadmin", "password": "seedpassword123"},
    )
    assert r.status_code == 200
    assert r.json()["role"] == "admin"
    r = client_with_admin.get("/api/auth/me")
    assert r.status_code == 200
    assert r.json()["username"] == "seedadmin"


def test_user_updated_at_advances_on_orm_update(client_with_admin: TestClient) -> None:
    """ORM `onupdate` keeps `updated_at` meaningful when rows change (local SQLite timestamps)."""

    application = client_with_admin.app
    with application.state.SessionLocal() as db:
        user = db.scalar(select(User).where(User.username == "seedadmin"))
        assert user is not None
        before = user.updated_at
    with application.state.SessionLocal() as db:
        user = db.scalar(select(User).where(User.username == "seedadmin"))
        assert user is not None
        user.password_hash = hash_password("seedpassword123")
        db.commit()
        db.refresh(user)
        after = user.updated_at
    assert after >= before


def test_auth_rate_limiting_returns_429(tmp_path, monkeypatch) -> None:
    """Auth endpoints return 429 when per-IP rate limit is exceeded."""
    monkeypatch.setenv("SQLITE_PATH", str(tmp_path / "rl.db"))
    monkeypatch.setenv("CHROMA_PATH", str(tmp_path / "chroma"))
    monkeypatch.setenv("AUTH_RATE_LIMIT", "3/minute")
    monkeypatch.delenv("ADMIN_USERNAME", raising=False)
    monkeypatch.delenv("ADMIN_PASSWORD", raising=False)

    from app.config import get_settings
    from app.rate_limit import reset_rate_limiter

    get_settings.cache_clear()
    reset_rate_limiter()
    from app.main import create_app

    application = create_app()
    with TestClient(application) as client:
        for i in range(3):
            r = client.post(
                "/api/auth/register",
                json={"username": f"rl_user_{i}", "password": "Password123"},
            )
            assert r.status_code == 201, f"request {i} should succeed"
        r = client.post(
            "/api/auth/register",
            json={"username": "rl_user_blocked", "password": "Password123"},
        )
        assert r.status_code == 429
        assert r.headers.get("Retry-After") == "60"
    get_settings.cache_clear()
    reset_rate_limiter()


def test_email_verification_response_contains_preview_token(client: TestClient) -> None:
    """Verification request response includes preview_token for demo use."""
    client.post(
        "/api/auth/register",
        json={"username": "tok_demo", "password": "Password123"},
    )
    r = client.post(
        "/api/auth/email-verification/request",
        json={"username": "tok_demo", "email": "tok_demo@example.com"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["preview_token"] is not None
    assert len(body["preview_token"]) > 0
    assert body["delivery_channel"] == "email"


# --- password complexity ---


def test_register_rejects_password_without_uppercase(client: TestClient) -> None:
    """Password must contain at least one uppercase letter."""
    r = client.post(
        "/api/auth/register",
        json={"username": "weak_pass_user", "password": "alllowercase1"},
    )
    assert r.status_code == 422
    assert "uppercase" in r.json()["detail"].lower()


def test_register_rejects_password_without_lowercase(client: TestClient) -> None:
    r = client.post(
        "/api/auth/register",
        json={"username": "weak_pass_user2", "password": "ALLUPPERCASE1"},
    )
    assert r.status_code == 422
    assert "lowercase" in r.json()["detail"].lower()


def test_register_rejects_password_without_digit(client: TestClient) -> None:
    r = client.post(
        "/api/auth/register",
        json={"username": "weak_pass_user3", "password": "NoDigitsHere"},
    )
    assert r.status_code == 422
    assert "digit" in r.json()["detail"].lower()


def test_register_accepts_strong_password(client: TestClient) -> None:
    r = client.post(
        "/api/auth/register",
        json={"username": "strong_pass_user", "password": "Strong1Pass"},
    )
    assert r.status_code == 201


# --- account lockout ---


def test_account_lockout_after_repeated_failures(tmp_path, monkeypatch) -> None:
    """Account is locked after MAX_FAILED_LOGINS consecutive bad attempts."""
    monkeypatch.setenv("SQLITE_PATH", str(tmp_path / "lock.db"))
    monkeypatch.setenv("CHROMA_PATH", str(tmp_path / "chroma"))
    monkeypatch.setenv("MAX_FAILED_LOGINS", "3")
    monkeypatch.setenv("ACCOUNT_LOCKOUT_MINUTES", "15")
    monkeypatch.delenv("ADMIN_USERNAME", raising=False)
    monkeypatch.delenv("ADMIN_PASSWORD", raising=False)

    from app.config import get_settings

    get_settings.cache_clear()
    from app.main import create_app

    application = create_app()
    with TestClient(application) as client:
        client.post(
            "/api/auth/register",
            json={"username": "lockme", "password": "GoodPass123"},
        )
        # 3 bad attempts
        for _ in range(3):
            r = client.post(
                "/api/auth/login",
                json={"username": "lockme", "password": "WrongPass999"},
            )
            assert r.status_code == 401

        # 4th attempt — account should be locked (403)
        r = client.post(
            "/api/auth/login",
            json={"username": "lockme", "password": "GoodPass123"},
        )
        assert r.status_code == 403
        assert "locked" in r.json()["detail"].lower()
    get_settings.cache_clear()


# --- change password ---


def _register_and_login(
    client: TestClient, username: str = "cpuser", password: str = "Password1",
) -> None:
    """Register a user and log in (sets session cookie on client)."""
    client.post("/api/auth/register", json={"username": username, "password": password})
    client.post("/api/auth/login", json={"username": username, "password": password})


def test_change_password_success_revokes_session(client: TestClient) -> None:
    _register_and_login(client, "cp_ok", "OldPass1")
    r = client.put(
        "/api/auth/password",
        json={"current_password": "OldPass1", "new_password": "NewPass2"},
    )
    assert r.status_code == 200
    assert "changed" in r.json()["message"].lower()
    # Session should be revoked
    assert client.get("/api/auth/me").status_code == 401
    # Old password should no longer work
    r = client.post("/api/auth/login", json={"username": "cp_ok", "password": "OldPass1"})
    assert r.status_code == 401
    # New password should work
    r = client.post("/api/auth/login", json={"username": "cp_ok", "password": "NewPass2"})
    assert r.status_code == 200


def test_change_password_wrong_current_returns_401(client: TestClient) -> None:
    _register_and_login(client, "cp_wrong", "CorrectPass1")
    r = client.put(
        "/api/auth/password",
        json={"current_password": "WrongPass9", "new_password": "AnyPass1"},
    )
    assert r.status_code == 401
    assert "incorrect" in r.json()["detail"].lower()


def test_change_password_weak_new_password_returns_422(client: TestClient) -> None:
    _register_and_login(client, "cp_weak", "GoodPass1")
    r = client.put(
        "/api/auth/password",
        json={"current_password": "GoodPass1", "new_password": "nodigit"},
    )
    assert r.status_code == 422


def test_change_password_unauthenticated_returns_401(client: TestClient) -> None:
    r = client.put(
        "/api/auth/password",
        json={"current_password": "a", "new_password": "Whatever1"},
    )
    assert r.status_code == 401


# --- change email ---


def test_change_email_success(client: TestClient) -> None:
    _register_and_login(client, "ce_ok", "Password1")
    r = client.put(
        "/api/auth/email",
        json={"new_email": "new_email@example.com"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["delivery_channel"] == "email"
    # email_verified should now be False — check via /me
    me = client.get("/api/auth/me").json()
    assert me["email"] == "new_email@example.com"
    assert me["email_verified"] is False


def test_change_email_duplicate_returns_409(client: TestClient) -> None:
    """Changing to an email already used by another user returns 409."""
    client.post("/api/auth/register", json={"username": "ce_other", "password": "Password1"})
    client.post("/api/auth/login", json={"username": "ce_other", "password": "Password1"})
    client.put("/api/auth/email", json={"new_email": "taken@example.com"})
    client.post("/api/auth/logout")

    _register_and_login(client, "ce_dup", "Password1")
    r = client.put("/api/auth/email", json={"new_email": "taken@example.com"})
    assert r.status_code == 409
    assert "already" in r.json()["detail"].lower()


def test_change_email_invalid_format_returns_422(client: TestClient) -> None:
    _register_and_login(client, "ce_bad", "Password1")
    r = client.put("/api/auth/email", json={"new_email": "not-an-email"})
    assert r.status_code == 422


def test_change_email_unauthenticated_returns_401(client: TestClient) -> None:
    r = client.put("/api/auth/email", json={"new_email": "x@y.com"})
    assert r.status_code == 401


def test_successful_login_resets_failed_counter(client: TestClient) -> None:
    """A successful login clears the failed-attempt counter."""
    client.post(
        "/api/auth/register",
        json={"username": "reset_counter", "password": "GoodPass123"},
    )
    # 2 bad attempts
    for _ in range(2):
        client.post(
            "/api/auth/login",
            json={"username": "reset_counter", "password": "WrongPass999"},
        )
    # succeed
    r = client.post(
        "/api/auth/login",
        json={"username": "reset_counter", "password": "GoodPass123"},
    )
    assert r.status_code == 200

    # 2 more bad attempts — should NOT lock (counter was reset)
    for _ in range(2):
        client.post(
            "/api/auth/login",
            json={"username": "reset_counter", "password": "WrongPass999"},
        )
    r = client.post(
        "/api/auth/login",
        json={"username": "reset_counter", "password": "GoodPass123"},
    )
    assert r.status_code == 200

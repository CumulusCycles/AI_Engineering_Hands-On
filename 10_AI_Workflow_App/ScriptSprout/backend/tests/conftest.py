"""Pytest does not require a running server (`TestClient` starts the app in-process).

Repo-root `.env` is ignored while tests run (`Settings.settings_customise_sources`) so
`monkeypatch.delenv` / `setenv` fully control config (e.g. admin seed on/off).
"""

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(autouse=True)
def _reset_rate_limiter():
    """Clear in-process rate-limit counters between tests."""
    from app.rate_limit import reset_rate_limiter

    reset_rate_limiter()
    yield
    reset_rate_limiter()


@pytest.fixture
def client(tmp_path, monkeypatch):
    """Isolated SQLite under tmp_path; no admin seed unless env vars are set in the test."""
    monkeypatch.setenv("SQLITE_PATH", str(tmp_path / "test.db"))
    monkeypatch.setenv("CHROMA_PATH", str(tmp_path / "chroma"))
    # Match local dev ergonomics: tests expect unauthenticated meta unless a case opts out.
    monkeypatch.setenv("EXPOSE_META_WITHOUT_AUTH", "true")
    monkeypatch.setenv("AUTHOR_EMAIL_VERIFICATION_REQUIRED", "false")
    monkeypatch.delenv("ADMIN_USERNAME", raising=False)
    monkeypatch.delenv("ADMIN_PASSWORD", raising=False)

    from app.config import get_settings

    get_settings.cache_clear()
    from app.main import create_app

    application = create_app()
    with TestClient(application) as test_client:
        yield test_client
    get_settings.cache_clear()


@pytest.fixture
def client_with_admin(tmp_path, monkeypatch):
    """SQLite + admin user seeded from env."""
    monkeypatch.setenv("SQLITE_PATH", str(tmp_path / "test.db"))
    monkeypatch.setenv("CHROMA_PATH", str(tmp_path / "chroma"))
    monkeypatch.setenv("EXPOSE_META_WITHOUT_AUTH", "true")
    monkeypatch.setenv("AUTHOR_EMAIL_VERIFICATION_REQUIRED", "false")
    monkeypatch.setenv("ADMIN_USERNAME", "seedadmin")
    monkeypatch.setenv("ADMIN_PASSWORD", "seedpassword123")

    from app.config import get_settings

    get_settings.cache_clear()
    from app.main import create_app

    application = create_app()
    with TestClient(application) as test_client:
        yield test_client
    get_settings.cache_clear()

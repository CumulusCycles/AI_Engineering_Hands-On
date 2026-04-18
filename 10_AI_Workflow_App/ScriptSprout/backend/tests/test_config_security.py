"""Settings validation for deployment-hardening rules."""

from __future__ import annotations

import pytest


def test_production_requires_secure_session_cookie(monkeypatch: pytest.MonkeyPatch) -> None:
    """APP_ENV=production must use SESSION_COOKIE_SECURE=true."""

    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("SESSION_COOKIE_SECURE", "false")
    from app.config import get_settings

    get_settings.cache_clear()
    with pytest.raises(ValueError, match="SESSION_COOKIE_SECURE"):
        get_settings()
    get_settings.cache_clear()


def test_production_accepts_secure_session_cookie(monkeypatch: pytest.MonkeyPatch) -> None:
    """Production with Secure cookies loads."""

    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("SESSION_COOKIE_SECURE", "true")
    from app.config import get_settings

    get_settings.cache_clear()
    s = get_settings()
    assert s.app_environment == "production"
    assert s.session_cookie_secure is True
    get_settings.cache_clear()




def test_admin_password_too_short_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    """ADMIN_PASSWORD under 12 characters is rejected."""
    monkeypatch.setenv("ADMIN_USERNAME", "myadmin")
    monkeypatch.setenv("ADMIN_PASSWORD", "short123")
    from app.config import get_settings

    get_settings.cache_clear()
    with pytest.raises(ValueError, match="ADMIN_PASSWORD must be at least 12"):
        get_settings()
    get_settings.cache_clear()


def test_admin_password_long_enough_passes(monkeypatch: pytest.MonkeyPatch) -> None:
    """ADMIN_PASSWORD with 12+ characters is accepted."""
    monkeypatch.setenv("ADMIN_USERNAME", "myadmin")
    monkeypatch.setenv("ADMIN_PASSWORD", "LongEnough123!")
    from app.config import get_settings

    get_settings.cache_clear()
    s = get_settings()
    assert s.admin_password == "LongEnough123!"
    get_settings.cache_clear()

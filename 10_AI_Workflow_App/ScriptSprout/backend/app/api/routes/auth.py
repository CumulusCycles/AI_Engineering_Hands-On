from __future__ import annotations

import hashlib
import hmac
import secrets
from datetime import UTC, datetime, timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.auth.password import hash_password, verify_password
from app.config import get_settings
from app.db.deps import get_db
from app.db.models import AuthSession, User
from app.rate_limit import check_rate_limit
from app.schemas.auth import (
    ChangeEmailRequest,
    ChangeEmailResponse,
    ChangePasswordRequest,
    ChangePasswordResponse,
    EmailVerificationConfirmRequest,
    EmailVerificationConfirmResponse,
    EmailVerificationRequest,
    EmailVerificationRequestResponse,
    LoginRequest,
    RegisterRequest,
    RegisterResponse,
    UserResponse,
)

router = APIRouter(prefix="/api/auth", tags=["auth"])


def _auth_rate_limit() -> str:
    """Return the configured auth rate limit string for slowapi."""
    return get_settings().auth_rate_limit


def _session_ttl_seconds(settings) -> int:
    """Convert session_ttl_days to seconds for cookie max_age."""

    return max(1, int(settings.session_ttl_days * 24 * 3600))


def _set_session_cookie(response: Response, request: Request, session_id: str) -> None:
    """Write the session cookie onto the outgoing response."""

    settings = request.app.state.settings
    response.set_cookie(
        key=settings.session_cookie_name,
        value=session_id,
        httponly=True,
        max_age=_session_ttl_seconds(settings),
        samesite=settings.session_cookie_samesite,
        secure=settings.session_cookie_secure,
        path="/",
    )


def _clear_session_cookie(response: Response, request: Request) -> None:
    """Delete the session cookie from the outgoing response."""

    settings = request.app.state.settings
    response.delete_cookie(
        key=settings.session_cookie_name,
        path="/",
        samesite=settings.session_cookie_samesite,
        secure=settings.session_cookie_secure,
    )


def _verification_token_hash(token: str) -> str:
    """Build a SHA-256 digest for one-time verification token comparison."""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def _is_expired(expires_at: datetime) -> bool:
    """Return True when verification expiration is in the past."""
    if expires_at.tzinfo is None:
        return expires_at < datetime.now(UTC).replace(tzinfo=None)
    return expires_at < datetime.now(UTC)


@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
def register(
    request: Request, body: RegisterRequest, db: Session = Depends(get_db)
) -> RegisterResponse:
    """Create a new author account or return 409 if the username is taken."""

    check_rate_limit(request, _auth_rate_limit())
    username = body.username
    existing = db.scalar(select(User).where(User.username == username))
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already registered",
        )
    user = User(
        username=username,
        password_hash=hash_password(body.password),
        role="author",
        is_active=True,
        email_verified=False,
    )
    db.add(user)
    db.commit()
    return RegisterResponse(username=user.username, role=user.role, verification_required=True)


@router.post(
    "/email-verification/request",
    response_model=EmailVerificationRequestResponse,
)
def request_email_verification(
    request: Request,
    body: EmailVerificationRequest,
    db: Session = Depends(get_db),
) -> EmailVerificationRequestResponse:
    """Create and store a verification token, then return delivery metadata."""
    check_rate_limit(request, _auth_rate_limit())
    user = db.scalar(select(User).where(User.username == body.username))
    if user is None or user.role != "author":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Author account not found",
        )
    if user.email_verified:
        return EmailVerificationRequestResponse(
            message="Email already verified.",
            delivery_channel="none",
        )
    collision = db.scalar(select(User).where(User.email == body.email).where(User.id != user.id))
    if collision is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already in use")

    token = secrets.token_urlsafe(24)
    now = datetime.now(UTC)
    user.email = body.email
    user.email_verification_token_hash = _verification_token_hash(token)
    user.email_verification_sent_at = now
    user.email_verification_expires_at = now + timedelta(minutes=30)
    user.email_verified = False
    db.commit()

    return EmailVerificationRequestResponse(
        message="Verification token generated.",
        delivery_channel="email",
        preview_token=token,
    )


@router.post(
    "/email-verification/confirm",
    response_model=EmailVerificationConfirmResponse,
)
def confirm_email_verification(
    request: Request,
    body: EmailVerificationConfirmRequest,
    db: Session = Depends(get_db),
) -> EmailVerificationConfirmResponse:
    """Confirm author email ownership using one-time token."""
    check_rate_limit(request, _auth_rate_limit())
    user = db.scalar(select(User).where(User.username == body.username))
    if user is None or user.role != "author":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Author account not found",
        )
    if user.email_verified:
        return EmailVerificationConfirmResponse(message="Email is already verified.")
    if (
        user.email_verification_token_hash is None
        or user.email_verification_expires_at is None
        or _is_expired(user.email_verification_expires_at)
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Verification token expired",
        )
    if not hmac.compare_digest(
        user.email_verification_token_hash,
        _verification_token_hash(body.token),
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification token",
        )

    user.email_verified = True
    user.email_verification_token_hash = None
    user.email_verification_sent_at = None
    user.email_verification_expires_at = None
    db.commit()
    return EmailVerificationConfirmResponse(message="Email verified successfully.")


@router.post("/login", response_model=UserResponse)
def login(
    body: LoginRequest,
    response: Response,
    request: Request,
    db: Session = Depends(get_db),
) -> User:
    """Authenticate credentials, create a session, and set the session cookie."""

    check_rate_limit(request, _auth_rate_limit())
    username = body.username.strip()
    user = db.scalar(select(User).where(User.username == username))

    # --- account lockout check ---
    if user is not None and user.locked_until is not None:
        if not _is_expired(user.locked_until):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account temporarily locked due to too many failed login attempts.",
            )
        # lock expired — reset
        user.failed_login_count = 0
        user.locked_until = None

    if user is None or not verify_password(body.password, user.password_hash):
        # increment failure counter if user exists
        if user is not None:
            user.failed_login_count = (user.failed_login_count or 0) + 1
            settings = request.app.state.settings
            if user.failed_login_count >= settings.max_failed_logins:
                user.locked_until = datetime.now(UTC) + timedelta(
                    minutes=settings.account_lockout_minutes,
                )
            db.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )
    settings = request.app.state.settings
    if (
        settings.author_email_verification_required
        and user.role == "author"
        and not user.email_verified
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email verification is required before login.",
        )
    now = datetime.now(UTC)
    # Reset lockout counter on successful login
    if user.failed_login_count:
        user.failed_login_count = 0
        user.locked_until = None
    db.execute(
        update(AuthSession)
        .where(AuthSession.user_id == user.id)
        .where(AuthSession.revoked_at.is_(None))
        .values(revoked_at=now)
    )
    session_id = secrets.token_urlsafe(32)
    expires_at = datetime.now(UTC) + timedelta(days=settings.session_ttl_days)
    db.add(
        AuthSession(
            id=session_id,
            user_id=user.id,
            expires_at=expires_at,
        )
    )
    db.commit()
    _set_session_cookie(response, request, session_id)
    return user


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(response: Response, request: Request, db: Session = Depends(get_db)) -> None:
    """Revoke the current session and clear the session cookie."""

    settings = request.app.state.settings
    raw = request.cookies.get(settings.session_cookie_name)
    if raw:
        row = db.scalar(select(AuthSession).where(AuthSession.id == raw))
        if row is not None and row.revoked_at is None:
            row.revoked_at = datetime.now(UTC)
            db.commit()
    _clear_session_cookie(response, request)


@router.get("/me", response_model=UserResponse)
def me(user: Annotated[User, Depends(get_current_user)]) -> User:
    """Return the currently authenticated user's profile."""

    return user


@router.put("/password", response_model=ChangePasswordResponse)
def change_password(
    body: ChangePasswordRequest,
    response: Response,
    request: Request,
    user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
) -> ChangePasswordResponse:
    """Change the authenticated user's password and revoke all sessions."""
    if not verify_password(body.current_password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Current password is incorrect",
        )
    user.password_hash = hash_password(body.new_password)
    # Revoke all sessions so the user must re-login
    db.execute(
        update(AuthSession)
        .where(AuthSession.user_id == user.id)
        .where(AuthSession.revoked_at.is_(None))
        .values(revoked_at=datetime.now(UTC))
    )
    db.commit()
    _clear_session_cookie(response, request)
    return ChangePasswordResponse(message="Password changed. Please log in again.")


@router.put("/email", response_model=ChangeEmailResponse)
def change_email(
    body: ChangeEmailRequest,
    request: Request,
    user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
) -> ChangeEmailResponse:
    """Change the authenticated user's email and require re-verification."""
    collision = db.scalar(
        select(User).where(User.email == body.new_email).where(User.id != user.id)
    )
    if collision is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already in use",
        )
    token = secrets.token_urlsafe(24)
    now = datetime.now(UTC)
    user.email = body.new_email
    user.email_verified = False
    user.email_verification_token_hash = _verification_token_hash(token)
    user.email_verification_sent_at = now
    user.email_verification_expires_at = now + timedelta(minutes=30)
    db.commit()
    return ChangeEmailResponse(
        message="Email updated. Verification token generated.",
        delivery_channel="email",
        preview_token=token,
    )

from __future__ import annotations

import re

from pydantic import BaseModel, ConfigDict, Field, field_validator

# Shared regex: local@domain.tld — intentionally permissive but catches obvious junk.
_EMAIL_RE = re.compile(r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$")


def _validate_username(v: str) -> str:
    """Strip whitespace and enforce >= 3 char length."""
    s = v.strip()
    if len(s) < 3:
        raise ValueError("at least 3 characters after trimming whitespace")
    return s


def _validate_password_complexity(v: str) -> str:
    """Enforce minimum complexity: at least one uppercase, one lowercase, one digit."""
    if not any(c.isupper() for c in v):
        raise ValueError("must contain at least one uppercase letter")
    if not any(c.islower() for c in v):
        raise ValueError("must contain at least one lowercase letter")
    if not any(c.isdigit() for c in v):
        raise ValueError("must contain at least one digit")
    return v


def _validate_email(v: str) -> str:
    """Normalise and validate email format."""
    s = v.strip().lower()
    if not _EMAIL_RE.match(s):
        raise ValueError("valid email is required")
    return s


class RegisterRequest(BaseModel):
    username: str = Field(min_length=1, max_length=255)
    password: str = Field(min_length=8, max_length=256)

    @field_validator("username")
    @classmethod
    def username_trimmed_length(cls, v: str) -> str:
        return _validate_username(v)

    @field_validator("password")
    @classmethod
    def password_complexity(cls, v: str) -> str:
        return _validate_password_complexity(v)


class LoginRequest(BaseModel):
    username: str = Field(min_length=1, max_length=255)
    password: str = Field(min_length=1, max_length=256)


class EmailVerificationRequest(BaseModel):
    username: str = Field(min_length=1, max_length=255)
    email: str = Field(min_length=3, max_length=320)

    @field_validator("username")
    @classmethod
    def username_trimmed_length_for_verification(cls, v: str) -> str:
        return _validate_username(v)

    @field_validator("email")
    @classmethod
    def email_trimmed_for_verification(cls, v: str) -> str:
        return _validate_email(v)


class EmailVerificationConfirmRequest(BaseModel):
    username: str = Field(min_length=1, max_length=255)
    token: str = Field(min_length=8, max_length=256)

    @field_validator("username")
    @classmethod
    def username_trimmed_length_for_confirm(cls, v: str) -> str:
        return _validate_username(v)


class RegisterResponse(BaseModel):
    username: str
    role: str
    verification_required: bool = True


class EmailVerificationRequestResponse(BaseModel):
    message: str
    delivery_channel: str
    preview_token: str | None = None


class EmailVerificationConfirmResponse(BaseModel):
    message: str


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: str | None = None
    email_verified: bool
    role: str
    is_active: bool


class ChangePasswordRequest(BaseModel):
    current_password: str = Field(min_length=1, max_length=256)
    new_password: str = Field(min_length=8, max_length=256)

    @field_validator("new_password")
    @classmethod
    def new_password_complexity(cls, v: str) -> str:
        return _validate_password_complexity(v)


class ChangePasswordResponse(BaseModel):
    message: str


class ChangeEmailRequest(BaseModel):
    new_email: str = Field(min_length=3, max_length=320)

    @field_validator("new_email")
    @classmethod
    def email_format(cls, v: str) -> str:
        return _validate_email(v)


class ChangeEmailResponse(BaseModel):
    message: str
    delivery_channel: str
    preview_token: str | None = None

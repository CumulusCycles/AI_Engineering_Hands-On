import os
from functools import lru_cache
from pathlib import Path
from typing import Annotated, Literal, Self

from pydantic import AliasChoices, BeforeValidator, Field, model_validator
from pydantic_settings import BaseSettings, PydanticBaseSettingsSource, SettingsConfigDict

# backend/app/config.py -> repo root is parents[2]
_REPO_ROOT = Path(__file__).resolve().parents[2]


def _default_sqlite_path() -> Path:
    """Return the default SQLite database path under the repo data directory."""

    return _REPO_ROOT / "data" / "app.db"


def _default_chroma_path() -> Path:
    """Return the default Chroma persistence path under the repo data directory."""

    return _REPO_ROOT / "data" / "chroma"


def _resolve_repo_path(v: Path | str | None) -> Path | None:
    """Resolve a relative path against the repo root, or return an absolute path as-is."""

    if v is None:
        return None
    p = Path(v)
    if not p.is_absolute():
        return _REPO_ROOT / p
    return p


RepoPath = Annotated[Path, BeforeValidator(_resolve_repo_path)]


def _is_blank(v: str | None) -> bool:
    """Return True if the value is None or a whitespace-only string."""

    return v is None or (isinstance(v, str) and len(v.strip()) == 0)


class Settings(BaseSettings):
    """Load from environment and optional `.env` at the ScriptSprout project root.

    The project root is the directory that contains `backend/`.
    """

    model_config = SettingsConfigDict(
        env_file=_REPO_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        """Exclude the repo .env file during pytest so tests rely only on os.environ."""

        # Under pytest, skip the repo `.env` so tests only see `os.environ` (e.g. monkeypatched
        # SQLITE_PATH) and are not affected by a developer's local `.env` admin credentials.
        if os.environ.get("PYTEST_CURRENT_TEST") is not None:
            return init_settings, env_settings, file_secret_settings
        return init_settings, env_settings, dotenv_settings, file_secret_settings

    # OpenAI (key optional until you call model routes)
    openai_api_key: str | None = None
    # Model strategy (mirrors chapter 9 AI Workflows CLI — `9_AI_Workflows/`):
    # - Base tasks default to BASE_MODEL
    # - Story generation uses OPENAI_STORY_MODEL (default: gpt-4o-mini)
    # - Guardrails parse defaults back to BASE_MODEL unless overridden
    base_model: str = "gpt-5-nano"

    openai_smoke_model: str | None = None
    openai_synopsis_model: str | None = None
    openai_title_model: str | None = None
    openai_description_model: str | None = None
    openai_nlp_model: str | None = None
    openai_admin_nlp_model: str | None = Field(
        default=None,
        validation_alias=AliasChoices("OPENAI_ADMIN_NLP_MODEL"),
        description=(
            "Model for POST /api/admin/nlp-query; defaults to OPENAI_NLP_MODEL / BASE_MODEL."
        ),
    )

    openai_story_model: str | None = "gpt-4o-mini"
    openai_guardrails_model: str | None = None
    openai_image_model: str = Field(
        default="dall-e-3",
        validation_alias=AliasChoices("OPENAI_IMAGE_MODEL", "MODEL_THUMBNAIL_IMAGE"),
    )
    thumbnail_size: str = Field(
        default="1280x720",
        validation_alias="THUMBNAIL_SIZE",
        description=(
            "Target WxH for the stored thumbnail PNG. DALL-E 3 only accepts 1024x1024, "
            "1024x1792, and 1792x1024; if this value is not one of those, the service "
            "requests a supported size and resizes to this target (see thumbnail_generation)."
        ),
    )
    thumbnail_quality: Literal["standard", "hd"] = Field(
        default="standard",
        validation_alias="THUMBNAIL_QUALITY",
    )
    thumbnail_style: Literal["vivid", "natural"] = Field(
        default="vivid",
        validation_alias="THUMBNAIL_STYLE",
    )
    openai_embedding_model: str = Field(
        default="text-embedding-3-small",
        validation_alias=AliasChoices("OPENAI_EMBEDDING_MODEL"),
    )
    openai_tts_model: str = Field(
        default="gpt-4o-mini-tts",
        validation_alias=AliasChoices("OPENAI_TTS_MODEL", "MODEL_TTS"),
    )
    tts_voice_female_us: str = "nova"
    tts_voice_female_uk: str = "fable"
    tts_voice_male_us: str = "echo"
    tts_voice_male_uk: str = "onyx"
    tts_voice_default: str = "nova"
    transient_retry_max_attempts: int = Field(default=2, ge=1, le=10)

    # Persistence (relative paths resolve from repo root)
    sqlite_path: RepoPath = Field(default_factory=_default_sqlite_path)
    chroma_path: RepoPath = Field(default_factory=_default_chroma_path)

    # Admin bootstrap
    admin_username: str | None = None
    admin_password: str | None = None

    # Session cookies
    session_cookie_name: str = "scriptsprout_session"
    session_ttl_days: int = 7
    session_cookie_secure: bool = True
    session_cookie_samesite: Literal["lax", "strict", "none"] = "lax"
    author_email_verification_required: bool = True

    # Security gates (safe defaults for anything beyond localhost).
    expose_meta_without_auth: bool = Field(
        default=False,
        description=(
            "When True, GET /api/meta/db-status and /chroma-status work without a session. "
            "Enable for local demos; leave False when the API is network-exposed."
        ),
    )
    allow_admin_cleanse: bool = Field(
        default=False,
        description=(
            "When True, POST /api/admin/cleanse may wipe SQLite and Chroma. "
            "Keep False unless operators explicitly need destructive reset."
        ),
    )
    auth_rate_limit: str = Field(
        default="5/minute",
        description=(
            "Rate limit applied to authentication endpoints (register, login, "
            "email-verification). Uses slowapi/limits notation, e.g. '5/minute'."
        ),
    )
    max_failed_logins: int = Field(
        default=5,
        ge=1,
        description=(
            "Lock the account after this many consecutive failed login attempts."
        ),
    )
    account_lockout_minutes: int = Field(
        default=15,
        ge=1,
        description="Minutes an account stays locked after exceeding MAX_FAILED_LOGINS.",
    )
    app_environment: Literal["development", "production"] = Field(
        default="development",
        validation_alias=AliasChoices("APP_ENV", "ENVIRONMENT"),
        description='Set to "production" behind HTTPS; enforces Secure session cookies.',
    )

    @model_validator(mode="after")
    def admin_credentials_are_paired(self) -> Self:
        """Require both ADMIN_USERNAME and ADMIN_PASSWORD or neither."""

        if _is_blank(self.admin_username) != _is_blank(self.admin_password):
            msg = "Set both ADMIN_USERNAME and ADMIN_PASSWORD, or leave both unset."
            raise ValueError(msg)
        return self

    @model_validator(mode="after")
    def admin_password_strength(self) -> Self:
        """Enforce minimum strength for the bootstrap admin password."""
        pw = self.admin_password
        if pw and len(pw.strip()) < 12:
            raise ValueError(
                "ADMIN_PASSWORD must be at least 12 characters for security."
            )
        return self

    @model_validator(mode="after")
    def production_requires_secure_session_cookie(self) -> Self:
        """Reject production configuration when SESSION_COOKIE_SECURE is disabled."""

        if self.app_environment == "production" and not self.session_cookie_secure:
            msg = "APP_ENV=production requires SESSION_COOKIE_SECURE=true"
            raise ValueError(msg)
        return self

    @model_validator(mode="after")
    def openai_model_defaults_are_filled(self) -> Self:
        """Fall back unset per-task OpenAI model fields to base_model."""

        base = self.base_model

        if self.openai_smoke_model is None:
            self.openai_smoke_model = base
        if self.openai_synopsis_model is None:
            self.openai_synopsis_model = base
        if self.openai_title_model is None:
            self.openai_title_model = base
        if self.openai_description_model is None:
            self.openai_description_model = base
        if self.openai_nlp_model is None:
            self.openai_nlp_model = base
        if self.openai_admin_nlp_model is None:
            self.openai_admin_nlp_model = self.openai_nlp_model

        # If explicitly unset, keep the story default.
        if self.openai_story_model is None:
            self.openai_story_model = "gpt-4o-mini"

        if self.openai_guardrails_model is None:
            self.openai_guardrails_model = base

        return self

    @model_validator(mode="after")
    def disable_email_verification_gate_by_default_in_pytest(self) -> Self:
        """Keep legacy test expectations unless a test opts into the auth gate."""
        if (
            os.environ.get("PYTEST_CURRENT_TEST") is not None
            and os.environ.get("AUTHOR_EMAIL_VERIFICATION_REQUIRED") is None
        ):
            self.author_email_verification_required = False
        return self

    @model_validator(mode="after")
    def relax_rate_limit_in_pytest(self) -> Self:
        """Use a permissive rate limit during tests unless explicitly overridden."""
        if (
            os.environ.get("PYTEST_CURRENT_TEST") is not None
            and os.environ.get("AUTH_RATE_LIMIT") is None
        ):
            self.auth_rate_limit = "1000/minute"
        return self

    @model_validator(mode="after")
    def relax_cookie_secure_in_pytest(self) -> Self:
        """Disable Secure cookie flag in tests (plain HTTP) unless explicitly set."""
        if (
            os.environ.get("PYTEST_CURRENT_TEST") is not None
            and os.environ.get("SESSION_COOKIE_SECURE") is None
        ):
            self.session_cookie_secure = False
        return self


@lru_cache
def get_settings() -> Settings:
    """Return the cached application Settings singleton."""

    return Settings()

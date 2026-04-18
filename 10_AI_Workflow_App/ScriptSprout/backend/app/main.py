from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from app.api.routes.admin import router as admin_router
from app.api.routes.admin_nlp import router as admin_nlp_router
from app.api.routes.auth import router as auth_router
from app.api.routes.content import router as content_router
from app.api.routes.health import router as health_router
from app.api.routes.meta import router as meta_router
from app.api.routes.model_calls_admin import router as model_calls_admin_router
from app.api.routes.nlp import router as nlp_router
from app.api.routes.openai_admin import router as openai_admin_router
from app.api.routes.search import router as search_router
from app.config import get_settings
from app.db.bootstrap import configure_database
from app.handlers import register_exception_handlers
from app.schemas.errors import ErrorResponse
from app.services.chroma_store import create_persistent_chroma


def create_app() -> FastAPI:
    """Build and return the configured FastAPI application."""

    cfg = get_settings()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        """Set up DB, Chroma, and data dirs on startup; tear down on shutdown."""

        data_dir = cfg.sqlite_path.parent
        data_dir.mkdir(parents=True, exist_ok=True)
        cfg.chroma_path.mkdir(parents=True, exist_ok=True)
        configure_database(app, cfg)
        chroma_client, chroma_collection = create_persistent_chroma(
            cfg.chroma_path,
            embedding_model=cfg.openai_embedding_model,
        )
        app.state.chroma_client = chroma_client
        app.state.chroma_collection = chroma_collection
        yield
        app.state.engine.dispose()

    application = FastAPI(
        title="ScriptSprout API",
        description=(
            "From Prompt to YouTube-Ready Story Content. REST API for authors and admins. "
            "Admin routes are mostly inspection and analytics; exceptions include gated "
            "**`POST /api/admin/cleanse`**, live **`POST /api/admin/openai/smoke`**, and "
            "**`POST /api/admin/nlp-query`** (structured parse then server-side metrics/search)."
        ),
        version="0.1.0",
        lifespan=lifespan,
        openapi_tags=[
            {
                "name": "health",
                "description": "Liveness and bootstrap checks (no auth required).",
            },
            {
                "name": "meta",
                "description": (
                    "Bootstrap introspection. Unauthenticated **only** when "
                    "**`EXPOSE_META_WITHOUT_AUTH=true`**; otherwise **GET** meta routes return "
                    "**404**. For production, keep the flag **false** or remove meta entirely."
                ),
            },
            {
                "name": "auth",
                "description": (
                    "Author registration, login, logout, and session-backed `me`. "
                    "Rate-limited to **`AUTH_RATE_LIMIT`** (default 5 req/min per IP). "
                    "Passwords require ≥8 chars with uppercase, lowercase, and digit. "
                    "Accounts lock after **`MAX_FAILED_LOGINS`** (default 5) consecutive "
                    "failures for **`ACCOUNT_LOCKOUT_MINUTES`** (default 15)."
                ),
            },
            {
                "name": "admin",
                "description": (
                    "Admin-only surface (role **admin**): **`GET /api/admin/ping`**; "
                    "**`GET /api/admin/metrics`** (time-window KPIs from ORM tables); "
                    "**`POST /api/admin/nlp-query`** (OpenAI metrics and/or semantic search); "
                    "read-only **`GET /api/admin/content/`** and **`GET /api/admin/content/{id}`** "
                    "across authors; destructive **`POST /api/admin/cleanse`** when "
                    "**`ALLOW_ADMIN_CLEANSE=true`**; **`GET /api/admin/generation-runs/{run_id}`** "
                    "(run + guardrails events); **`/api/admin/openai/`** smoke; "
                    "**`/api/admin/model-calls/`** call history."
                ),
            },
            {
                "name": "content",
                "description": (
                    "Author-owned content: shell create (`prompt`), paginated list summaries, "
                    "detail by id. Paths under **`/api/content/{content_id}/…`** load the row "
                    "through a shared ownership check (**404** if missing or not yours); media, "
                    "generation, approve/regenerate, and semantic-index routes share that rule."
                ),
            },
            {
                "name": "nlp",
                "description": (
                    "Author-only NLP helpers: extract story parameters + "
                    "missing-field **follow_up** payload."
                ),
            },
            {
                "name": "search",
                "description": (
                    "Author and admin **semantic search** over Chroma ``content_semantic_index`` "
                    "(requires prior indexing via **POST /api/content/{id}/semantic-index**)."
                ),
            },
        ],
        responses={
            401: {
                "description": "Authentication required or session invalid",
                "model": ErrorResponse,
            },
            403: {
                "description": "Authenticated but not allowed for this resource (e.g. wrong role)",
                "model": ErrorResponse,
            },
            404: {
                "description": "Resource not found",
                "model": ErrorResponse,
            },
            409: {
                "description": "Conflict (e.g. duplicate username on register)",
                "model": ErrorResponse,
            },
            502: {
                "description": "Upstream / OpenAI error or bad gateway",
                "model": ErrorResponse,
            },
            503: {
                "description": "Service unavailable (e.g. OpenAI API key not configured)",
                "model": ErrorResponse,
            },
            422: {
                "description": "Validation error",
                "model": ErrorResponse,
            },
            429: {
                "description": (
                    "Rate limit exceeded — retry after the period "
                    "indicated in Retry-After header"
                ),
            },
            500: {
                "description": "Unexpected server error",
                "model": ErrorResponse,
            },
        },
    )

    class _SecurityHeadersMiddleware(BaseHTTPMiddleware):
        async def dispatch(self, request: Request, call_next) -> Response:
            response = await call_next(request)
            response.headers.setdefault("X-Content-Type-Options", "nosniff")
            response.headers.setdefault("X-Frame-Options", "DENY")
            response.headers.setdefault(
                "Referrer-Policy", "strict-origin-when-cross-origin"
            )
            return response

    application.add_middleware(_SecurityHeadersMiddleware)

    application.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://127.0.0.1:5173",
            "http://localhost:5173",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    register_exception_handlers(application)
    application.include_router(health_router)
    application.include_router(meta_router)
    application.include_router(auth_router)
    application.include_router(admin_router)
    application.include_router(admin_nlp_router)
    application.include_router(openai_admin_router)
    application.include_router(model_calls_admin_router)
    application.include_router(content_router)
    application.include_router(nlp_router)
    application.include_router(search_router)

    return application


# ASGI entry: ``uv run uvicorn app.main:create_app --factory`` (see root README).

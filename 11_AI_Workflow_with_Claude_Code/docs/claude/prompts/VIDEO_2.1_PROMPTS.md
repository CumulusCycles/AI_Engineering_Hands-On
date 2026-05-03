1.
```
**Role:** You are a senior backend engineer starting the MVP backend build
phase for ScriptSprout. You follow the layered architecture and rules already
established in `.claude/rules/backend-fastapi.md` and
`.claude/rules/database-and-migrations.md`. You treat `CLAUDE.md` as a living
artifact and update it at the start of every phase before writing code.

**Input:** Update the existing `CLAUDE.md` so it reflects the current phase
(Phase 2.1 — backend build) and the concrete scope we are about to implement.

**Context:**
- `CLAUDE.md` already exists from Phase 1 with project overview, tech stack,
  and hard rules — keep those intact. We are only updating phase-related sections.
- No backend code exists yet; we are about to create it.
- The MVP scope is a filtered subset of the full product — regeneration,
  admin, embeddings, Chroma, thumbnails, and audio are explicitly deferred
  to later phases.

**Execution:**
1. Update the **Current phase** section of `CLAUDE.md` to read:
   `"Phase 2.1: Backend Build — building the complete FastAPI backend for the MVP"`
2. Replace the **Current build scope** section with:
   - Backend project initialized with uv
   - Pydantic Settings for all environment variables
   - SQLAlchemy models: User, Session, ContentItem, ModelCallLog
   - SQLite database with automatic schema bootstrap on startup
   - FastAPI layered architecture: routes → services → repositories
   - Pydantic schemas for all request/response contracts
   - Shared dependencies: auth session guard, ownership guard
   - Routes: health, auth (register/login/logout/me), content (create/generate/list/get)
   - OpenAI single-pass generation: title + description + story in one call
   - Every OpenAI call logged to the `model_call_log` table
   - Unit tests: happy path, 401 without session, ownership denial
   - Postman collection for all MVP routes
3. Leave **Out of scope** unchanged (regeneration, admin, embeddings, Chroma,
   thumbnails, audio).
4. Stage and commit with message:
   `docs: update CLAUDE.md for Phase 2.1 backend build`
```

2.
```
**Input:** Read the MVP milestone docs so you know exactly which slice of the
full product we're building in this phase, then summarize your understanding.

**Context:**
- The full product context (master requirements) is already encoded in
  `CLAUDE.md` and the rules files.
- The MVP docs are the scoping filter — they tell you what to build AND what
  to defer. Anything outside the MVP scope must NOT appear in this build.

**Execution:**
1. Read in this order:
   - `docs/reqs/mvp/MVP_BUSINESS_REQS.md`
   - `docs/reqs/mvp/MVP_FUNCTIONAL_REQS.md`
   - `docs/reqs/mvp/MVP_TECH_REQS.md`
2. Summarize:
   - The data entities we need for the MVP
   - The API routes we need to expose
   - What is explicitly deferred and must not appear in this build
3. Do not create any files yet.
```

3.
```
Please check git status, then create and checkout a new feature branch called
feat/backend-mvp. Confirm we are on the new branch.
```

4.
```
**Input:** Create the `.claude/commands/` directory and add three backend
workflow command files that will be used throughout this phase and beyond.

**Context:**
- Commands make recurring operations invocable by name (e.g. `/test-backend`).
- The `validate-and-fix` skill defined in Phase 1 calls the `test-backend`
  command — so this must exist before we run the validation loop.
- `.claude/` is a living artifact; commands are added in the phase that needs
  them, not preemptively.

**Execution:**
1. Create `.claude/commands/test-backend.md` — runs the backend test suite:
   - Navigate to `backend/`
   - Run: `uv run pytest tests/ -v`
   - Report results
2. Create `.claude/commands/lint-backend.md` — runs the backend linter:
   - Navigate to `backend/`
   - Run: `uv run ruff check app/`
   - Report any issues found
3. Create `.claude/commands/run-backend.md` — starts the backend dev server:
   - Navigate to `backend/`
   - Run: `uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`
   - Confirm startup output is clean
4. Update `.claude/README.md` to note that backend commands have been added
   in Phase 2.1.
5. Stage all files and commit with a Conventional Commit message.
```

5.
```
**Input:** Initialize the backend Python project using `uv` and install all
MVP dependencies. Do not create any application files yet — we are only
setting up the package manager and dependencies.

**Context:**
- `uv` is our Python package manager (per `CLAUDE.md` stack decisions).
- `slowapi` is required for rate limiting on auth endpoints per the technical
  requirements.
- We need both runtime dependencies (FastAPI stack + OpenAI) and dev
  dependencies (pytest, ruff).

**Execution:**
1. Create the `backend/` directory.
2. From inside `backend/`, initialize a uv project: `uv init`
3. Delete the auto-generated entry-point stub `uv init` creates at the backend
   root (typically `main.py`, sometimes `hello.py` on older uv versions). Leave
   `pyproject.toml`, `.python-version`, and `README.md` in place. The real
   FastAPI app entry point is created at `backend/app/main.py` in a later
   prompt — leaving the stub would cause confusion with that file.
4. Add core dependencies:
   ```
   uv add fastapi uvicorn[standard] sqlalchemy pydantic-settings \
     python-multipart itsdangerous passlib[bcrypt] openai slowapi
   ```
5. Add dev dependencies:
   ```
   uv add --dev pytest pytest-asyncio httpx ruff
   ```
6. Show me `pyproject.toml` so I can confirm the dependency list is correct.
```

6.
```
**Input:** Create the complete backend folder structure with empty files and
`__init__.py` stubs. Do not fill in any files yet — we are establishing the
layered architecture first so subsequent prompts can drop code into the right
places.

**Context:**
- Follow the layering from `.claude/rules/backend-fastapi.md`: routes →
  services → repositories, plus supporting folders.
- `tests/` sits at the `backend/` level, not inside `app/` — conventional
  Python project layout.
- `postman/` is created now but stays empty until the end of this phase.

**Execution:**
Create this exact tree, with an `__init__.py` in every Python package directory.
All `.py` files except `__init__.py` are **empty stubs** for now. `postman/` is an
empty directory (no placeholder file). **`pyproject.toml`** already exists from the
previous prompt — do not remove or replace it.

```
backend/
├── pyproject.toml             # already exists — leave as-is
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── database.py
│   ├── limiter.py
│   ├── main.py
│   ├── dependencies/
│   │   ├── __init__.py
│   │   └── auth.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── session.py
│   │   ├── content_item.py
│   │   └── model_call_log.py
│   ├── repositories/
│   │   ├── __init__.py
│   │   ├── user_repo.py
│   │   ├── session_repo.py
│   │   ├── content_repo.py
│   │   └── model_call_log_repo.py
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── health.py
│   │   ├── auth.py
│   │   └── content.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── common.py
│   │   └── content.py
│   └── services/
│       ├── __init__.py
│       ├── auth_service.py
│       └── content_service.py
├── postman/
└── tests/
    ├── conftest.py
    ├── test_auth.py
    ├── test_content.py
    └── test_health.py
```

7.
```
**Input:** Create the backend config module (`backend/app/config.py`) using
Pydantic Settings, and update the project-root `.env.example` with all Phase 2.1
environment variables.

**Context:**
- All environment variables flow through Pydantic Settings — no scattered
  `os.getenv()` calls anywhere in the codebase.
- `SESSION_SECRET_KEY` and `OPENAI_API_KEY` MUST have no defaults — the app
  must fail loudly on startup if they are missing.
- `.env.example` is populated incrementally. Phase 1 added only GH credentials.
  This phase adds the backend variables below that section.

**Execution:**
1. Create `backend/app/config.py` with a Pydantic Settings class covering:

   Database:
   - `DATABASE_URL: str` — default `"sqlite:///./scriptsprout.db"`

   Sessions:
   - `SESSION_COOKIE_NAME: str` — default `"scriptsprout_session"`
   - `SESSION_TTL_SECONDS: int` — default `86400` (24 hours)
   - `SESSION_SECRET_KEY: str` — no default, must be set

   Auth hardening:
   - `AUTH_RATE_LIMIT: str` — default `"10/minute"`
   - `AUTH_MAX_FAILED_ATTEMPTS: int` — default `5`
   - `AUTH_LOCKOUT_SECONDS: int` — default `900` (15 minutes)

   AI:
   - `OPENAI_API_KEY: str` — no default, must be set
   - `OPENAI_CHAT_MODEL: str` — default `"gpt-4o-mini"`

   App:
   - `APP_ENV: str` — default `"development"`
   - `CORS_ORIGINS: list[str]` — default `["http://localhost:5173"]`

   Export a single instance: `settings = Settings()`.

2. Update `.env.example` at the project root. Below the existing GH section,
   add the new variables grouped with comments:
   ```
   # --- Phase 2.1: Backend ---

   # Database
   # Sessions
   # Auth
   # AI (OpenAI)
   # App / CORS
   ```
   Use safe placeholder values throughout.

3. Stage and commit both files with a Conventional Commit message.
```

8.
```
**Input:** Create the four SQLAlchemy 2.x declarative models for the MVP —
`User`, `Session`, `ContentItem`, `ModelCallLog`.

**Context:**
- Follow `.claude/rules/database-and-migrations.md`: one model per file,
  explicit relationships with `relationship()` and foreign keys, no raw SQL.
- `Session.id` must be an opaque random string token — not an auto-increment
  integer. (Session IDs leak information when sequential.)
- All models live under `backend/app/models/`.

**Execution:**
1. Create `backend/app/models/user.py` — `User`:
   - `id`: Integer primary key
   - `username`: String, unique, not null, indexed
   - `email`: String, unique, nullable
   - `password_hash`: String, not null
   - `role`: String, not null, default `"author"` (values: `"author"`, `"admin"`)
   - `is_active`: Boolean, default True
   - `failed_login_attempts`: Integer, default 0
   - `locked_until`: DateTime, nullable
   - `created_at`: DateTime, default `utcnow`
   - Relationships: `sessions` (one-to-many), `content_items` (one-to-many)

2. Create `backend/app/models/session.py` — `Session`:
   - `id`: String primary key (opaque random token — not an integer)
   - `user_id`: Integer FK → `users.id`, not null
   - `expires_at`: DateTime, not null
   - `revoked_at`: DateTime, nullable
   - `created_at`: DateTime, default `utcnow`
   - Relationship: `user` (many-to-one)

3. Create `backend/app/models/content_item.py` — `ContentItem`:
   - `id`: Integer primary key
   - `author_id`: Integer FK → `users.id`, not null
   - `subject`: String, not null
   - `genre`: String, not null
   - `audience`: String, not null
   - `runtime`: String, not null
   - `title`: String, nullable (generated)
   - `synopsis`: Text, nullable (generated — short summary, between
     description and story in length; required by `history-detail.html`
     and `detail-regenerate.html` mockups)
   - `description`: Text, nullable (generated)
   - `story`: Text, nullable (generated)
   - `status`: String, not null, default `"draft"`
   - `created_at`: DateTime, default `utcnow`
   - `updated_at`: DateTime, default `utcnow`, onupdate `utcnow`
   - Relationships: `author` (many-to-one), `model_call_logs` (one-to-many)

4. Create `backend/app/models/model_call_log.py` — `ModelCallLog`:
   - `id`: Integer primary key
   - `user_id`: Integer FK → `users.id`, not null
   - `content_item_id`: Integer FK → `content_items.id`, nullable
   - `operation`: String, not null (e.g. `"generate_content"`)
   - `model_name`: String, not null
   - `success`: Boolean, not null
   - `latency_ms`: Integer, nullable
   - `prompt_tokens`: Integer, nullable
   - `completion_tokens`: Integer, nullable
   - `error_class`: String, nullable
   - `created_at`: DateTime, default `utcnow`

5. Update `backend/app/models/__init__.py` to import all four models.

6. Stage and commit with a Conventional Commit message.
```

9.
```
**Input:** Create the database module, the rate limiter, and the FastAPI
application entry point. After this prompt the app must be runnable for the
first time, with automatic schema bootstrap on startup.

**Context:**
- Use the modern `@asynccontextmanager` lifespan pattern — NOT the deprecated
  `@app.on_event` decorators.
- Import all models before calling `Base.metadata.create_all(engine)` so they
  are registered with metadata before the tables are created.
- The rate limiter lives in its own module (`app/limiter.py`) to avoid a
  circular import between `main.py` (registers the middleware) and
  `routes/auth.py` (uses the decorator). Both import the same `limiter`
  instance from `app.limiter`.
- No routers are registered yet — schemas, repositories, and route files come
  in later prompts. After this prompt the app starts cleanly with an empty
  API surface (just `/` → `/docs` redirect and Swagger). Routers are wired
  in once the route files exist.

**Execution:**
1. Create `backend/app/database.py`:
   - SQLAlchemy engine created from `settings.DATABASE_URL`
   - `SessionLocal` factory
   - `Base = declarative_base()`
   - `get_db()` dependency: yields a session, closes after request
   - `bootstrap_database()` function: imports all models, then calls
     `Base.metadata.create_all(engine)`

2. Create `backend/app/limiter.py`:
   - Imports: `from slowapi import Limiter`, `from slowapi.util import get_remote_address`
   - Export a single instance: `limiter = Limiter(key_func=get_remote_address)`
   - That is the entire file. Keeping it tiny lets both `main.py` and route
     files import the same instance without circular imports.

3. Create `backend/app/main.py`:
   - FastAPI app with `title="ScriptSprout API"`, `version="0.1.0"`
   - CORS middleware using `settings.CORS_ORIGINS` (allow credentials, all
     methods, all headers)
   - Lifespan context manager (using `@asynccontextmanager`) that calls
     `bootstrap_database()` on startup
   - Rate limiter wiring: import `limiter` from `app.limiter`, then
     `app.state.limiter = limiter`; register a `RateLimitExceeded` exception
     handler using `slowapi._rate_limit_exceeded_handler`; add
     `SlowAPIMiddleware`
   - `GET /` redirects to `/docs`
   - Do NOT register any routers yet — they are wired in later (prompt 14)
     after the route files exist.

4. Stage and commit with a Conventional Commit message.
```

10.
```
**Input:** Create Pydantic v2 schemas for all MVP request and response shapes.

**Context:**
- Every request/response shape uses a schema — no raw dicts across API
  boundaries (per `.claude/rules/backend-fastapi.md`).
- Field names and types must match the models defined in the previous prompt.
- `ErrorResponse` must match the consistent error shape our backend rules
  require: `{"code": "...", "message": "..."}`.
- Response schemas that wrap SQLAlchemy ORM rows (`AuthResponse`,
  `ContentResponse`, `ContentListResponse`) MUST set
  `model_config = ConfigDict(from_attributes=True)` so FastAPI can serialize
  ORM instances directly via `response_model=...`. Pure request schemas
  (`RegisterRequest`, `LoginRequest`, `ContentCreateRequest`) and non-ORM
  responses (`MessageResponse`, `ErrorResponse`, `HealthResponse`) do NOT
  need it.

**Execution:**
1. Create `backend/app/schemas/auth.py`:
   - `RegisterRequest`: `username`, `password`, `email` (optional)
   - `LoginRequest`: `username`, `password`
   - `AuthResponse`: `id`, `username`, `role`, `created_at` —
     `model_config = ConfigDict(from_attributes=True)`
   - `MessageResponse`: `message` (generic success message)

2. Create `backend/app/schemas/content.py`:
   - `ContentCreateRequest`: `subject`, `genre`, `audience`, `runtime`
   - `ContentResponse`: `id`, `author_id`, `subject`, `genre`, `audience`,
     `runtime`, `title`, `synopsis`, `description`, `story`, `status`,
     `created_at`, `updated_at` — `model_config = ConfigDict(from_attributes=True)`
   - `ContentListResponse`: `items` (list of `ContentResponse`), `total` —
     `model_config = ConfigDict(from_attributes=True)`

3. Create `backend/app/schemas/common.py`:
   - `ErrorResponse`: `code`, `message`
   - `HealthResponse`: `status`, `version`

4. Stage and commit with a Conventional Commit message.
```

11.
```
**Input:** Create the four repository modules that form the entire data
access layer for the MVP.

**Context:**
- All database access goes through repositories — no queries in routes or
  services (per `.claude/rules/backend-fastapi.md`).
- Each function accepts a `db` session as the first argument.
- Use SQLAlchemy query API only — no raw SQL.
- `session_repo.create` must generate the opaque random session ID inside
  the repo function itself (not at the call site).

**Execution:**
1. Create `backend/app/repositories/user_repo.py`:
   - `get_by_id(db, user_id) → User | None`
   - `get_by_username(db, username) → User | None`
   - `create(db, username, password_hash, email=None) → User`
   - `increment_failed_attempts(db, user_id) → User`
   - `lock_account(db, user_id, until: datetime) → User`
   - `reset_failed_attempts(db, user_id) → User`

2. Create `backend/app/repositories/session_repo.py`:
   - `create(db, user_id, expires_at) → Session` (generate opaque random id here)
   - `get_valid_session(db, session_id) → Session | None` (returns `None` if
     expired or revoked)
   - `revoke(db, session_id) → None`

3. Create `backend/app/repositories/content_repo.py`:
   - `create(db, author_id, subject, genre, audience, runtime) → ContentItem`
   - `get_by_id(db, content_id) → ContentItem | None`
   - `get_by_id_and_author(db, content_id, author_id) → ContentItem | None`
   - `list_by_author(db, author_id) → list[ContentItem]`
   - `update_generated_fields(db, content_id, title, synopsis, description, story, status) → ContentItem`

4. Create `backend/app/repositories/model_call_log_repo.py`:
   - `create(db, user_id, operation, model_name, success, content_item_id=None,
     latency_ms=None, prompt_tokens=None, completion_tokens=None,
     error_class=None) → ModelCallLog`

5. Stage and commit with a Conventional Commit message.
```

12.
```
**Input:** Create the shared FastAPI dependency functions in
`backend/app/dependencies/auth.py` — one for auth session checking, one for
author-role enforcement, one for content ownership enforcement.

**Context:**
- Defined once, reused everywhere — never copy-pasted per route.
- **Ownership denial returns 404, NOT 403.** Returning 403 would reveal that
  the content item exists and belongs to someone else. 404 treats the item as
  if it doesn't exist for this user. This is required by our backend rules.
- The session cookie is HTTP-only (set by the login route).

**Execution:**
Create `backend/app/dependencies/auth.py` with four dependency functions.
Per the Session-alias rule in `.claude/rules/backend-fastapi.md`: alias
OUR auth `Session` model as `AuthSession`
(`from app.models.session import Session as AuthSession`); leave
SQLAlchemy's `Session` un-aliased. Apply this in every backend file that
references both.

1. `get_current_session(request, db) → Session` (the auth Session model)
   - Read session ID from the HTTP-only session cookie
   - Call `session_repo.get_valid_session()` to validate
   - If no session or invalid: raise `HTTPException 401`
   - Return the auth `Session` model
   - Use this when the route needs the session ID itself (e.g., logout)

2. `get_current_user(session = Depends(get_current_session)) → User`
   - Return `session.user` (via the SQLAlchemy relationship)
   - Most protected routes use this; it transitively gates auth via
     `get_current_session`

3. `require_author(current_user: User = Depends(get_current_user)) → User`
   - If user role is not `"author"` or `"admin"`: raise `HTTPException 403`
   - Return the user

4. `get_owned_content(content_id: int, current_user: User = Depends(get_current_user), db = Depends(get_db)) → ContentItem`
   - Call `content_repo.get_by_id_and_author(db, content_id, current_user.id)`
   - If not found: raise `HTTPException 404` (never 403 — do not reveal existence)
   - Return the `ContentItem`

Stage and commit with a Conventional Commit message.
```

13.
```
**Input:** Create the two service modules that hold all MVP business logic —
`auth_service.py` and `content_service.py`.

**Context:**
- Services orchestrate repositories and AI calls. All OpenAI calls live here.
- **Every OpenAI call MUST be logged to `model_call_log` before returning —
  on both success and failure paths** (per `CLAUDE.md` hard rules).
- No raw exception details leak to the client — re-raise as clean
  `HTTPException` with a generic message.
- Password hashing uses `passlib[bcrypt]`.

**Execution:**
1. Create `backend/app/services/auth_service.py`:
   - `register_user(db, username, password, email=None) → User`
     - Check username not already taken (raise `409` if taken)
     - Hash password with passlib bcrypt
     - Call `user_repo.create()`
   - `login_user(db, username, password) → tuple[User, Session]`
     - Get user by username (raise `401` if not found)
     - Check account not locked (raise `423` with retry-after if locked)
     - Verify password hash (raise `401` if wrong)
       - On wrong password: `increment_failed_attempts`, lock if threshold reached
     - `reset_failed_attempts` on success
     - Create session via `session_repo.create()` with TTL from settings
     - Return `(user, session)` — the route needs both: `user` to build the
       `AuthResponse`, `session.id` to set the cookie
   - `logout_user(db, session_id) → None`
     - Call `session_repo.revoke()`

2. Create `backend/app/services/content_service.py`:
   - `create_content_item(db, author_id, subject, genre, audience, runtime) → ContentItem`
     - Call `content_repo.create()`
   - `generate_content(db, content_item_id, author_id) → ContentItem`
     - Fetch content item (verify ownership)
     - Record start time before the OpenAI call
     - Call OpenAI chat completions to generate title + synopsis +
       description + story in one call
     - On success:
       - Calculate `latency_ms`
       - Log to `model_call_log` via `model_call_log_repo.create()` with token counts
       - Update content item with generated fields and status `"generated"`
     - On failure:
       - Log the failed call (`success=False`, `error_class=type(e).__name__`)
       - Re-raise a clean `HTTPException` — no raw exception details to the client
     - Return updated `ContentItem`

3. Stage and commit with a Conventional Commit message.
```

14.
```
**Input:** Create all three MVP route files — `health.py`, `auth.py`,
`content.py` — and register their routers in `main.py`.

**Context:**
- Route handlers are thin: parse input, call service, return response.
  No business logic in routes (per `.claude/rules/backend-fastapi.md`).
- All protected routes use the dependency functions from the previous prompt —
  no inline auth checks.
- All routers mount under the `/api` prefix.

**Execution:**
1. Create `backend/app/routes/health.py`:
   - `GET /health` → `HealthResponse`: `{"status": "ok", "version": "0.1.0"}`
   - No auth required

2. Create `backend/app/routes/auth.py`:
   - Imports include `limiter` from `app.limiter` and `settings` from
     `app.config`
   - `POST /auth/register` → `AuthResponse` (201)
     - Decorate with `@limiter.limit(settings.AUTH_RATE_LIMIT)` (rate limited
       per remote IP). The handler MUST take `request: Request` as a parameter
       — slowapi reads it to extract the remote address.
     - Call `auth_service.register_user()`, return user data
   - `POST /auth/login` → `AuthResponse` (200)
     - Decorate with `@limiter.limit(settings.AUTH_RATE_LIMIT)` (same pattern;
       `request: Request` parameter required)
     - Call `auth_service.login_user()` → unpack `(user, session)`
     - Set HTTP-only session cookie from `session.id` using `settings` values
       (cookie name, TTL)
     - Return `AuthResponse` built from `user`
   - `POST /auth/logout` → `MessageResponse` (200)
     - Use `get_current_session` dependency (this also gates auth — 401 if no
       valid session)
     - Call `auth_service.logout_user(db, session.id)`, clear the session cookie
   - `GET /auth/me` → `AuthResponse` (200)
     - Require valid session, return current user data

3. Create `backend/app/routes/content.py`:
   - `POST /content/` → `ContentResponse` (201)
     - Require author (use `require_author` dependency)
     - Call `content_service.create_content_item()`
   - `POST /content/{content_id}/generate` → `ContentResponse` (200)
     - Require owned content (use `get_owned_content` dependency)
     - Call `content_service.generate_content()`
   - `GET /content/` → `ContentListResponse` (200)
     - Require author, return list of author's own content items only
   - `GET /content/{content_id}` → `ContentResponse` (200)
     - Require owned content, return item

4. Update `backend/app/main.py` to register all three routers:
   - health router: `prefix="/api"`, `tag="health"`
   - auth router: `prefix="/api"`, `tag="auth"`
   - content router: `prefix="/api"`, `tag="content"`

5. Stage and commit with a Conventional Commit message.
```

15.
```
**Input:** Write the full unit test suite for the MVP backend covering health,
auth, and content routes. Run the suite and confirm all tests pass before
committing.

**Context:**
- Tests must cover happy path, 401 without session, and ownership denial per
  `docs/reqs/mvp/MVP_TECH_REQS.md`.
- Use an in-memory SQLite database for tests — do NOT share the real DB file.
- Do NOT test `generate_content` — that requires a live OpenAI call. That
  route is exercised via Postman for now; we'll add mocks in a later phase.
- If any test fails, follow the `validate-and-fix` skill: analyze, fix root
  cause, re-run, repeat. Do not commit until the suite is clean.

**Execution:**
1. Create `backend/tests/conftest.py`:
   - `TestClient` fixture using httpx + the FastAPI app
   - In-memory SQLite database for tests
   - Bootstrap test DB schema before tests
   - Disable rate limiting for tests: import the `limiter` from `app.limiter`
     and set `limiter.enabled = False` once at module/fixture setup. Tests
     all share `127.0.0.1` and would otherwise trip `AUTH_RATE_LIMIT`.
   - Helper to create a test user and return auth cookie
   - Helper to create a second test user (for ownership tests)
   - Tear down after each test

2. Create `backend/tests/test_health.py`:
   - `test_health_returns_200`
   - `test_health_response_shape`: `status="ok"`, version present

3. Create `backend/tests/test_auth.py`:
   - `test_register_success`: `POST /api/auth/register` → 201, returns user data
   - `test_register_duplicate_username`: second register with same username → 409
   - `test_login_success`: login with valid credentials → 200, cookie set
   - `test_login_wrong_password`: → 401
   - `test_login_unknown_user`: → 401
   - `test_me_authenticated`: `GET /api/auth/me` with valid session → 200
   - `test_me_unauthenticated`: `GET /api/auth/me` without session → 401
   - `test_logout_clears_session`: logout then `/me` → 401

4. Create `backend/tests/test_content.py`:
   - `test_create_content_unauthenticated`: `POST /api/content/` without session → 401
   - `test_create_content_authenticated`: → 201, returns content item
   - `test_list_content_empty`: `GET /api/content/` with no items → 200, empty list
   - `test_list_content_returns_own_only`: two authors, each sees only their own items
   - `test_get_content_ownership_denial`: author A cannot `GET` author B's content → 404
   - `test_get_content_not_found`: `GET /api/content/999` → 404

5. Run `uv run pytest tests/ -v` from inside `backend/` and show me the
   full output. Do not commit until all tests pass.
```

16.
```
**Input:** Run the `validate-and-fix` skill on the backend to confirm everything
is clean before we push.

**Context:**
- Use the `/test-backend` command for the test suite and the `/lint-backend`
  command for lint checks.
- Follow the `validate-and-fix` skill exactly: fix root causes, not symptoms;
  never modify a test to make it pass; loop until clean.

**Execution:**
1. Run `/test-backend` — full pytest run.
2. Run `/lint-backend` — ruff check.
3. If anything fails, follow the `validate-and-fix` skill and loop.
4. When done, confirm:
   - Total tests: `X passed, 0 failed`
   - Ruff lint: 0 issues
   - All changes committed
```

17.
```
Please start the backend dev server from inside the backend/ directory:

uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

Show me the startup output. I want to confirm:
- No errors on startup
- DB bootstrap runs (tables created)
- Server running on port 8000

I will manually verify Swagger at http://localhost:8000/docs in the browser.
After I confirm, I will stop the server with Ctrl+C.
```

18.
```
**Input:** Create a Postman Collection v2.1 JSON file covering all MVP routes,
in logical workflow order.

**Context:**
- File path: `backend/postman/ScriptSprout_MVP.postman_collection.json`.
- The collection is used for manual testing now and will be driven by Newman
  for automated API testing in a later phase — so request bodies and descriptions
  need to be real, not placeholders.
- Postman Collection Schema: v2.1.

**Execution:**
Create the collection with these route groups in this order:

1. **Health**
   - `GET /api/health`

2. **Auth**
   - `POST /api/auth/register`
   - `POST /api/auth/login`
   - `GET /api/auth/me`
   - `POST /api/auth/logout`

3. **Content**
   - `POST /api/content/` (create item)
   - `POST /api/content/:id/generate`
   - `GET /api/content/` (list mine)
   - `GET /api/content/:id` (get one)

For each request:
- Set `Content-Type: application/json` where applicable
- Add example request bodies for POST routes
- Add a brief description explaining what the request does

Stage and commit with a Conventional Commit message.
```

19.
```
**Input:** Run the **`log-claude-build`** procedure in **`.claude/skills/log-claude-build.md`** for **`VIDEO_2.1`**.

**Context:**
- The skill was installed in **VIDEO_1**. Execute it yourself now—do not ask the learner to trigger the skill manually.
- Stay on **`feat/backend-mvp`**. Ground summaries in **`git log` / `git diff`** for harness paths only (`CLAUDE.md`, `.claude/`, and harness-related root **`.env.example`** if it changed this phase).

**Execution:**
1. Follow the skill end-to-end with **`VIDEO_ID=VIDEO_2.1`**.
2. Stage and commit with: `docs: VIDEO_2.1 harness build notes`
```

20.
```
**Input:** Summarize the commits on this branch, push it to origin, and open
a PR against `main` using the `gh` CLI.

**Context:**
- Remote is `origin`, base is `main`.
- Use `gh` CLI for push and PR creation (GitHub MCP arrives in Phase 3).
- The `validate-and-fix` loop already confirmed tests and lint are clean —
  this is the final step.

**Execution:**
1. Show me a summary of all commits on `feat/backend-mvp` so I can review what
   we've built.
2. Push the `feat/backend-mvp` branch to `origin`.
3. Open a pull request using `gh pr create` with:
   - Base branch: `main`
   - Title: `feat: MVP backend — auth, content generation, tests, Postman`
   - Body (verbatim):

## What this PR contains

Complete FastAPI backend for the ScriptSprout MVP — layered architecture,
SQLAlchemy models, auth with session management, single-pass content generation
with OpenAI, unit tests, and Postman collection.

### Architecture
- `backend/app/config.py` — Pydantic Settings for all env vars
- `backend/app/database.py` — SQLAlchemy engine, session factory, auto-bootstrap
- `backend/app/main.py` — FastAPI app, CORS, lifespan, slowapi wiring, Swagger at /docs
- `backend/app/limiter.py` — slowapi `Limiter` instance shared by main.py and auth routes (separate module to avoid circular imports)
- `backend/app/models/` — User, Session, ContentItem, ModelCallLog
- `backend/app/schemas/` — request/response contracts (no raw dicts)
- `backend/app/repositories/` — all DB access in one place
- `backend/app/services/` — business logic, OpenAI calls, model call logging
- `backend/app/routes/` — thin handlers: health, auth (rate-limited register/login), content
- `backend/app/dependencies/` — shared session/auth guards, ownership guard (404 pattern)

### API surface
- GET /api/health
- POST /api/auth/register, /login, /logout — GET /api/auth/me
- POST /api/content/, /api/content/{id}/generate
- GET /api/content/, /api/content/{id}

### Quality
- All unit tests passing (happy path, 401, ownership denial)
- Ruff lint clean
- App starts cleanly, Swagger loads at /docs
- DB bootstraps automatically on startup
- Rate limiting (`AUTH_RATE_LIMIT`) enforced on `POST /auth/register` and `POST /auth/login` via slowapi; disabled in tests

### Config additions
- CLAUDE.md updated for Phase 2.1
- .claude/commands/ — test-backend, lint-backend, run-backend
- .env.example — Phase 2.1 variables added (database, sessions, auth, AI)

### Note on generate_content tests
OpenAI generation tests are not included — live API calls are not tested in unit tests.
Postman collection covers the generate endpoint for manual/integration testing.
```


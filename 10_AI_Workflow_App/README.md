# ScriptSprout

> **Course module 10 — AI Workflow App.** This README, [`ARCHITECTURE.md`](ARCHITECTURE.md), [`TESTING.md`](TESTING.md), and [`architecture.html`](architecture.html) live in **10_AI_Workflow_App/**. Executable project files (backend, frontend, [`ScriptSprout/test-scripts/`](ScriptSprout/test-scripts/), `.env`, `data/`) are in **[`ScriptSprout/`](ScriptSprout/)**. Run `./startup.sh`, `./test-scripts/test.sh`, and `cd backend` / `cd frontend` from **`ScriptSprout/`** unless a path is written as absolute.

<img src="ScriptSprout/img/script-sprout.png" alt="ScriptSprout" width="50%" />

**From Prompt to YouTube-Ready Story Content**  
*Plant a prompt. Grow a channel-ready story.*

ScriptSprout is a standalone web application for content creators who want to generate narrated YouTube video content with AI. Authors can start from a single natural-language prompt, review and approve drafts (synopsis, title, description), generate a full story with automatic guardrails checking, and produce both a thumbnail image and optional narration audio file. Admins have **HTTP APIs that are mostly inspection and analytics**: content browse, model-call history, generation-run inspection, **semantic search across all authors**, **`GET /api/admin/metrics`**, and **`POST /api/admin/nlp-query`** (structured parse of the question, then server-side metrics and/or semantic search — not OpenAI tool calling). **Exceptions:** **`POST /api/admin/cleanse`** is a **gated destructive** reset (SQLite + Chroma); **`POST /api/admin/openai/smoke`** performs a live OpenAI call and records **`model_calls`**. The React app includes auth shell routes (`/`, `/login`, `/register`, `/verify-email`), author **`/profile`**, a unified author studio (`/studio`), admin dashboard (`/admin-dashboard`), and admin NLP query (`/admin-nlp`).

## Audience

- **Authors:** Generate and manage story content end-to-end in the UI.
- **Admins:** Inspect cross-author content and usage, run semantic search, view aggregated metrics, and submit natural-language admin queries in both API and UI flows (plus gated operational routes such as **cleanse** and **OpenAI smoke** — see API tables).

## Core Capabilities

- **NLP-first input** — structured parameter extraction with follow-up prompts when fields are missing
- **Step approval flow (HITL)** — synopsis, title, and description each require author approval before proceeding
- **Story generation with guardrails** — automatic guardrails loop with per-content row limits
- **Thumbnail and narration audio** — generated and stored as SQLite BLOBs with dedicated `GET` media routes
- **Semantic indexing** — title/description/story text embedded into ChromaDB for vector search (audio/thumbnails are not embedded)
- **Semantic search** — author-scoped or admin-scoped search across indexed content
- **Admin APIs (mostly read / analytics)** — content browse, model-call history, generation-run inspection, aggregated metrics, natural-language admin queries; **cleanse** and **smoke** are exceptions (see `/api/admin` routes)
- **Author profile management** — change password (revokes all sessions) and change email (requires re-verification)
- **Email verification** — configurable author email verification before login is allowed

## Frontend Routes

| Route | Component | Access |
|---|---|---|
| `/` | HomePage | Public |
| `/login` | LoginPage | Redirects to `/` if logged in |
| `/register` | RegisterPage | Redirects to `/` if logged in |
| `/verify-email` | EmailVerificationPage | Public (no session gate; not redirected when logged in) |
| `/studio` | AuthorStudioPage | Author only |
| `/profile` | ProfilePage | Author only |
| `/admin-dashboard` | AdminDashboardPage | Admin only |
| `/admin-nlp` | AdminNlpQueryPage | Admin only |

Legacy routes `/workspace`, `/draft-review`, and `/story-media` redirect to `/studio`.

## API Endpoints

### Auth (`/api/auth`)

| Method | Path | Description |
|---|---|---|
| POST | `/register` | Register a new author account |
| POST | `/login` | Log in (sets session cookie) |
| POST | `/logout` | Log out (clears session cookie) |
| GET | `/me` | Get current authenticated user |
| PUT | `/password` | Change password (revokes all sessions) |
| PUT | `/email` | Change email (requires re-verification) |
| POST | `/email-verification/request` | Request email verification token |
| POST | `/email-verification/confirm` | Confirm email with token |

### Content (`/api/content`)

| Method | Path | Description |
|---|---|---|
| POST | `/` | Create a new content row |
| GET | `/` | List author's content |
| GET | `/{id}` | Get content detail |
| GET | `/{id}/thumbnail` | Get thumbnail image |
| GET | `/{id}/audio` | Get narration audio |
| POST | `/{id}/generate-synopsis` | Generate synopsis |
| POST | `/{id}/generate-title` | Generate title |
| POST | `/{id}/generate-description` | Generate description |
| POST | `/{id}/generate-story` | Generate story with guardrails |
| POST | `/{id}/generate-thumbnail` | Generate thumbnail image |
| POST | `/{id}/generate-audio` | Generate narration audio |
| POST | `/{id}/approve-step` | Approve a workflow step |
| POST | `/{id}/regenerate-step` | Regenerate a workflow step |
| POST | `/{id}/semantic-index` | Index content into ChromaDB |

### NLP (`/api/nlp`)

| Method | Path | Description |
|---|---|---|
| POST | `/extract-story-parameters` | Extract structured parameters from a prompt |

### Search (`/api/search`)

| Method | Path | Description |
|---|---|---|
| POST | `/semantic` | Semantic search (author- or admin-scoped) |

### Admin (`/api/admin`)

| Method | Path | Description |
|---|---|---|
| GET | `/ping` | Admin auth check |
| GET | `/metrics` | Aggregated metrics (optional `start`/`end` query params) |
| GET | `/content/` | Browse all authors' content |
| GET | `/content/{id}` | Get any content detail |
| POST | `/cleanse` | Wipe SQLite + Chroma (requires `ALLOW_ADMIN_CLEANSE=true`) |
| GET | `/generation-runs/{run_id}` | Inspect a generation run |
| POST | `/openai/smoke` | OpenAI connectivity smoke test |
| GET | `/model-calls/` | List model call history |
| POST | `/nlp-query` | Natural-language admin query |

### Meta (`/api/meta`)

| Method | Path | Description |
|---|---|---|
| GET | `/db-status` | SQLite status (requires `EXPOSE_META_WITHOUT_AUTH=true`) |
| GET | `/chroma-status` | ChromaDB status (requires `EXPOSE_META_WITHOUT_AUTH=true`) |

### Health

| Method | Path | Description |
|---|---|---|
| GET | `/health` | Application health check |

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 19, TypeScript, Vite 8 |
| Backend | FastAPI, Python 3.11+ (managed by [uv](https://docs.astral.sh/uv/)) |
| Database | SQLite (via SQLAlchemy) |
| Vector store | ChromaDB |
| AI | OpenAI Responses API, Images API, Audio API (TTS), Embeddings API |
| Frontend testing | Vitest (unit), Playwright (E2E) |
| Backend testing | pytest with `TestClient` |
| API testing | Postman collection + Newman CLI |
| Linting | Ruff (backend), ESLint (frontend) |

## Architecture

**Repository layout**, **request flow** (FastAPI routes, `app/services`, `app/db/repos`, SQLite, Chroma, OpenAI), **admin cleanse** (SQLite + Chroma wipe), and **dev server** commands are documented in **[`ARCHITECTURE.md`](ARCHITECTURE.md)**. For a visual overview, open **[`architecture.html`](architecture.html)** in a browser.

By default, SQLite lives at **`ScriptSprout/data/app.db`** and Chroma at **`ScriptSprout/data/chroma`** unless you override **`SQLITE_PATH`** and **`CHROMA_PATH`** (see [Environment variables](#environment-variables)). Keep **`ScriptSprout/data/`** if you want data to survive restarts.

## Quick Start (Local Dev)

**Requirements:** [uv](https://docs.astral.sh/uv/) (manages Python 3.11+ and the backend venv), Node 20+ (or current LTS), `npm`.

### 1. Environment

Copy **`ScriptSprout/.env.example`** to **`ScriptSprout/.env`** (not required for `/health` alone):

```bash
cd ScriptSprout
cp .env.example .env
```

For local development, keep `EXPOSE_META_WITHOUT_AUTH=true` so `GET /api/meta/*` works. Keep `SESSION_COOKIE_SECURE=false` (or unset) while using `http://` on localhost. When deploying behind HTTPS, set `APP_ENV=production` and `SESSION_COOKIE_SECURE=true` (enforced at startup).

### 2. Backend (FastAPI)

```bash
cd ScriptSprout/backend
uv sync --group dev
uv run uvicorn app.main:create_app --factory --reload --host 127.0.0.1 --port 8000
```

- Health: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)
- Swagger UI: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- ReDoc: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

**Cookie auth in Swagger UI:** call `POST /api/auth/login` first (Try it out); the session cookie persists across requests on the same host.

### 3. Frontend (Vite + React)

In a second terminal:

```bash
cd ScriptSprout/frontend
npm install
npm run dev
```

Open [http://127.0.0.1:5173/](http://127.0.0.1:5173/). The dev server proxies **`GET /health`** and **`/api/*`** to the API (see `ScriptSprout/frontend/vite.config.ts`).

### Convenience Scripts

From **`ScriptSprout/`**:

```bash
./startup.sh                  # Start backend, wait for /health, then start frontend
./shutdown.sh                 # Stop frontend (:5173) and backend (:8000) dev servers
./reset-db-and-chroma.sh --yes   # Wipe SQLite + Chroma (see [Reset Dev Database](#reset-dev-database))
```

## Testing

**Setup, script reference, and copy-paste commands:** **[`TESTING.md`](TESTING.md)**.

All automation shells use `set -euo pipefail` and exit on first failure.

**Cross-stack test/verify automation** lives under **[`ScriptSprout/test-scripts/`](ScriptSprout/test-scripts/)** (see [`ScriptSprout/test-scripts/README.md`](ScriptSprout/test-scripts/README.md)). **`./startup.sh`**, **`./shutdown.sh`**, and **`./reset-db-and-chroma.sh`** stay at **`ScriptSprout/`** root (dev servers and local DB wipe).

### Test Scripts

| Script | What it runs | Run from |
|---|---|---|
| `./test-scripts/test.sh` | Backend (Ruff + pytest) then frontend (ESLint + Vitest) | `ScriptSprout/` |
| `./backend/test.sh` | Ruff lint + pytest | `ScriptSprout/backend/` or `ScriptSprout/` |
| `./frontend/test.sh` | ESLint + Vitest | `ScriptSprout/frontend/` or `ScriptSprout/` |
| `./test-scripts/test-e2e.sh` | Playwright E2E tests | `ScriptSprout/` |
| `./test-scripts/test-postman.sh` | Newman API automation (safe mode, OpenAI disabled) | `ScriptSprout/` |
| `./test-scripts/verify.sh` | Unit/lint, E2E, Newman author run, then Newman admin smoke | `ScriptSprout/` |
| `./test-scripts/test-cleanup.sh` | **Manual only:** delete test/build caches (keeps `.venv`, `node_modules`, `frontend/.vite`, `data/`, `.env`) | `ScriptSprout/` |

### Unit and Lint Tests

Run the combined backend + frontend gate:

```bash
cd ScriptSprout
./test-scripts/test.sh
```

Optional args are passed through to backend pytest only (e.g. `./test-scripts/test.sh -v`).

Run backend or frontend independently:

```bash
cd ScriptSprout
./backend/test.sh      # Ruff check + pytest
./frontend/test.sh     # ESLint + Vitest
```

### End-to-End Tests (Playwright)

Requires a one-time browser install:

```bash
cd ScriptSprout/frontend && npx playwright install
```

Run E2E:

```bash
cd ScriptSprout
./test-scripts/test-e2e.sh           # Headless
./test-scripts/test-e2e.sh headed    # Visible browser
```

### API Tests (Postman / Newman)

Spins up an ephemeral backend server, runs the Newman collection, then shuts it down:

```bash
cd ScriptSprout
./test-scripts/test-postman.sh                                        # Safe mode (OpenAI disabled)
POSTMAN_LIVE=1 ./test-scripts/test-postman.sh                         # Live OpenAI calls
POSTMAN_INCLUDE_ADMIN_SMOKE=1 ./test-scripts/test-postman.sh          # Safe mode + admin smoke folders
POSTMAN_LIVE=1 POSTMAN_INCLUDE_ADMIN_SMOKE=1 ./test-scripts/test-postman.sh  # Live + admin smoke
```

The Postman collection is at [`ScriptSprout/backend/postman/ScriptSprout.postman_collection.json`](ScriptSprout/backend/postman/ScriptSprout.postman_collection.json). See [`ScriptSprout/backend/postman/README.md`](ScriptSprout/backend/postman/README.md) for folder details.

### Verify (full local check)

Runs unit/lint, E2E, and both Newman passes (safe + admin smoke) in sequence:

```bash
cd ScriptSprout
./test-scripts/verify.sh
```

### Test artifact cleanup (optional)

Removes linters’/test caches and Playwright output; does **not** remove **`data/`**, **`backend/.venv`**, **`frontend/node_modules`**, or **`frontend/.vite`**. Run manually when you want a cleaner tree — **not** invoked by **`verify.sh`**.

```bash
cd ScriptSprout
./test-scripts/test-cleanup.sh
```

### Reset Dev Database

Wipe SQLite and ChromaDB for a clean start. Restart the API server afterward (startup recreates tables and reseeds admin):

```bash
cd ScriptSprout
./reset-db-and-chroma.sh --yes
```

Also supports `--kill-port` to stop any running server on the API port before wiping.

## Environment Variables

**Canonical list and comments:** `ScriptSprout/.env.example`. Settings load via `ScriptSprout/backend/app/config.py` (`get_settings()`).

### Security and Behavior

| Variable | Default | Description |
|---|---|---|
| `APP_ENV` | `development` | Set to `production` to enforce `SESSION_COOKIE_SECURE=true` |
| `EXPOSE_META_WITHOUT_AUTH` | `false` | Allow unauthenticated `GET /api/meta/*` |
| `ALLOW_ADMIN_CLEANSE` | `false` | Allow `POST /api/admin/cleanse` |
| `AUTHOR_EMAIL_VERIFICATION_REQUIRED` | `true` | Block login until email is verified |
| `AUTH_RATE_LIMIT` | `5/minute` | Rate limit for auth endpoints (per IP) |
| `MAX_FAILED_LOGINS` | `5` | Failed login attempts before account lockout |
| `ACCOUNT_LOCKOUT_MINUTES` | `15` | Duration of account lockout |

### Admin Bootstrap

Set **both** or **neither** (the app will error if only one is set):

| Variable | Description |
|---|---|
| `ADMIN_USERNAME` | Seed admin username |
| `ADMIN_PASSWORD` | Seed admin password (12-character minimum) |

### Session Cookies

| Variable | Default | Description |
|---|---|---|
| `SESSION_COOKIE_NAME` | `scriptsprout_session` | Cookie name |
| `SESSION_TTL_DAYS` | `7` | Session lifetime |
| `SESSION_COOKIE_SECURE` | `true` | Require HTTPS (set `false` for local dev) |
| `SESSION_COOKIE_SAMESITE` | `lax` | SameSite policy |

### Paths

| Variable | Default | Description |
|---|---|---|
| `SQLITE_PATH` | `./data/app.db` | SQLite database file |
| `CHROMA_PATH` | `./data/chroma` | ChromaDB directory |

### OpenAI

| Variable | Default | Description |
|---|---|---|
| `OPENAI_API_KEY` | — | Required for all OpenAI routes |
| `BASE_MODEL` | `gpt-5-nano` | Default model for base tasks |
| `OPENAI_SMOKE_MODEL` | `BASE_MODEL` | Model for smoke test |
| `OPENAI_NLP_MODEL` | `BASE_MODEL` | Model for NLP extraction |
| `OPENAI_ADMIN_NLP_MODEL` | `OPENAI_NLP_MODEL` | Model for admin NLP query |
| `OPENAI_SYNOPSIS_MODEL` | `BASE_MODEL` | Model for synopsis generation |
| `OPENAI_TITLE_MODEL` | `BASE_MODEL` | Model for title generation |
| `OPENAI_DESCRIPTION_MODEL` | `BASE_MODEL` | Model for description generation |
| `OPENAI_STORY_MODEL` | `gpt-4o-mini` | Model for story generation |
| `OPENAI_GUARDRAILS_MODEL` | `BASE_MODEL` | Model for guardrails parsing |
| `OPENAI_EMBEDDING_MODEL` | `text-embedding-3-small` | Model for embeddings |
| `OPENAI_IMAGE_MODEL` | `dall-e-3` | Model for thumbnail (alias: `MODEL_THUMBNAIL_IMAGE`) |
| `OPENAI_TTS_MODEL` | `gpt-4o-mini-tts` | Model for narration (alias: `MODEL_TTS`) |
| `TRANSIENT_RETRY_MAX_ATTEMPTS` | `2` | Max API attempts per call (initial + retries) |

### Thumbnail

| Variable | Default | Description |
|---|---|---|
| `THUMBNAIL_SIZE` | `1280x720` | **Stored** thumbnail dimensions (`WxH`). DALL·E 3 accepts only **`1024x1024`**, **`1024x1792`**, and **`1792x1024`**. If you set another size (default `1280x720`), the API is called with a supported size and the PNG is **resized** to this target (`ScriptSprout/backend/app/services/thumbnail_generation.py`). |
| `THUMBNAIL_QUALITY` | `standard` | Image quality |
| `THUMBNAIL_STYLE` | `vivid` | Image style |

### TTS Voices

| Variable | Default | Description |
|---|---|---|
| `TTS_VOICE_FEMALE_US` | `nova` | Female US voice |
| `TTS_VOICE_FEMALE_UK` | `fable` | Female UK voice |
| `TTS_VOICE_MALE_US` | `echo` | Male US voice |
| `TTS_VOICE_MALE_UK` | `onyx` | Male UK voice |
| `TTS_VOICE_DEFAULT` | `nova` | Default voice |

Guardrail loop count is configured per content row (`guardrails_max_loops` on create), not via environment variable.

## OpenAPI and API Docs

With the backend running:

| URL | Description |
|---|---|
| `/docs` | Swagger UI |
| `/redoc` | ReDoc |
| `/openapi.json` | OpenAPI JSON spec |

## Postman Collection

The collection at [`ScriptSprout/backend/postman/ScriptSprout.postman_collection.json`](ScriptSprout/backend/postman/ScriptSprout.postman_collection.json) contains the following folders:

Auth, Content, NLP extract, Synopsis, Title + Description, Story, Thumbnail, Audio, Media, Semantic index, Semantic search, Admin / RBAC, Admin content, Admin metrics, Admin NLP query, OpenAI smoke + model_calls, Generation runs.

See [`ScriptSprout/backend/postman/README.md`](ScriptSprout/backend/postman/README.md) for details.

## Brand Colors

| Name | Hex |
|---|---|
| Primary Navy | `#2F3E57` |
| Secondary Green | `#4CAF50` |
| Highlight Yellow | `#F4C542` |
| Base White | `#FFFFFF` |

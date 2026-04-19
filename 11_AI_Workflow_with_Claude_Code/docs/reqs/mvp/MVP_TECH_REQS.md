# ScriptSprout — Technical requirements (MVP milestone)

**Document type:** Milestone scope — **not** a second architecture spec  
**Audience:** Engineering during **MVP / Video 12** work

---

## Canonical specifications (read these first)

| Document | Purpose |
|----------|---------|
| [`../TECHNICAL_REQS.md`](../TECHNICAL_REQS.md) | Stack, layering, auth, API principles, data concepts, AI, testing, deployment |
| [`../FUNCTIONAL_REQS.md`](../FUNCTIONAL_REQS.md) | All **observable** behavior the system must meet |
| [`../BUSINESS_REQS.md`](../BUSINESS_REQS.md) | Why the system exists and what “done” means for the business |

**This file does not replace [`../TECHNICAL_REQS.md`](../TECHNICAL_REQS.md).** It scopes **MVP engineering only**: what to build first, which env vars you need at minimum, and what **must not** appear yet.

**MVP functional slice:** [`MVP_FUNCTIONAL_REQS.md`](./MVP_FUNCTIONAL_REQS.md)

---

## MVP — technical slice (must hold)

### Stack (MVP)

Per master **[`../TECHNICAL_REQS.md`](../TECHNICAL_REQS.md) §2** — MVP MUST use:

- **Backend:** Python, **FastAPI**, **SQLAlchemy**, **SQLite**, Pydantic settings  
- **Frontend:** **React**, **TypeScript**, **Vite**  
- **Auth:** **Server-side sessions** + **HTTP-only** session cookie  
- **AI:** OpenAI (or compatible) via official SDK; **single** text generation path acceptable for “title + description + story” in MVP  
- **Layout:** **Milestone / repo convention** (not prescribed in master [`../TECHNICAL_REQS.md`](../TECHNICAL_REQS.md)): monorepo with **`backend/`** and **`frontend/`** as siblings — keep unless the master doc or team explicitly changes it

### Architecture (MVP)

Follow master **[`../TECHNICAL_REQS.md`](../TECHNICAL_REQS.md) §3–5** in full: thin routes, services, repos/schemas, **shared** auth + **ownership** dependencies, AI calls isolated with logging.

### Data (MVP minimum)

Conceptual entities required for MVP (see master **§7** for full intent):

- **User** (author role sufficient for MVP)
- **Session** (opaque id, expiry, revocation)
- **Content item** — brief fields + **title**, **description**, **story** + timestamps + author FK
- **Model call log** — enough metadata per AI request for debugging and later admin metrics

### API shape (MVP)

MVP MUST expose **grouped HTTP resources** under a stable prefix (master **§4**). Capabilities required:

- **Auth:** register, login, logout, **current user**
- **Content:** create item, **run generation** (returns or persists title/description/story), **list mine**, **get one** (ownership enforced)
- **Health:** liveness for local dev / ops

Exact path strings and OpenAPI layout are **implementation choices** as long as **[`../FUNCTIONAL_REQS.md`](../FUNCTIONAL_REQS.md)** behaviors hold.

### AI (MVP)

- **One** primary text model for the bundled generation (configure via environment — e.g. a small general model).
- **No** embeddings pipeline, **no** image/TTS calls in MVP.
- **Every** provider call MUST be logged per master **§8** / **TG-4**.

### Explicitly **out of scope for MVP** (defer)

- Chroma / vector store / embedding index upkeep / **admin** NLP semantic investigation routes  
- Thumbnail and audio generate/serve routes  
- Admin route group, admin bootstrap, cross-author reads  
- Optional features only named in enhancements (see [`../enhancements/ENHANCEMENTS_TECH_REQS.md`](../enhancements/ENHANCEMENTS_TECH_REQS.md))

---

## Environment variables (MVP minimum set)

Load from **`.env`** at project root (never commit secrets). Names are **illustrative** — align with your `.env.example`.

**AI**

- API key for the text provider  
- Default **chat** / story model name(s)

**Database**

- SQLite file path (or URL if you standardize differently)

**Session**

- Cookie name, TTL, `Secure` / `SameSite` flags appropriate to deployment

**Auth hardening (recommended even in MVP)**

- Rate limit string for auth endpoints  
- Lockout thresholds if you implement them (master **§5**)

**Tooling (optional for your workflow)**

- If you use GitHub MCP: token, owner, repo — **only** if that integration is in scope for MVP.

---

## Quality bar (MVP)

Per master **[`../TECHNICAL_REQS.md`](../TECHNICAL_REQS.md) §14** — at minimum:

- Backend: happy path + **401** without session + **ownership** denial  
- Frontend: generation flow **loading / error / success**, history **empty** state  
- Lint clean for changed code

---

## Revision

| Version | Notes |
|---------|--------|
| 1.0 | Baseline MVP technical milestone (`docs/reqs/mvp/`). |

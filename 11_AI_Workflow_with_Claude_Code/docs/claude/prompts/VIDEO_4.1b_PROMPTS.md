1.
```
**Role:** You are a senior backend engineer building the ScriptSprout admin
surface. This phase introduces three first-of-their-kind concepts to the
backend: admin role enforcement, a vector store (Chroma), and cross-author
visibility through admin reads. Your priorities are: strict separation
between author routes and admin routes, never leaking cross-author data
through semantic hits on author paths, and making admin bootstrap fully
idempotent so restarts are safe.

**Input:** Update the project-root `CLAUDE.md` to reflect the Phase 4.1b
scope and the new hard rules that come with admin enforcement — before any
code changes.

**Context:**
- CLAUDE.md last described Phase 4.1a (author-facing enhancements: E1, E3, E4).
- 4.1b adds E2 (admin NLP / Chroma) and E5 (admin dashboard). These are
  admin-only concerns; they do NOT replace the author surface.
- The existing hard-rules section must be preserved — append the new admin
  rules rather than replacing the block.
- Do not touch sections unrelated to Phase 4.1b (rules files, commands,
  validate-and-fix skill, MCP servers, agents).

**Execution:**
1. Edit `CLAUDE.md` with the following changes:

   a. Current phase → change to:
      "Phase 4.1b: Enhancements Backend — admin surface (E2 admin
      NLP/semantic with Chroma, E5 admin dashboard)"

   b. Current build scope → replace with:
      E2 — Admin NLP / semantic investigation:
           Chroma vector store initialized on startup
           Embeddings upserted automatically when content is generated or
           regenerated
           Admin-only route: natural language query → metrics + semantic hits
      E5 — Admin dashboard:
           require_admin dependency fully enforced on all admin routes
           Admin bootstrap from environment on startup (idempotent)
           Routes: metrics, paginated model-call history, read-only content
           inspection

   c. Out of scope → update to:
      Email verification, destructive cleanse, public discovery, billing,
      collaborative editing, rich admin NLP studio beyond shipped surfaces

   d. Append to hard rules:
      - Admin routes MUST use `require_admin` dependency — never author guard
      - Authors MUST never receive cross-author data from any path including
        semantic
      - Chroma vectors MUST be upserted/deleted in sync with `content_item`
        changes
      - Admin NLP queries may return cross-author hits — authors never get them
      - Admin bootstrap MUST be idempotent — safe to run on every restart

2. Stage and commit with:
   `docs: update CLAUDE.md for Phase 4.1b enhancements backend admin surface`
```

2.
```
**Input:** Read the enhancement milestone docs and summarize only E2 and E5
(admin surface) in terms grounded in the existing stack.

**Context:**
- E1, E3, and E4 are already built and merged (4.1a). Do not re-summarize
  them.
- This video is the first time admin role enforcement, Chroma, and
  cross-author reads appear in the project — call out those first-time
  concerns explicitly.
- Do not write any code, create files, or modify config in this prompt.

**Execution:**
1. Read, in order:
   - `docs/reqs/enhancements/ENHANCEMENTS_BUSINESS_REQS.md`
   - `docs/reqs/enhancements/ENHANCEMENTS_FUNCTIONAL_REQS.md`
   - `docs/reqs/enhancements/ENHANCEMENTS_TECH_REQS.md`

2. Summarize in three bullet groups:
   - **E2:** Chroma responsibilities, indexing policy (when upserts fire),
     and the admin NLP query route shape
   - **E5:** `require_admin` enforcement, admin bootstrap idempotency, and
     the four admin routes (metrics, NLP query, model calls, content inspect)
   - **Ownership / admin boundary:** the rules that apply to both (authors
     never see cross-author data; admins see all)

3. Create nothing.
```

3.
```
Using GitHub MCP, please create and checkout a new feature branch called
feat/enhancements-backend-admin from main. Confirm we are on the new branch.
```

4.
```
**Input:** Create a new rules file `.claude/rules/admin-and-search.md` that
governs admin routes and semantic search patterns, and update
`.claude/README.md` to reference it.

**Context:**
- Existing rules files cover backend-fastapi, database-and-migrations,
  frontend-react-vite-typescript, and coding-standards. This is the first
  rules file for admin and semantic concerns — same file shape.
- These rules codify the boundaries introduced by 4.1b; they must be
  inheritable by future phases (the frontend video will read these too when
  wiring admin UI).
- Destructive admin operations (cleanse, wipe) appear in the master spec
  docs but are deliberately NOT implemented. The rules file must say so
  explicitly so a future session doesn't regress and add them.

**Execution:**
1. Create `.claude/rules/admin-and-search.md` with two sections:

   **Admin rules:**
   - ALL admin routes MUST use `require_admin` dependency — never the
     author guard
   - Admin guards must check `role == "admin"` explicitly — not just
     "not author"
   - Cross-author reads on admin routes must be logged at the audit level
   - Admin bootstrap user created from `ADMIN_USERNAME` / `ADMIN_PASSWORD`
     env vars on startup only if no admin user exists — idempotent, safe to
     run on every restart
   - Destructive admin operations (cleanse, wipe) are NOT implemented in
     this build — do not add them even if referenced in master docs

   **Semantic search rules:**
   - Chroma collection initialized on startup alongside SQLite bootstrap
   - Vectors upserted automatically on: content generated, content regenerated
   - Vectors deleted automatically on: content item deleted (if deletion is
     ever added)
   - Author-scoped callers MUST NEVER receive cross-author vector hits —
     enforce in service
   - Admin semantic queries use admin-only routes and may return
     cross-author results
   - Embedding model must be consistent between index time and query time —
     use settings value

2. Update `.claude/README.md` to list the new rules file under the rules
   section alongside the existing files.

3. Stage and commit with:
   `docs: add admin-and-search rules file for Phase 4.1b`
```

5.
```
**Input:** Add the Phase 4.1b environment variables (Chroma, embeddings,
admin bootstrap) to `backend/app/config.py` and to `.env.example`.

**Context:**
- 4.1a added the image + TTS vars; this prompt completes the Phase 4.1 env
  var set.
- `ADMIN_USERNAME` and `ADMIN_PASSWORD` are intentionally optional. Admin
  bootstrap is skipped when either is unset — this keeps local dev frictionless
  and makes the bootstrap idempotent.
- `CHROMA_PATH` is a relative path by default (`./chroma_db`) — that folder
  should be added to `.gitignore` if not already (check and add if missing).
- `.env.example` already has per-phase section headers — follow that
  convention.

**Execution:**
1. Update `backend/app/config.py` to add:
   - `OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-small"`
   - `CHROMA_PATH: str = "./chroma_db"`
   - `ADMIN_USERNAME: str | None = None`
   - `ADMIN_PASSWORD: str | None = None`

2. Append a new section to `.env.example`, directly below the Phase 4.1a
   block:

   ```
   # --- Phase 4.1b: Enhancements Backend (admin surface) ---
   # Embeddings + Chroma
   OPENAI_EMBEDDING_MODEL=text-embedding-3-small
   CHROMA_PATH=./chroma_db

   # Admin bootstrap (optional — skip if not set)
   ADMIN_USERNAME=
   ADMIN_PASSWORD=
   ```

3. If `./chroma_db` is not yet in `.gitignore`, add it now.

4. Stage and commit with:
   `feat: add Phase 4.1b config vars for Chroma, embeddings, admin bootstrap`
```

6.
```
**Input:** Extend `backend/app/database.py` to initialize Chroma on startup
and bootstrap the admin user idempotently.

**Context:**
- `bootstrap_database()` already initializes the SQLite schema on startup.
  Preserve that behavior — only add the Chroma and admin steps.
- Install `chromadb` via `uv add chromadb` before importing it.
- Admin bootstrap MUST be idempotent. Three distinct log outcomes so the
  behavior is observable from the startup logs:
    - "Admin user bootstrapped"
    - "Admin user already exists"
    - "Admin bootstrap skipped (credentials not set)"
- Do NOT wire the embedding index service or admin service yet — those
  come in the next prompts.

**Execution:**
1. Run `uv add chromadb` from `backend/` to add the dependency.

2. Update `backend/app/database.py` to add:
   - `get_chroma_client()` — returns a persistent Chroma client at
     `settings.CHROMA_PATH`
   - `get_or_create_collection()` — returns the `"content_items"` collection,
     creating it if absent

3. Extend `bootstrap_database()` to:
   - Keep the existing SQLite schema bootstrap
   - Initialize the Chroma client and collection; log confirmation
   - If both `settings.ADMIN_USERNAME` and `settings.ADMIN_PASSWORD` are set:
     check if an admin user exists; if not, create one with `role="admin"`
     and a hashed password
   - Log the three outcomes above

4. Stage and commit with:
   `feat: init Chroma and admin bootstrap on startup`
```

7.
```
**Input:** Build the embedding index service and wire its `upsert` into the
content generation and regeneration paths so Chroma stays in sync.

**Context:**
- The embedding index is the *invariant enforcement layer* for the Chroma
  collection. Every time a content item changes, the index must be updated —
  otherwise admin NLP queries will return stale hits.
- The text document is built from `title + description + story`, skipping
  `None` fields. If the combined document is empty (all three fields None),
  skip the upsert rather than embedding an empty string.
- Every embedding API call MUST be logged to `model_call_log` — same
  discipline as every other OpenAI call in the project.
- `content_service.py` is MVP code; `regeneration_service.py` is 4.1a code.
  Both must now invoke the index after successful writes.
- Do NOT add admin-query-side code here — that lands in the next prompt.

**Execution:**
1. Create `backend/app/services/embedding_index.py` with:
   - `upsert_content_item(content_item: ContentItem) -> None`
     * Build the document (skip None fields); if empty, return early
     * Embed via OpenAI using `settings.OPENAI_EMBEDDING_MODEL`
     * Upsert into the `"content_items"` Chroma collection with:
       - `id`: `str(content_item.id)`
       - `embedding`: the vector
       - `metadata`: `{ author_id, status, created_at }`
     * Log the embedding call to `model_call_log`
   - `delete_content_item(content_item_id: int) -> None`
     * Delete the vector from Chroma by id

2. Update `backend/app/services/content_service.py`: after every successful
   generation call, invoke `embedding_index.upsert_content_item(item)`.
   Preserve all existing behavior.

3. Update `backend/app/services/regeneration_service.py`: after every
   successful `regenerate_title`, `regenerate_description`, and
   `regenerate_story`, invoke `embedding_index.upsert_content_item(item)`.

4. Stage and commit with:
   `feat: E2 embedding index service wired into generate and regenerate`
```

8.
```
**Input:** Build the admin service (metrics, NLP query, model-call history,
cross-author content inspection) and its response schemas.

**Context:**
- Admin NLP queries MUST NOT apply an author filter to the Chroma query —
  the admin sees all. Author routes that use the index (none today, but the
  boundary matters) do apply the filter. This is the load-bearing rule from
  the new admin-and-search rules file.
- Hydrate semantic hits from SQLite after the Chroma query. Chroma is
  authoritative for similarity; SQLite is authoritative for field values.
- The admin content inspection path is READ-ONLY. Do not add update or
  delete admin operations here or anywhere else in this phase.
- Follow the existing service/schema convention: async functions, Pydantic
  v2 schemas, `model_config = ConfigDict(from_attributes=True)` where
  returning ORM rows.

**Execution:**
1. Create `backend/app/services/admin_service.py` with:
   - `get_metrics(db) -> dict`
     * total content items, total model calls, success rate, counts by
       operation type — all authors combined
   - `nlp_query(db, query_text: str) -> dict`
     * Embed the query via OpenAI
     * Chroma top-5 — NO author filter
     * Hydrate IDs from SQLite `content_items`
     * Return `{ metrics: get_metrics(), semantic_hits: [ContentResponse...] }`
   - `get_model_calls(db, page: int = 1, page_size: int = 20) -> dict`
     * Paginated `model_call_log` rows across all authors, `created_at desc`
     * Return `{ items, total, page, page_size }`
   - `get_content_item_admin(db, content_id: int) -> ContentItem`
     * Fetch by id with no author filter
     * Raise 404 if not found

2. Create `backend/app/schemas/admin.py` with:
   - `MetricsResponse` — total_items, total_model_calls, success_rate,
     calls_by_operation
   - `NlpQueryRequest` — query_text
   - `NlpQueryResponse` — metrics, semantic_hits
   - `ModelCallResponse` — all fields from `ModelCallLog`
   - `ModelCallListResponse` — items, total, page, page_size
   - `AdminContentResponse` — same shape as `ContentResponse`

3. Stage and commit with:
   `feat: E2/E5 admin service and response schemas`
```

9.
```
**Input:** Activate the `require_admin` dependency, create the admin router
with its four routes, and register the router on the app.

**Context:**
- `require_admin` was stubbed during the MVP so the dependency name existed
  but had no real enforcement. Now it must actually check `role == "admin"`
  and raise `403` otherwise.
- `403` is the correct response for authenticated-but-not-admin (admin
  existence is not a secret). This differs from the 404-on-ownership-denial
  pattern used on author routes (where the existence of another user's
  content IS a secret).
- All four admin routes use `require_admin`. None of them use the author
  guard — mixing guards here is the exact mistake the new rules file is
  meant to prevent.
- Register the router with `prefix="/api"` and `tags=["admin"]` so it
  appears under `/api/admin/*` and groups cleanly in the OpenAPI docs.

**Execution:**
1. Update `backend/app/dependencies/auth.py` to fully implement
   `require_admin`:
   ```
   def require_admin(current_user: User = Depends(get_current_user)) -> User:
       if current_user.role != "admin":
           raise HTTPException(status_code=403, detail="Admin access required")
       return current_user
   ```

2. Create `backend/app/routes/admin.py` with four routes (all using
   `require_admin`):
   - `GET /admin/metrics` → `MetricsResponse`
   - `POST /admin/nlp-query` → `NlpQueryResponse`
   - `GET /admin/model-calls?page=&page_size=` → `ModelCallListResponse`
   - `GET /admin/content/{content_id}` → `AdminContentResponse` (read-only)

3. Register the admin router in `backend/app/main.py` with `prefix="/api"`
   and `tags=["admin"]`.

4. Stage and commit with:
   `feat: activate require_admin and register admin router`
```

10.
```
**Input:** Write unit tests for E2 and E5, add an admin fixture, and run
the full suite.

**Context:**
- The most important guarantee to test is the 403 behavior: every admin
  route, when hit by an authenticated author, returns 403. This is the
  guard the whole phase hinges on.
- Unauthenticated requests on admin routes should return 401 (handled by
  `get_current_user` before `require_admin` runs).
- OpenAI embedding calls must be mocked — never hit the real API from tests.
- The admin user fixture belongs in `backend/tests/conftest.py` so it can
  be reused later (e.g., by the frontend admin tests via the backend
  integration path).

**Execution:**
1. Add an admin user fixture to `backend/tests/conftest.py` that creates a
   user with `role="admin"` and returns an authenticated TestClient session.

2. Create `backend/tests/test_admin.py`:
   - `test_metrics_requires_admin` (author session) → 403
   - `test_metrics_admin_success` → 200; metrics shape correct
   - `test_nlp_query_requires_admin` → 403
   - `test_nlp_query_admin_success` → 200; metrics + semantic_hits
   - `test_model_calls_requires_admin` → 403
   - `test_model_calls_admin_success` → 200; paginated shape
   - `test_admin_content_requires_admin` → 403
   - `test_admin_content_admin_success` → 200; admin reads any author's item
   - `test_unauthenticated_admin_routes` → 401 for every admin route

3. Mock all OpenAI embedding calls via `monkeypatch` / `unittest.mock`.

4. Run the full suite: `cd backend && uv run pytest tests/ -v`. Show the
   full output. Fix any failures before committing — do NOT xfail or skip.

5. Stage and commit with:
   `test: E2/E5 admin tests with 401/403 guard coverage`
```

11.
```
**Input:** Add the admin routes to the Postman collection as a new Admin
group with an auth note.

**Context:**
- The collection was renamed in 4.1a to
  `backend/postman/ScriptSprout.postman_collection.json`.
- Every admin request requires an authenticated admin session — make this
  explicit with a group-level note so users don't waste time debugging 403s.
- Preserve existing folders (Auth, Content, Regeneration, Thumbnail, Audio,
  etc.) verbatim — only append the new Admin group.

**Execution:**
1. Add a new folder `7. Admin (E2, E5)` to the collection with:
   - `GET /api/admin/metrics`
   - `POST /api/admin/nlp-query` (include an example body with `query_text`)
   - `GET /api/admin/model-calls?page=1&page_size=20`
   - `GET /api/admin/content/:id`

2. Add a folder-level description:
   "Requires admin session — log in as an admin user (bootstrapped via
   `ADMIN_USERNAME` / `ADMIN_PASSWORD` env vars)."

3. Stage and commit with:
   `docs: add admin routes to Postman collection`
```

12.
```
**Input:** Run the `validate-and-fix` skill across the backend until tests
and lint are both clean.

**Context:**
- The full suite now includes MVP tests, 4.1a tests, and the new E2/E5
  admin tests — everything must stay green.
- Do not short-circuit the loop (no xfail, no skip). Fix the underlying code.
- Do not proceed to push/PR until fully green and all fixes are committed.

**Execution:**
1. Run the `validate-and-fix` skill:
   - `/test-backend`
   - `/lint-backend`
   - Fix, re-run, repeat until both are clean.

2. Confirm:
   - Total tests passed, 0 failed
   - Ruff lint clean, 0 issues
   - All fix commits staged and committed
```

13.
```
**Input:** Push the branch, open the PR via GitHub MCP, and invoke the
`pr-reviewer` agent on it.

**Context:**
- Remote is `origin`, base branch is `main`.
- Use **GitHub MCP** for push, PR open, and agent invocation.
- This is the highest-risk PR in the series: first admin role, first
  cross-author reads, first vector store. The agent is expected to take
  this review seriously — any finding is worth investigating on camera.
- Tests and lint are already clean from the previous prompt.

**Execution:**
1. Using GitHub MCP, push `feat/enhancements-backend-admin` to `origin`.

2. Show me the commit summary for this branch.

3. Using GitHub MCP, open a PR with:
   - Base: `main`
   - Title: `feat: enhancements backend (admin surface) — E2 admin NLP/semantic, E5 admin dashboard`
   - Body (verbatim):

   ```
   ## What this PR contains

   The admin-facing backend enhancements on top of 4.1a — first admin role
   enforcement, first vector store, first cross-author visibility.

   ### E2 — Admin NLP / semantic investigation
   - `embedding_index.py` — Chroma upsert/delete
   - Auto-upsert wired into content_service and regeneration_service
   - `admin_service.nlp_query()` — embed query, semantic search, return hits + metrics
   - Admin-only route: POST /api/admin/nlp-query

   ### E5 — Admin dashboard
   - `require_admin` dependency fully enforced (activated from MVP stub)
   - Admin bootstrap from ADMIN_USERNAME/ADMIN_PASSWORD on startup (idempotent)
   - Routes: GET metrics, GET model-calls (paginated), GET content/{id} (cross-author read)

   ### Infrastructure
   - Chroma initialized on startup alongside SQLite
   - `.claude/rules/admin-and-search.md` — new rules file for admin guards and semantic patterns

   ### Quality
   - All tests passing (MVP + 4.1a + E2/E5 tests, including admin 403 guard)
   - Ruff lint clean
   - Postman collection updated with admin group

   ### Config additions
   - CLAUDE.md updated for Phase 4.1b
   - .env.example — Phase 4.1b variables added (Chroma, embeddings, admin bootstrap)
   ```

4. Return the PR URL.

5. Invoke the `pr-reviewer` agent:
   "Run the pr-reviewer agent on the feat/enhancements-backend-admin PR"

6. Alert me when complete:
   "PR #N has been reviewed. [X issues / No issues] found. Review comments
   are posted — check the PR when you're ready."
```


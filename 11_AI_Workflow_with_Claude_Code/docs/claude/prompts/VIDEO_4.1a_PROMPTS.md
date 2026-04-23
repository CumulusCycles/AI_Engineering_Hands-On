1.
```
**Role:** You are a senior backend engineer resuming the ScriptSprout build.
The MVP backend and frontend are merged; Phase 3 added GitHub MCP and the
pr-reviewer agent. You are starting the *author-facing* enhancements —
extending the existing content resource with OpenAI-powered features. You
care about: keeping each regenerate/media call ownership-guarded, logging
every OpenAI call for traceability, and *not* mixing admin/vector-store
concerns into this phase (those belong to the next video).

**Input:** Update the project-root `CLAUDE.md` to reflect the Phase 4.1a
scope before any code changes.

**Context:**
- CLAUDE.md last described Phase 3 (GitHub MCP + pr-reviewer agent).
- 4.1a is deliberately split from 4.1b: author-facing extensions only (E1,
  E3, E4). Admin surface (E2, E5) and Chroma land in the next video — do not
  mention those as "coming up" inside `CLAUDE.md`'s *current* scope section;
  only list them under the out-of-scope block.
- The hard-rules section already exists — append new rules, do not replace
  existing ones.
- Keep sections unrelated to Phase 4.1a (rules files, commands, validate-
  and-fix, MCP servers, agents) untouched.

**Execution:**
1. Edit `CLAUDE.md` with the following changes:

   a. Current phase → change to:
      "Phase 4.1a: Enhancements Backend — author-facing extensions
      (E1 regenerate, E3 thumbnail, E4 audio) on top of the MVP backend"

   b. Current build scope → replace with:
      E1 — Regenerate individual fields: title, description, story
           independently. Each regeneration: ownership guard, single-field
           OpenAI call, model call log
      E3 — Thumbnail generation: OpenAI images API, blob + MIME stored on
           content_item row. Generate and serve endpoints both
           ownership-guarded
      E4 — Audio narration (TTS): OpenAI speech API, blob + MIME + voice
           stored on content_item row. Generate and serve endpoints both
           ownership-guarded

   c. Out of scope for 4.1a (lands in 4.1b):
      E2 — Admin NLP / semantic investigation (Chroma, embeddings)
      E5 — Admin dashboard (require_admin activation, admin routes)
      Email verification, destructive cleanse, public discovery, billing,
      collaborative editing

   d. Append to hard rules:
      - Regenerating one field MUST NOT modify other fields
      - Media blobs (thumbnail, audio) stored in-database with MIME type
        alongside
      - Every generate/regenerate/media call logged to model_call_log

2. Stage and commit with:
   `docs: update CLAUDE.md for Phase 4.1a enhancements backend author-facing`
```

2.
```
**Input:** Read the three enhancement milestone docs and summarize only the
in-scope tracks (E1, E3, E4) for this video.

**Context:**
- The enhancement package defines five tracks (E1–E5). E2 and E5 are
  admin-facing — they are 4.1b's work; explicitly ignore them here.
- You already have full product context from `CLAUDE.md` and the rules files,
  so the summary should be grounded in the existing stack (FastAPI,
  SQLAlchemy 2.x async, OpenAI SDK).
- Do not write any code, create routes, or update services in this prompt —
  this is a read-and-align step.

**Execution:**
1. Read, in order:
   - `docs/reqs/enhancements/ENHANCEMENTS_BUSINESS_REQS.md`
   - `docs/reqs/enhancements/ENHANCEMENTS_FUNCTIONAL_REQS.md`
   - `docs/reqs/enhancements/ENHANCEMENTS_TECH_REQS.md`

2. For each of E1, E3, E4, summarize in three bullets:
   - What it does (author-facing behavior)
   - What new routes / services it requires
   - What new environment variables it needs

3. Confirm you are ignoring E2 and E5. Create nothing.
```

3.
```
Using GitHub MCP, please create and checkout a new feature branch called
feat/enhancements-backend-author from main. Confirm we are on the new branch.
```

4.
```
**Input:** Add the Phase 4.1a environment variables to `backend/app/config.py`
(Pydantic Settings) and to `.env.example`.

**Context:**
- Only E3 (thumbnail) and E4 (audio) introduce new env vars in this phase —
  E1 regeneration reuses the existing `OPENAI_API_KEY` and `OPENAI_MODEL`.
- Do NOT add Chroma, embedding, or admin variables yet. Those belong to
  4.1b. Adding them here would spread scope across two videos.
- Follow the existing convention in `config.py`: typed `Settings` attributes
  with defaults, loaded via Pydantic `BaseSettings`.
- `.env.example` already has labeled section headers per phase — mirror that
  format for Phase 4.1a.

**Execution:**
1. Update `backend/app/config.py` to add:
   - `OPENAI_IMAGE_MODEL: str = "dall-e-3"`
   - `THUMBNAIL_SIZE: str = "1024x1024"`
   - `THUMBNAIL_QUALITY: str = "standard"`
   - `THUMBNAIL_STYLE: str = "vivid"`
   - `OPENAI_TTS_MODEL: str = "tts-1"`
   - `TTS_VOICE_DEFAULT: str = "alloy"`

2. Append a new section to `.env.example`:

   ```
   # --- Phase 4.1a: Enhancements Backend (author-facing) ---
   # Thumbnail (DALL-E)
   OPENAI_IMAGE_MODEL=dall-e-3
   THUMBNAIL_SIZE=1024x1024
   THUMBNAIL_QUALITY=standard
   THUMBNAIL_STYLE=vivid

   # Audio TTS
   OPENAI_TTS_MODEL=tts-1
   TTS_VOICE_DEFAULT=alloy
   ```

3. Stage and commit with:
   `feat: add Phase 4.1a config vars for thumbnail and audio`
```

5.
```
**Input:** Add thumbnail and audio media columns to the `ContentItem` model
and two write methods to the content repository.

**Context:**
- Schema bootstrap runs on app startup (see `backend/app/db/init_db.py`);
  there is no Alembic in the project, so new nullable columns will be
  picked up on next start — no migration file needed.
- All new columns MUST be nullable — existing rows predate the enhancement
  and must not break on startup.
- Follow the existing repository pattern in `content_repo.py`: async
  functions, explicit commit, return the refreshed `ContentItem`.
- Do not wire these repository methods into any service yet — services land
  in the next three prompts.

**Execution:**
1. Update `backend/app/models/content_item.py` to add:
   - `thumbnail_blob: Mapped[bytes | None]` (LargeBinary, nullable)
   - `thumbnail_mime: Mapped[str | None]` (String, nullable — e.g. "image/png")
   - `audio_blob: Mapped[bytes | None]` (LargeBinary, nullable)
   - `audio_mime: Mapped[str | None]` (String, nullable — e.g. "audio/mpeg")
   - `audio_voice: Mapped[str | None]` (String, nullable — voice used for TTS)

2. Update `backend/app/repositories/content_repo.py` to add:
   - `update_thumbnail(db, content_id, blob: bytes, mime: str) -> ContentItem`
   - `update_audio(db, content_id, blob: bytes, mime: str, voice: str) -> ContentItem`

3. Stage and commit with:
   `feat: add thumbnail + audio columns and repo writers to ContentItem`
```

6.
```
**Input:** Build E1 — per-field regeneration for title, description, and
story. Each field regenerates independently.

**Context:**
- The hard rule from CLAUDE.md applies: regenerating one field MUST NOT
  modify the other two. This is the main invariant to protect.
- Follow the existing service pattern in `backend/app/services/content_service.py`
  (ownership check → OpenAI call → model_call_log entry → DB update → return).
- Use the existing `get_owned_content` FastAPI dependency for ownership —
  do NOT inline ownership checks on the routes. This is consistent with all
  author-facing content routes today.
- Every regenerate call MUST be logged to `model_call_log` (success or
  failure). Failures log with the error reason; the route still returns an
  appropriate HTTP error.
- Use the existing OpenAI client configuration (`OPENAI_MODEL`, `OPENAI_API_KEY`
  from Pydantic Settings) — no new env vars for E1.

**Execution:**
1. Create `backend/app/services/regeneration_service.py` with:
   - `regenerate_title(db, content_item_id, author_id) -> ContentItem`
   - `regenerate_description(db, content_item_id, author_id) -> ContentItem`
   - `regenerate_story(db, content_item_id, author_id) -> ContentItem`

   Each function:
   - Fetches and verifies ownership
   - Calls OpenAI with the item's existing fields as context, generating
     only the target field
   - Logs the call to `model_call_log` (success or failure)
   - Updates only the target field + `updated_at`; leaves other fields
     untouched
   - Returns the updated item

2. Update `backend/app/schemas/content.py` to add `RegenerateResponse`
   (same shape as `ContentResponse`).

3. Update `backend/app/routes/content.py` to add three routes:
   - `POST /content/{content_id}/regenerate/title` → `ContentResponse`
   - `POST /content/{content_id}/regenerate/description` → `ContentResponse`
   - `POST /content/{content_id}/regenerate/story` → `ContentResponse`

   All three use the `get_owned_content` dependency and delegate to the
   matching service function.

4. Stage and commit with:
   `feat: E1 per-field regeneration service and routes`
```

7.
```
**Input:** Build E3 — thumbnail generation and serving. Store the image
bytes in-database on the `content_item` row; serve via StreamingResponse.

**Context:**
- Use the DALL-E configuration added in PROMPT 4: `OPENAI_IMAGE_MODEL`,
  `THUMBNAIL_SIZE`, `THUMBNAIL_QUALITY`, `THUMBNAIL_STYLE`.
- Media blobs live on the `ContentItem` row itself (columns added in
  PROMPT 5). Do NOT introduce a separate media table.
- Both the generate and the serve endpoints MUST be ownership-guarded via
  the existing `get_owned_content` dependency — a user cannot fetch another
  user's thumbnail.
- Ownership denial returns `404` (not `403`) to avoid leaking the existence
  of other users' content — matches the established pattern on the existing
  content routes.
- Log every generate call to `model_call_log` with
  `operation="generate_thumbnail"`.

**Execution:**
1. Create `backend/app/services/thumbnail_service.py` with:
   - `generate_thumbnail(db, content_item_id, author_id) -> ContentItem`
     * Verify ownership via the existing pattern
     * Build an image prompt from the first ~200 chars of the story/synopsis
     * Call the OpenAI images API using the settings values
     * Download the generated image bytes
     * Log the model call with `operation="generate_thumbnail"`
     * Persist via `content_repo.update_thumbnail(blob, mime)`
     * Return the updated item

   - `get_thumbnail(db, content_item_id, author_id) -> tuple[bytes, str]`
     * Verify ownership
     * If no `thumbnail_blob`: raise HTTP 404
     * Return `(thumbnail_blob, thumbnail_mime)`

2. Update `backend/app/routes/content.py` to add:
   - `POST /content/{content_id}/thumbnail/generate` → `ContentResponse`
   - `GET /content/{content_id}/thumbnail` → `StreamingResponse`
     (Content-Type set from `thumbnail_mime`)

   Both routes use the `get_owned_content` dependency.

3. Stage and commit with:
   `feat: E3 thumbnail generation and serve routes`
```

8.
```
**Input:** Build E4 — TTS audio generation and serving. Same shape as E3
but for audio narration.

**Context:**
- Use the TTS config added in PROMPT 4: `OPENAI_TTS_MODEL`, `TTS_VOICE_DEFAULT`.
- The voice is a per-call parameter (optional query param on the generate
  route); if not provided, fall back to `settings.TTS_VOICE_DEFAULT`.
- `audio_mime` is `"audio/mpeg"` (we ship mp3 bytes). Persist
  `audio_voice` alongside the blob so we know which voice produced it.
- Ownership rules are identical to E3: both routes go through
  `get_owned_content`; ownership denial returns 404, not 403.
- Log every generate call to `model_call_log` with `operation="generate_audio"`.

**Execution:**
1. Create `backend/app/services/audio_service.py` with:
   - `generate_audio(db, content_item_id, author_id, voice: str | None = None) -> ContentItem`
     * Verify ownership
     * Resolve voice: param if provided, else `settings.TTS_VOICE_DEFAULT`
     * Call OpenAI speech with the story text + selected voice
     * Log the model call with `operation="generate_audio"`
     * Persist blob + `"audio/mpeg"` + voice via `content_repo.update_audio`
     * Return the updated item

   - `get_audio(db, content_item_id, author_id) -> tuple[bytes, str]`
     * Verify ownership
     * If no `audio_blob`: raise HTTP 404
     * Return `(audio_blob, audio_mime)`

2. Update `backend/app/routes/content.py` to add:
   - `POST /content/{content_id}/audio/generate?voice=<voice>` → `ContentResponse`
   - `GET /content/{content_id}/audio` → `StreamingResponse`
     (Content-Type: `audio/mpeg`)

   Both routes use the `get_owned_content` dependency.

3. Stage and commit with:
   `feat: E4 TTS audio generation and serve routes`
```

9.
```
**Input:** Add unit tests for the author-facing enhancement tracks (E1, E3,
E4) and confirm the full suite stays green.

**Context:**
- Tests live in `backend/tests/` and follow the existing `test_*.py` pattern
  (FastAPI `TestClient`, pytest fixtures, no live OpenAI calls).
- OpenAI regen / thumbnail / audio calls MUST be mocked — never hit the real
  OpenAI API from tests. Use `monkeypatch` or `unittest.mock`.
- Two authors must be set up in the ownership-denial tests so that author B
  can attempt to access author A's content. Ownership denial returns 404
  (not 403) — this is the established pattern; tests must assert 404.
- The E1 invariant is critical: `test_regenerate_title_authenticated` must
  assert that description and story are UNCHANGED after a title regen.

**Execution:**
1. Create `backend/tests/test_regeneration.py` (E1):
   - `test_regenerate_title_authenticated` → 200; title updated; description
     and story unchanged
   - `test_regenerate_title_unauthenticated` → 401
   - `test_regenerate_title_ownership_denial` (author B hits author A's item)
     → 404
   - `test_regenerate_description_authenticated` → 200
   - `test_regenerate_story_authenticated` → 200

2. Create `backend/tests/test_media.py` (E3, E4):
   - `test_thumbnail_generate_unauthenticated` → 401
   - `test_thumbnail_generate_ownership_denial` → 404
   - `test_thumbnail_serve_no_thumbnail` (GET before generate) → 404
   - `test_audio_generate_unauthenticated` → 401
   - `test_audio_generate_ownership_denial` → 404
   - `test_audio_serve_no_audio` (GET before generate) → 404

3. Run the full suite: `cd backend && uv run pytest tests/ -v`. Show me the
   full output. If any test fails (new or pre-existing), stop and fix before
   committing — do NOT xfail or skip.

4. Once all green, stage and commit with:
   `test: E1/E3/E4 unit tests with mocked OpenAI calls`
```

10.
```
**Input:** Extend the Postman collection with the new author-facing
enhancement routes, and rename the collection from MVP to full ScriptSprout.

**Context:**
- The current collection is `backend/postman/ScriptSprout_MVP.postman_collection.json`.
  Rename the file to `ScriptSprout.postman_collection.json` and update the
  collection's own `info.name` to match.
- Admin routes (E2, E5) are 4.1b's work — do NOT add them here.
- Preserve all existing folders (Auth, Content, Model Call Log, etc.) and
  their requests. Only *add* the new folders below.
- Each new request should have: method, URL with `:id` param, short
  description, and — where applicable — an example body.

**Execution:**
1. Rename `backend/postman/ScriptSprout_MVP.postman_collection.json` to
   `backend/postman/ScriptSprout.postman_collection.json` and update the
   collection `info.name` field.

2. Add three new folders:

   **4. Regeneration (E1)**
   - `POST /api/content/:id/regenerate/title`
   - `POST /api/content/:id/regenerate/description`
   - `POST /api/content/:id/regenerate/story`

   **5. Thumbnail (E3)**
   - `POST /api/content/:id/thumbnail/generate`
   - `GET /api/content/:id/thumbnail`

   **6. Audio (E4)**
   - `POST /api/content/:id/audio/generate`
   - `GET /api/content/:id/audio`

3. Stage and commit with:
   `docs: update Postman collection with E1/E3/E4 routes`
```

11.
```
**Input:** Run the `validate-and-fix` skill across the backend until tests
and lint are both clean.

**Context:**
- Use the `/test-backend` command for the test suite and `/lint-backend`
  for Ruff. The skill loop is defined in `.claude/skills/validate-and-fix.md`
  — follow it verbatim.
- Do NOT short-circuit the loop: do not xfail, skip, or delete failing tests
  to make the suite pass. Fix the underlying code.
- Do not proceed to the push/PR prompt until both gates are fully green and
  every fix is committed.

**Execution:**
1. Run the `validate-and-fix` skill:
   - `/test-backend`
   - `/lint-backend`
   - Fix any failures, re-run, repeat until both are clean.

2. When clean, confirm out loud:
   - Total tests passed and 0 failed
   - Ruff lint clean with 0 issues
   - All fix commits are staged and committed
```

12.
```
**Input:** Push the branch, open the PR via GitHub MCP, and invoke the
`pr-reviewer` agent on it.

**Context:**
- Remote is `origin`, base branch is `main`.
- Use **GitHub MCP** for push, PR open, and the agent invocation. Do NOT
  fall back to `git push` or `gh pr create`.
- Tests and lint were verified clean by the previous prompt — do not re-run
  them here.
- The PR body is part of the on-camera narrative; use the exact body below
  verbatim so it matches what viewers see on screen.

**Execution:**
1. Using GitHub MCP, push `feat/enhancements-backend-author` to `origin`.

2. Show me the commit summary for this branch before opening the PR.

3. Using GitHub MCP, open a pull request with:
   - Base branch: `main`
   - Title: `feat: enhancements backend (author-facing) — E1 regenerate, E3 thumbnail, E4 audio`
   - Body (verbatim):

   ```
   ## What this PR contains

   Three author-facing backend enhancements built on top of the MVP — per-field
   regeneration, thumbnail generation, and audio narration. Admin-facing tracks
   (E2, E5) land in the next PR.

   ### E1 — Per-field regeneration
   - `regeneration_service.py` — regenerate title, description, story independently
   - 3 new routes: POST /api/content/{id}/regenerate/{field}
   - Each call: ownership guard, single OpenAI call, model call logged

   ### E3 — Thumbnail generation
   - `thumbnail_service.py` — DALL-E generation, blob stored in content_item row
   - Routes: POST generate (ownership-guarded), GET serve (StreamingResponse)

   ### E4 — Audio narration
   - `audio_service.py` — OpenAI TTS, blob stored in content_item row
   - Routes: POST generate (ownership-guarded), GET serve (StreamingResponse)

   ### Quality
   - All tests passing (MVP + E1/E3/E4 tests)
   - Ruff lint clean
   - Postman collection updated

   ### Config additions
   - CLAUDE.md updated for Phase 4.1a
   - .env.example — Phase 4.1a variables added (image + TTS only)
   ```

4. Return the PR URL.

5. Invoke the `pr-reviewer` agent on the PR:
   "Run the pr-reviewer agent on the feat/enhancements-backend-author PR"

6. Alert me when the review completes in the standard form:
   "PR #N has been reviewed. [X issues / No issues] found. Review comments
   are posted — check the PR when you're ready."
```


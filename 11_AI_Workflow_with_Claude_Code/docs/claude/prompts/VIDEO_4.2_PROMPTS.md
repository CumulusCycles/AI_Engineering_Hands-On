1.
```
**Role:** You are a senior frontend engineer wiring up the final phase of
ScriptSprout. The backend (MVP + author enhancements + admin surface) is
fully merged; your job is to surface all five enhancement tracks in the React
UI. Your priorities are: field-local loading for regeneration (don't block
the whole page when one field refreshes), strict separation of the admin
surface from author sessions (admins see admin nav; authors never do), and
graceful handling of every async state (idle, loading, error, success/empty).

**Input:** Update the project-root `CLAUDE.md` to reflect Phase 4.2 and
signal that this is the final phase of the series.

**Context:**
- CLAUDE.md last described Phase 4.1b (admin surface backend).
- The application is considered *complete* at the end of this phase — call
  that out in the phase line so future sessions read it as the end state,
  not a midpoint.
- Hard rules do not change in this phase — the existing admin and semantic
  rules already cover the frontend implications. Do not duplicate them.
- Do not touch sections unrelated to Phase 4.2.

**Execution:**
1. Edit `CLAUDE.md` with the following changes:

   a. Current phase → change to:
      "Phase 4.2: Enhancements Frontend — final phase, wiring E1-E5 UI to
      enhancement backend routes. After this phase the ScriptSprout
      application is complete."

   b. Current build scope → replace with:
      E1 — Regeneration UI: per-field regenerate buttons in Studio with
           field-local loading — title, description, story each refresh
           independently
      E2 — Admin NLP query page: text input, submit, display metrics +
           semantic hits, empty state handling
      E3 — Thumbnail UI: generate button in Studio, preview in History list,
           full image in Studio detail view
      E4 — Audio UI: generate button in Studio, in-browser audio player with
           controls
      E5 — Admin dashboard: metrics display, paginated model call history,
           read-only content inspection — hidden from author sessions entirely

2. Stage and commit with:
   `docs: update CLAUDE.md for Phase 4.2 enhancements frontend`
```

2.
```
**Input:** Read the enhancement requirement docs and list the mockup files,
then summarize UI scope — without writing any code.

**Context:**
- You already have full product context from `CLAUDE.md` and the rules files.
- The mockups in `designs/mockup-pages/` cover the enhancement screens —
  several are first-time admin surfaces and must be mapped to pages
  explicitly so there's no ambiguity later.
- Every new async operation in this phase must handle the four states:
  idle, loading, error, success/empty. Confirm this in the summary.

**Execution:**
1. Read:
   - `docs/reqs/enhancements/ENHANCEMENTS_FUNCTIONAL_REQS.md`
   - `docs/reqs/enhancements/ENHANCEMENTS_BUSINESS_REQS.md`

2. List the files in `designs/mockup-pages/` so we can identify the new
   mockups.

3. Summarize:
   - Per track (E1–E5), the UI the track requires
   - Which mockup files map to which new pages (especially admin and NLP
     query)
   - The four async states that must be handled for every new async op

4. Do NOT create any files or run any builds in this prompt.
```

3.
```
Create a new feature branch `feat/enhancements-frontend` from `main`.
GitHub MCP creates the branch on the remote; raw `git` is still used locally
to check it out (Claude Code's shell does not have a native MCP "checkout").

1. Use GitHub MCP to create the remote branch `feat/enhancements-frontend`
   off `main`.
2. Locally: `git fetch origin && git checkout feat/enhancements-frontend`
   to check it out as a tracking branch.

Confirm we are on the new branch.
```

4.
```
**Input:** Extend the TypeScript types to cover every enhancement API
response shape — content (E1/E3/E4) and admin (E2/E5).

**Context:**
- Types must match the backend Pydantic schemas exactly. Any drift here
  becomes a runtime bug when the UI consumes the responses.
- Admin types are new territory — create `frontend/src/types/admin.ts` as a
  new file rather than mixing admin shapes into `content.ts`.
- Re-export all new types from `frontend/src/types/index.ts` to keep imports
  consistent with the existing convention.
- Do NOT change the content service or any page in this prompt — types
  first, call sites in subsequent prompts.

**Execution:**
1. Update `frontend/src/types/content.ts` `ContentResponse` to add the new
   media fields exposed by the enhanced backend (per the VIDEO_4.1a backend
   schema update):
   - `audio_voice: string | null` (the voice used for the most recent TTS
     generation; `null` if no audio has been generated)

   No separate `RegenerateResponse` is needed — regenerate routes return
   `ContentResponse`. No separate `ThumbnailAvailable` or `AudioAvailable`
   types either: the frontend uses `audio_voice !== null` to decide whether
   to render `<AudioPlayer>`, and `<ThumbnailPreview>` falls back to its
   placeholder via `img.onError` when no thumbnail exists.

2. Create `frontend/src/types/admin.ts` with:
   - `MetricsResponse` — `total_items`, `total_model_calls`, `success_rate`,
     `calls_by_operation: Record<string, number>`
   - `ModelCallResponse` — all `ModelCallLog` fields (id, user_id,
     content_item_id, operation, model_name, success, latency_ms,
     prompt_tokens, completion_tokens, error_class, created_at)
   - `ModelCallListResponse` — `items`, `total`, `page`, `page_size`
   - `NlpQueryRequest` — `query_text: string`
   - `NlpQueryResponse` — `query_text: string`, `semantic_hits:
     ContentResponse[]` (no `metrics` — `/admin/metrics` is a separate route
     that the dashboard calls independently)

3. Update `frontend/src/types/index.ts` to re-export all new types.

4. Stage and commit with:
   `feat: add enhancement + admin TypeScript types`
```

5.
```
**Input:** Extend `contentService.ts` with the E1/E3/E4 API calls and
create a new `adminService.ts` for E2/E5.

**Context:**
- Follow the existing fetch pattern in `contentService.ts`: use the shared
  `fetchApi` helper and always pass `credentials: "include"` so the session
  cookie rides along through the Vite proxy.
- The thumbnail and audio GET endpoints return binary bodies streamed by
  the browser's native `<img>` and `<audio>` elements — so `getThumbnailUrl`
  and `getAudioUrl` MUST return URL strings, NOT `fetch()` promises. The
  browser handles the request itself (including cookies).
- Do not introduce a new HTTP helper — reuse the existing `fetchApi` error
  handling, status parsing, and JSON conventions.
- Do not wire these services into pages in this prompt — pages are updated
  in PROMPTS 7–11.

**Execution:**
1. Update `frontend/src/services/contentService.ts` to add:
   - `regenerateTitle(contentId: number): Promise<ContentResponse>`
     → `POST /api/content/{contentId}/regenerate/title`
   - `regenerateSynopsis(contentId: number): Promise<ContentResponse>`
     → `POST /api/content/{contentId}/regenerate/synopsis`
   - `regenerateDescription(contentId: number): Promise<ContentResponse>`
     → `POST /api/content/{contentId}/regenerate/description`
   - `regenerateStory(contentId: number): Promise<ContentResponse>`
     → `POST /api/content/{contentId}/regenerate/story`
   - `generateThumbnail(contentId: number): Promise<ContentResponse>`
     → `POST /api/content/{contentId}/thumbnail/generate`
   - `getThumbnailUrl(contentId: number): string`
     → returns `/api/content/{contentId}/thumbnail`
   - `generateAudio(contentId: number): Promise<ContentResponse>`
     → `POST /api/content/{contentId}/audio/generate`
   - `getAudioUrl(contentId: number): string`
     → returns `/api/content/{contentId}/audio`

2. Create `frontend/src/services/adminService.ts` with:
   - `getMetrics(): Promise<MetricsResponse>` → `GET /api/admin/metrics`
   - `getModelCalls(page?: number, pageSize?: number): Promise<ModelCallListResponse>`
     → `GET /api/admin/model-calls`
   - `nlpQuery(data: NlpQueryRequest): Promise<NlpQueryResponse>`
     → `POST /api/admin/nlp-query`
   - `getContentItemAdmin(contentId: number): Promise<ContentResponse>`
     → `GET /api/admin/content/{contentId}`

3. Stage and commit with:
   `feat: extend content service and add admin service for enhancements`
```

6.
```
**Input:** Create two shared media components: `ThumbnailPreview` (small /
large variants) and `AudioPlayer` (native HTML5 audio with voice label).

**Context:**
- Read `designs/mockup-pages/` and `designs/COLOR_PALETTE.md` before building
  — all colors must come from the palette.
- Use native browser elements (`<img>`, `<audio controls>`) — do NOT build a
  custom audio player or thumbnail loader. Native handles accessibility,
  keyboard support, and binary streaming for free.
- Image load errors (missing thumbnail, network hiccup) should fall back to
  the placeholder — NOT crash the component.
- The parent component (Studio, History) decides whether to render; for
  audio, don't render at all when no audio exists.

**Execution:**
1. Create `frontend/src/components/ThumbnailPreview.tsx`:
   - Props: `contentId: number`, `size: "small" | "large"`
   - If thumbnail exists: render `<img src={getThumbnailUrl(contentId)} />`
   - If no thumbnail: render a styled placeholder (camera icon or
     "No thumbnail" text)
   - Handle the image `onError` fallback to the placeholder
   - Small = compact History list layout; Large = full-width Studio layout

2. Create `frontend/src/components/AudioPlayer.tsx`:
   - Props: `contentId: number`, `voiceName: string | null`
   - Render `<audio controls src={getAudioUrl(contentId)} />`
   - If `voiceName` is provided: show a label (e.g. "Voice: alloy")
   - If `voiceName` is null: omit the label
   - Return null if no audio should render (parent controls visibility)

3. Stage and commit with:
   `feat: add ThumbnailPreview and AudioPlayer components`
```

7.
```
**Input:** Update `StudioPage.tsx` to add the E1 (per-field regeneration),
E3 (thumbnail generate + display), and E4 (audio generate + playback) UI in
the view-mode content panel.

**Context:**
- Read the Studio mockup in `designs/mockup-pages/` before updating. Colors
  from `designs/COLOR_PALETTE.md`.
- Field-local loading is the critical UX invariant for E1 (functional
  requirement R-3): when the author regenerates the title, ONLY the title
  shows a spinner — synopsis, description, and story stay readable and
  their buttons stay active. Use four independent state slices (one per
  field: title, synopsis, description, story), not a single page-level
  loading flag.
- Regenerate/generate buttons should only appear when the underlying field
  has content (e.g., don't show "Regenerate title" on a freshly-created,
  not-yet-generated item).
- If thumbnail / audio already exist when the page loads, show them
  immediately — the generate button is for the *create* case, not for
  re-displaying existing media.
- Error handling is field-scoped: an E1 title error shows an `ErrorMessage`
  next to the title only, not a page-wide banner.

**Execution:**
1. Update `StudioPage.tsx` view-mode content panel to add:

   **E1 — Per-field regeneration** (title, synopsis, description, story):
   - Four independent loading states (one per field)
   - Each field gets a "Regenerate" button, shown only when the field has
     content
   - While regenerating: that field shows a loading indicator; its button
     is disabled; other fields remain untouched and interactive
   - Error: scoped `ErrorMessage` below the affected field
   - Success: update the field content in place
   - Call `contentService.regenerateTitle / regenerateSynopsis /
     regenerateDescription / regenerateStory`

   **E3 — Thumbnail** (below the content panel):
   - "Generate Thumbnail" button — visible only when `story` is present
   - Loading / error / success states handled locally
   - On success or if thumbnail already exists: render
     `<ThumbnailPreview contentId={id} size="large" />`

   **E4 — Audio** (below the thumbnail):
   - "Generate Audio" button — visible only when `story` is present
   - Loading / error / success states handled locally
   - On success or if audio already exists: render
     `<AudioPlayer contentId={id} voiceName={item.audio_voice} />`

2. Stage and commit with:
   `feat: E1/E3/E4 studio UI — per-field regen, thumbnail, audio`
```

8.
```
**Input:** Update `HistoryPage.tsx` so each content item row shows a small
thumbnail preview alongside the existing text metadata.

**Context:**
- Read the History mockup in `designs/mockup-pages/` before updating.
- Existing row behavior (click → `/studio?id={contentId}`; status badge;
  subject/title/created date) must remain untouched — this is an *addition*,
  not a restructure.
- Items without a thumbnail must show the placeholder from
  `ThumbnailPreview` — not a broken image icon and not an empty box.
- Layout: thumbnail as a small square to the left of the row's text content,
  matching the history mockup.

**Execution:**
1. Update `HistoryPage.tsx` so each content item row renders
   `<ThumbnailPreview contentId={item.id} size="small" />` to the left of
   the existing metadata block.

2. Preserve all existing behavior (navigation, status badge, date display).

3. Stage and commit with:
   `feat: E3 thumbnail previews in History list`
```

9.
```
**Input:** Add an `AdminRoute` variant of `ProtectedRoute`, wire the admin
pages into the router, and hide admin nav links from author sessions.

**Context:**
- `AdminRoute` should mirror `ProtectedRoute`'s auth-loading and auth-not-yet-
  known handling — do not let an admin-check race the auth initialization.
- Redirect semantics matter: authenticated-but-not-admin → `/studio`
  (not `/login`). Sending a legitimate author to `/login` would be confusing
  and wrong. Only unauthenticated users go to `/login`.
- Admin nav links must be completely hidden from author sessions — not
  disabled, not greyed out, *hidden*. This matches CLAUDE.md's admin surface
  invariant ("hidden from author sessions entirely").
- This prompt does NOT create the admin pages themselves — those land in
  PROMPTS 10 and 11. Route registration in `App.tsx` is therefore deferred
  to PROMPT 11 (after both pages exist) so the project never enters a
  broken state where `App.tsx` imports a non-existent module.

**Execution:**
1. Update `frontend/src/auth/ProtectedRoute.tsx` to add an `AdminRoute`
   component that:
   - Applies the same auth-loading guard as `ProtectedRoute`
   - If not authenticated: redirect to `/login`
   - If authenticated but `user.role !== "admin"`: redirect to `/studio`
   - Otherwise: render children

2. Update `Layout.tsx` so the Admin nav link(s) only render when
   `user?.role === "admin"`. Point the link at `/admin`; the route will be
   wired in PROMPT 11 once both admin pages exist.

3. Stage and commit with:
   `feat: add AdminRoute guard and conditional admin nav (routes wired in PROMPT 11)`
```

10.
```
**Input:** Create `frontend/src/pages/AdminPage.tsx` — the admin dashboard
with a metrics section and a paginated model-call history section.

**Context:**
- Read the admin mockup in `designs/mockup-pages/` (`admin-dashboard.html`,
  `admin-model-calls.html`) before building. Colors from
  `designs/COLOR_PALETTE.md`.
- Metrics and model-call history are INDEPENDENT async loads. Each must
  handle its own four states (loading/error/empty/success). A metrics
  error must not blank out the model-call list, and vice versa.
- Pagination starts at page 1. Clicking next/prev issues a new
  `getModelCalls(page)` call — do not pre-fetch adjacent pages.
- Include a navigation entry point to `/admin/nlp` (built in the next
  prompt).

**Execution:**
1. Create `frontend/src/pages/AdminPage.tsx` with two independent sections:

   **Metrics (top):**
   - On mount: `adminService.getMetrics()`
   - Handle loading / error / success independently
   - On success: render metrics cards — total items, total model calls,
     success rate (as percentage), calls by operation (list or small table)

   **Model call history (below metrics):**
   - On mount: `adminService.getModelCalls(1)`
   - Handle loading / error / empty / success independently
   - Columns: operation, model name, success (✓/✗), latency, tokens,
     created date
   - Prev/next pagination controls with current-page indicator
   - On page change: `adminService.getModelCalls(newPage)`

2. Add a navigation link to `/admin/nlp` for the NLP query tool.

3. Stage and commit with:
   `feat: E5 admin dashboard page with metrics and paginated history`
```

11.
```
**Input:** Create `frontend/src/pages/AdminNlpPage.tsx` — the admin semantic
investigation tool.

**Context:**
- Read `search-bar.html`, `search-results.html`, and `search-empty.html` in
  `designs/mockup-pages/` before building. Colors from
  `designs/COLOR_PALETTE.md`.
- The empty-state treatment (no semantic hits) is a functional requirement
  (S-3): show an explicit "No matching content found for your query"
  empty state rather than an empty list.
- Four async states for the results area: idle (initial, no query yet),
  loading, error, success. Success can itself have hits OR be empty.
- Each hit shows: subject, title (or placeholder), `author_id`, status.
  Author IDs are admin-only data — that's intentional; this page is
  AdminRoute-guarded.
- Include a back link to `/admin` so the admin can return to the dashboard.

**Execution:**
1. Create `frontend/src/pages/AdminNlpPage.tsx` with:

   **Query form:**
   - Text input with placeholder "Ask a question about your content..."
   - Submit button labeled "Search"
   - Client-side validation: `query_text` must be non-empty; block submit
     if empty

   **Results (state machine):**
   - `idle`: show only the form
   - `loading`: disable the form; show `LoadingSpinner` in the results area
   - `error`: show `ErrorMessage`
   - `success`:
     - Semantic hits list: one row per hit (subject, title/placeholder,
       `author_id`, status)
     - If hits empty: show `EmptyState` with copy "No matching content
       found for your query" per S-3

2. Add a back link to `/admin`.

3. Now that both `AdminPage` and `AdminNlpPage` exist, wire the admin
   routes into `frontend/src/App.tsx`:
   - `/admin` → `AdminPage` wrapped in `AdminRoute`
   - `/admin/nlp` → `AdminNlpPage` wrapped in `AdminRoute`

   Registering both routes here (rather than in PROMPT 9) avoids the
   temporary "unresolved module" state Vite would otherwise hit between
   PROMPT 9 and PROMPT 11.

4. Stage and commit with:
   `feat: E2 admin NLP query page (+ wire admin routes in App.tsx)`
```

12.
```
**Input:** Add unit tests for the E1/E3/E4 Studio UI, the E5 Admin
dashboard, and the E2 Admin NLP page.

**Context:**
- Mock ALL service calls with `vi.mock` or per-test overrides — no real
  network calls. Follow the existing test patterns in
  `frontend/src/tests/`.
- The field-local loading assertion for E1 is the single most important
  test: clicking "Regenerate title" must show loading on the title ONLY,
  while the description and story remain non-loading. This guards the R-3
  invariant from CLAUDE.md.
- The NLP empty-state test guards the S-3 invariant — when `semantic_hits`
  is an empty array, the page must render the `EmptyState`, not a blank
  results area.
- Admin tests should assert pagination actually calls
  `getModelCalls(page)` with the right page number, not just that the
  buttons render.

**Execution:**
1. Create `frontend/src/tests/StudioPageEnhancements.test.tsx`:
   - `test_regenerate_title_button_appears_when_title_exists`
   - `test_regenerate_title_shows_field_loading` — loading on title only;
     synopsis, description, and story NOT in loading state
   - `test_regenerate_title_error` — `ErrorMessage` scoped to title only
   - `test_regenerate_title_success` — updated title shown in place
   - `test_regenerate_synopsis_shows_field_loading` — loading on synopsis
     only; other three fields NOT in loading state
   - `test_regenerate_synopsis_success` — updated synopsis shown in place
   - `test_generate_thumbnail_button_appears_when_story_exists`
   - `test_generate_thumbnail_loading_state`
   - `test_generate_thumbnail_error`
   - `test_generate_audio_button_appears_when_story_exists`
   - `test_generate_audio_loading_state`
   - `test_generate_audio_error`

2. Create `frontend/src/tests/AdminPage.test.tsx`:
   - `test_admin_page_shows_loading`
   - `test_admin_page_shows_metrics_on_success`
   - `test_admin_page_shows_model_calls`
   - `test_admin_page_pagination` — next page triggers `getModelCalls(2)`
   - `test_admin_page_error` — `getMetrics` reject renders `ErrorMessage`

3. Create `frontend/src/tests/AdminNlpPage.test.tsx`:
   - `test_nlp_form_renders`
   - `test_nlp_validation` — empty submit blocks the API call
   - `test_nlp_loading_state`
   - `test_nlp_empty_state` — empty `semantic_hits` renders `EmptyState`
   - `test_nlp_results` — hits render one row each
   - `test_nlp_error` — `nlpQuery` reject renders `ErrorMessage`

4. Run the suite: `cd frontend && npm run test`. Show the full output. Fix
   any failures before committing — do NOT skip.

5. Stage and commit with:
   `test: enhancement UI tests for Studio, Admin, and NLP pages`
```

13.
```
**Input:** Run the `validate-and-fix` skill across the frontend until tests
and lint are both clean.

**Context:**
- Use `/test-frontend` (Vitest) and `/lint-frontend` (ESLint).
- Do not short-circuit by skipping or xfailing tests. Fix the code.
- Do not proceed to the smoke test or PR until fully green and all fixes
  are committed.

**Execution:**
1. Run the `validate-and-fix` skill: `/test-frontend`, `/lint-frontend`.
   Fix, re-run, repeat until both are clean.

2. Confirm:
   - Total tests passed, 0 failed
   - ESLint clean, 0 errors
   - All fix commits staged and committed
```

14.
```
Before starting the frontend, confirm the backend is running and the
required env vars are set in the project-root `.env`:

1. Confirm `.env` has `OPENAI_API_KEY` set (used for generation, embeddings,
   thumbnails, audio) AND `ADMIN_USERNAME` + `ADMIN_PASSWORD` set (the
   admin bootstrap reads these on backend startup; admin-only flows in
   this smoke test require an admin user to log in as).

2. The backend was likely stopped at the end of an earlier phase. In a
   separate terminal, start it again:
   `cd backend && uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`
   Watch the startup log for "Admin user bootstrapped" or "Admin user
   already exists" — if you see "Admin bootstrap skipped (credentials not
   set)", stop and set `ADMIN_USERNAME` / `ADMIN_PASSWORD` first.

3. Then start the frontend dev server: from `frontend/`, run `npm run dev`.
   Confirm it starts on port 5173 with no errors and alert me when it is
   ready. I will walk through the complete application flow in the
   browser — author flow (E1/E3/E4) AND admin flow (E2/E5).
```

15.
```
**Input:** Run the **`log-claude-build`** procedure in **`.claude/skills/log-claude-build.md`** for **`VIDEO_4.2`**.

**Context:**
- Execute it yourself—do not ask the learner to trigger the skill manually.
- Stay on **`feat/enhancements-frontend`**. Ground summaries in **`git log` / `git diff`** for harness paths only (`CLAUDE.md`, `.claude/`).

**Execution:**
1. Follow the skill end-to-end with **`VIDEO_ID=VIDEO_4.2`**.
2. Stage and commit with: `docs: VIDEO_4.2 harness build notes`
```

16.
```
**Input:** Push the branch, open the PR via GitHub MCP, and invoke the
`pr-reviewer` agent on it.

**Context:**
- Remote is `origin`, base branch is `main`.
- Use **GitHub MCP** for push, PR open, and agent invocation.
- This is the final PR of the series — after merging, `main` is the full
  ScriptSprout application.
- Tests, lint, and the smoke test are already clean from the previous
  prompts.

**Execution:**
1. Using GitHub MCP, push `feat/enhancements-frontend` to `origin`.

2. Show me the commit summary for this branch.

3. Using GitHub MCP, open a PR with:
   - Base: `main`
   - Title: `feat: enhancements frontend — E1-E5 UI complete`
   - Body (verbatim):

   ```
   ## What this PR contains

   All five frontend enhancements wired to the enhancement backend — completing the
   full ScriptSprout application.

   ### E1 — Per-field regeneration UI
   - Regenerate buttons on title, description, story in Studio view mode
   - Field-local loading: only the regenerating field shows a spinner
   - Field-scoped error messages — other fields unaffected

   ### E2 — Admin NLP query page
   - AdminNlpPage: text input, submit, semantic hits display (metrics live on /admin)
   - Empty state for no results per functional requirements S-3
   - All four async states handled

   ### E3 — Thumbnail UI
   - ThumbnailPreview component (small/large variants)
   - Generate button in Studio, full preview in Studio view
   - Small thumbnail in History list with placeholder for items without thumbnails

   ### E4 — Audio UI
   - AudioPlayer component using native HTML5 audio controls
   - Generate button in Studio, player appears on success
   - Voice label displayed alongside player

   ### E5 — Admin dashboard
   - AdminPage: metrics cards + paginated model call history
   - AdminNlpPage: semantic investigation tool
   - AdminRoute guard: admin-only, authors redirected to /studio
   - Admin nav links hidden from author sessions entirely

   ### Quality
   - All tests passing (MVP + enhancement tests)
   - ESLint clean
   - Full end-to-end smoke test complete — all features working

   ### Config additions
   - CLAUDE.md updated for Phase 4.2 — final phase
   ```

4. Return the PR URL.

5. Invoke the `pr-reviewer` agent:
   "Run the pr-reviewer agent on the feat/enhancements-frontend PR"

6. Alert me when complete:
   "PR #N has been reviewed. [X issues / No issues] found. Review comments
   are posted — check the PR when you're ready."
```


1.
```
**Role:** You are a senior frontend engineer starting the MVP frontend build
phase for ScriptSprout. You follow the conventions in
`.claude/rules/frontend-react-vite-typescript.md`: all fetch calls live in
service modules, typed request/response shapes, all four async states handled
everywhere, colors exclusively from `designs/COLOR_PALETTE.md`, layout from
`designs/mockup-pages/`. You treat `CLAUDE.md` as a living artifact and update
it at the start of every phase before writing code.

**Input:** Update the existing `CLAUDE.md` so it reflects the current phase
(Phase 2.2 — frontend build) and the concrete scope we are about to implement.

**Context:**
- `CLAUDE.md` already exists with project overview, stack, and hard rules —
  keep those intact. Only update phase-related sections.
- Backend from Phase 2.1 is complete and running on port 8000. Frontend will
  proxy `/api/*` to it via Vite's dev server.
- MVP scope for the frontend is a filtered subset — regeneration, admin,
  thumbnails, and audio are explicitly deferred.

**Execution:**
1. Update the **Current phase** section to read:
   `"Phase 2.2: Frontend Build — building the React/TypeScript/Vite frontend
   wired to the MVP backend"`
2. Replace the **Current build scope** section with:
   - React/TypeScript/Vite frontend initialized with npm
   - Vite proxy configured to forward `/api/*` to backend on port 8000
   - Auth context: session state, login/logout, hydration from `/api/auth/me`
   - API service modules: all fetch calls in `services/`, never in components
   - TypeScript types matching all backend response schemas
   - Client-side routing with protected routes for authenticated pages
   - Pages: HomePage, LoginPage, RegisterPage, StudioPage (create + generate),
     HistoryPage
   - All four async states handled everywhere: loading, error, empty, success
   - Colors from `designs/COLOR_PALETTE.md` only — no hardcoded hex values
   - Layout matches `designs/mockup-pages/` for each page
   - Unit tests: submit success, validation failure, loading/error states
3. Leave **Out of scope** unchanged (regeneration, admin, embeddings,
   thumbnails, audio).
4. Stage and commit with message:
   `docs: update CLAUDE.md for Phase 2.2 frontend build`
```

2.
```
**Input:** Read the frontend-relevant MVP specs and designs, then summarize
your understanding of what we're building and what it should look like.

**Context:**
- Functional REQs define behavior; designs define visual intent. We need both
  grounded before writing components.
- The list of available mockups is not hardcoded — list the directory to see
  what exists.

**Execution:**
1. Read in this order:
   - `docs/reqs/mvp/MVP_FUNCTIONAL_REQS.md`
   - `designs/README.md`
   - `designs/COLOR_PALETTE.md`
2. List the files in `designs/mockup-pages/` so we know what mockups exist.
3. Summarize:
   - The pages the frontend needs (from the functional requirements)
   - The four async states every operation must handle
   - The color palette we must use
   - Which mockup files map to which pages
4. Do not create any files yet.
```

3.
```
Please check git status, then create and checkout a new feature branch called
feat/frontend-mvp. Confirm we are on the new branch.
```

4.
```
**Input:** Add three frontend workflow commands to `.claude/commands/` so the
validate-and-fix skill has what it needs at the end of this phase.

**Context:**
- Same pattern as Phase 2.1: commands added BEFORE the code that needs them,
  not after.
- Vite's default dev server port is 5173.

**Execution:**
1. Create `.claude/commands/test-frontend.md`:
   - Navigate to `frontend/`
   - Run: `npm run test`
   - Report results
2. Create `.claude/commands/lint-frontend.md`:
   - Navigate to `frontend/`
   - Run: `npm run lint`
   - Report any issues found
3. Create `.claude/commands/run-frontend.md`:
   - Navigate to `frontend/`
   - Run: `npm run dev`
   - Confirm it starts on port 5173
4. Update `.claude/README.md` to note that frontend commands have been added
   in Phase 2.2.
5. Stage all files and commit with a Conventional Commit message.
```

5.
```
**Input:** Scaffold the React/TypeScript/Vite project in `frontend/` and
install all dependencies needed for the MVP.

**Context:**
- Use the official `npm create vite@latest` scaffold with the `react-ts` template.
- We need `react-router-dom` for client-side routing.
- Testing stack is Vitest + React Testing Library running in jsdom.

**Execution:**
1. From the project root, run:
   `npm create vite@latest frontend -- --template react-ts`
2. Navigate to `frontend/` and run `npm install`.
3. Install runtime deps: `npm install react-router-dom`
4. Install dev deps:
   ```
   npm install --save-dev vitest @testing-library/react \
     @testing-library/jest-dom @testing-library/user-event jsdom \
     @vitest/coverage-v8
   ```
5. Add the test scripts to `frontend/package.json`. The Vite `react-ts`
   template ships with `dev`, `build`, `lint`, `preview` scripts but does
   NOT include a `test` script. Add:
   - `"test": "vitest"`
   - `"test:coverage": "vitest --coverage"`
   The `/test-frontend` slash command (and prompts 16–17) call `npm run test`,
   so this script must exist.
6. Show me `package.json` so I can confirm everything looks right.
```

6.
```
**Input:** Configure `vite.config.ts` with the dev server proxy and Vitest
settings, create the test setup file, and verify TypeScript strict mode in
`tsconfig.json`.

**Context:**
- The backend runs on port 8000. Vite's dev server proxy forwards `/api/*`
  and `/health` to it so the frontend can call the backend without CORS issues
  in development.
- Vitest reads its config from `vite.config.ts`. To get TypeScript types for
  the `test` field without a triple-slash directive, import `defineConfig`
  from `'vitest/config'` instead of `'vite'`.
- The setup file (`src/tests/setup.ts`) is created here, not in prompt 16,
  so the `setupFiles` reference in `vite.config.ts` resolves immediately —
  anyone running `npm run test` between this prompt and the test-writing
  prompt won't hit a missing-file error.

**Execution:**
1. Update `frontend/vite.config.ts`:
   - `import { defineConfig } from 'vitest/config'` (NOT from `'vite'` — the
     vitest version exposes the `test` field types)
   - Proxy `/api/*` to `http://localhost:8000`
   - Proxy `/health` to `http://localhost:8000`
   - Add Vitest config: `environment: 'jsdom'`, `globals: true`,
     `setupFiles: ['src/tests/setup.ts']`
2. Create `frontend/src/tests/setup.ts` with a single line:
   `import '@testing-library/jest-dom'`
   This makes its matchers (e.g. `toBeInTheDocument`) available in every
   test without per-file imports.
3. Verify `frontend/src/vite-env.d.ts` exists (Vite generates this).
4. Update `frontend/tsconfig.json` to ensure strict mode is on and paths
   resolve correctly.
5. Show me the final `vite.config.ts` before committing.
6. Stage and commit with a Conventional Commit message.
```

7.
```
**Input:** Define TypeScript interfaces mirroring the backend API schemas.
All types live in `frontend/src/types/`.

**Context:**
- Types are the shared contract between service modules and the components
  that consume them. Field names must match the backend schemas exactly.
- `ApiError` extends `Error` so it can be thrown and caught cleanly with
  `instanceof ApiError`.

**Execution:**
1. Create `frontend/src/types/auth.ts`:
   - `RegisterRequest`: `{ username: string; password: string; email?: string }`
   - `LoginRequest`: `{ username: string; password: string }`
   - `AuthResponse`: `{ id: number; username: string; role: string; created_at: string }`
   - `MessageResponse`: `{ message: string }`
2. Create `frontend/src/types/content.ts`:
   - `ContentCreateRequest`: `{ subject: string; genre: string; audience: string; runtime: string }`
   - `ContentResponse`: `{ id: number; author_id: number; subject: string;
     genre: string; audience: string; runtime: string;
     title: string | null; synopsis: string | null;
     description: string | null; story: string | null;
     status: string; created_at: string; updated_at: string }`
   - `ContentListResponse`: `{ items: ContentResponse[]; total: number }`
3. Create `frontend/src/types/common.ts`:
   - `ErrorResponse`: `{ code: string; message: string }`
   - `ApiError`: extends `Error` with `code: string` and `status: number`
4. Create `frontend/src/types/index.ts` that re-exports all types from the
   files above.
5. Stage and commit with a Conventional Commit message.
```

8.
```
**Input:** Create the API client layer — a base `fetchApi` helper plus
`authService` and `contentService` modules. All fetch calls live here.

**Context:**
- All fetch calls live in services, never directly in components (per
  `.claude/rules/frontend-react-vite-typescript.md`).
- **`credentials: "include"` is required on every fetch** — without it the
  session cookie isn't sent and every authenticated call will 401.
- The Vite proxy handles routing, so the base URL is an empty string — just
  call `/api/...` from the services.

**Execution:**
1. Create `frontend/src/services/api.ts` — base client:
   - Base URL: empty string (Vite proxy handles routing)
   - `fetchApi<T>()` helper that:
     - Sends fetch with `credentials: "include"`
     - Sets `Content-Type: application/json` for non-GET requests
     - On non-ok response: reads the error body and throws `ApiError` with
       `code` + `message`
     - On ok response: parses and returns JSON as `T`
   - Export `fetchApi` for use in other service modules.
2. Create `frontend/src/services/authService.ts`:
   - `register(data: RegisterRequest) → Promise<AuthResponse>` — POST `/api/auth/register`
   - `login(data: LoginRequest) → Promise<AuthResponse>` — POST `/api/auth/login`
   - `logout() → Promise<MessageResponse>` — POST `/api/auth/logout`
   - `getMe() → Promise<AuthResponse>` — GET `/api/auth/me`
3. Create `frontend/src/services/contentService.ts`:
   - `createContentItem(data: ContentCreateRequest) → Promise<ContentResponse>` — POST `/api/content/`
   - `generateContent(contentId: number) → Promise<ContentResponse>` — POST `/api/content/{contentId}/generate`
   - `listMyContent() → Promise<ContentListResponse>` — GET `/api/content/`
   - `getContentItem(contentId: number) → Promise<ContentResponse>` — GET `/api/content/{contentId}`
4. Stage and commit with a Conventional Commit message.
```

9.
```
**Input:** Create the auth context (`AuthContext.tsx`) and the `ProtectedRoute`
wrapper that consumes it.

**Context:**
- Session hydration happens on mount via `authService.getMe()`. While the
  hydration request is in-flight, `isLoading = true`.
- **`ProtectedRoute` MUST handle the loading state before deciding to redirect.**
  Otherwise a logged-in user who refreshes sees a flash of the login page
  while `/api/auth/me` is still resolving.

**Execution:**
1. Create `frontend/src/auth/AuthContext.tsx`:
   - `AuthState` type: `{ user: AuthResponse | null; isLoading: boolean; isAuthenticated: boolean }`
   - Context value:
     - `user: AuthResponse | null`
     - `isLoading: boolean` (true while hydrating from `/api/auth/me` on mount)
     - `isAuthenticated: boolean`
     - `login(data: LoginRequest) → Promise<void>` — calls `authService.login`, sets user
     - `logout() → Promise<void>` — calls `authService.logout`, clears user
     - `register(data: RegisterRequest) → Promise<void>` — calls `authService.register`
   - `AuthProvider` component:
     - On mount: call `authService.getMe()` to hydrate session state
     - While hydrating: `isLoading = true`
     - If `getMe()` succeeds: set user, `isAuthenticated = true`
     - If `getMe()` fails (401 or network): `user = null`, `isAuthenticated = false`
     - Wrap children in `AuthContext.Provider`
   - `useAuth()` hook: returns context, throws if used outside `AuthProvider`
2. Create `frontend/src/auth/ProtectedRoute.tsx`:
   - Takes `children` as prop
   - If `isLoading`: show a loading spinner or skeleton
   - If not `isAuthenticated`: redirect to `/login`
   - Otherwise: render children
3. Stage and commit with a Conventional Commit message.
```

10.
```
**Input:** Set up the React Router with all MVP routes and route guards in
`App.tsx`, and confirm `main.tsx` is correct.

**Context:**
- Route guards enforce authentication consistently — no ad-hoc checks in
  components (per `.claude/rules/frontend-react-vite-typescript.md`).
- Public auth pages should redirect authenticated users to `/studio` — no
  point showing login to someone who's already signed in.

**Execution:**
1. Update `frontend/src/App.tsx`:
   - Wrap everything in `AuthProvider`
   - Set up `BrowserRouter` with these routes:
     - `/` → `HomePage` for unauthenticated visitors (public landing); redirect
       to `/studio` if authenticated
     - `/login` → `LoginPage` (public, redirect to `/studio` if authenticated)
     - `/register` → `RegisterPage` (public, redirect to `/studio` if authenticated)
     - `/studio` → `StudioPage` (protected — wrap in `ProtectedRoute`)
     - `/history` → `HistoryPage` (protected — wrap in `ProtectedRoute`)
     - `*` → redirect to `/` (catch-all)
2. Confirm `frontend/src/main.tsx` mounts `App` to `#root` correctly. No
   changes should be needed beyond what Vite scaffolded.
3. Stage and commit with a Conventional Commit message.
```

11.
```
**Input:** Create four shared UI components used across multiple pages:
`Layout`, `LoadingSpinner`, `ErrorMessage`, `EmptyState`.

**Context:**
- Colors MUST come from `designs/COLOR_PALETTE.md` — no hardcoded hex values
  outside the palette.
- Layout MUST reference the relevant mockup in `designs/mockup-pages/`.
- Logo and brand assets come from `designs/brand/`.
- Read `designs/COLOR_PALETTE.md` and the relevant mockup files before
  writing any component.

**Execution:**
1. Read `designs/COLOR_PALETTE.md` and the `designs/mockup-pages/` files
   relevant to the shell/nav before writing code.
2. Create `frontend/src/components/Layout.tsx`:
   - Outer shell: navigation bar + main content area
   - Navigation bar shows the app logo/name (from `designs/brand/`) and nav links
   - Authenticated: show links to Studio and History plus a logout button
   - Unauthenticated: show links to Login and Register
3. Create `frontend/src/components/LoadingSpinner.tsx`:
   - Simple centered spinner component, used for full-page loading states
4. Create `frontend/src/components/ErrorMessage.tsx`:
   - Displays error code + human-readable message, used for API error states
5. Create `frontend/src/components/EmptyState.tsx`:
   - Displays an empty state message with optional call-to-action, used
     when content lists are empty
6. Stage and commit with a Conventional Commit message.
```

12.
```
**Input:** Build the Login and Register pages — entry points for all users.
Both pages must handle all four async states.

**Context:**
- Read the login and register mockups in `designs/mockup-pages/` before building.
- Colors exclusively from `designs/COLOR_PALETTE.md`.
- Use `useAuth()` from `AuthContext` — don't call the auth service directly
  from the component.

**Execution:**
1. Create `frontend/src/pages/LoginPage.tsx`:
   - Form: username, password fields
   - Validates both fields required before submit
   - On submit: calls `useAuth().login()`
   - States:
     - idle: form ready to submit
     - loading: disable form, show loading indicator on button
     - error: show `ErrorMessage` with the API error
     - success: redirect to `/studio`
   - Link to `/register` for new users
   - Layout matches the login mockup in `designs/mockup-pages/`
2. Create `frontend/src/pages/RegisterPage.tsx`:
   - Form: username, password, email (optional) fields
   - Validates username and password required before submit
   - On submit: calls `useAuth().register()`
   - States: idle, loading, error (username taken, validation), success (redirect to `/studio`)
   - Link to `/login` for existing users
   - Layout matches the register mockup in `designs/mockup-pages/`
3. Stage and commit with a Conventional Commit message.
```

13.
```
**Input:** Build the History page — the list of all content items the author
has created, including the empty state.

**Context:**
- Read the history mockup in `designs/mockup-pages/` before building.
- Colors exclusively from `designs/COLOR_PALETTE.md`.
- The empty state is required by the functional requirements — not optional.
- Clicking an item navigates to `/studio?id={contentId}` to reopen it.

**Execution:**
Create `frontend/src/pages/HistoryPage.tsx`:
1. On mount: call `contentService.listMyContent()`
2. States:
   - loading: show `LoadingSpinner`
   - error: show `ErrorMessage` with retry option
   - empty: show `EmptyState` with message and a link/button to go create
     content in Studio (match the mockup)
   - success: show list of content items
3. Each content item renders:
   - Subject (always present)
   - Title (if generated; otherwise placeholder like "Not yet generated")
   - Synopsis preview (if generated; truncated to ~120 chars to fit the
     row layout)
   - Status badge (draft / generated)
   - Created date formatted readably
   - Click → navigate to `/studio?id={contentId}`
4. Layout matches the history mockup in `designs/mockup-pages/`.
5. Stage and commit with a Conventional Commit message.
```

14.
```
**Input:** Build the Studio page — the author's content creation workspace.
This is the most complex page in the MVP and handles both creating a new
item and viewing an existing one.

**Context:**
- Read the studio mockup in `designs/mockup-pages/` CAREFULLY before building.
- Colors exclusively from `designs/COLOR_PALETTE.md`.
- The Studio has two modes, determined by the `?id` query param:
  - New item mode (no `?id`): brief form
  - View mode (`?id=N`): load existing item, show its content
- Field-level loading matters: during generate, the user should still be
  able to read the brief while the content panel shows a loading state —
  do NOT block the whole page.

**Execution:**
Create `frontend/src/pages/StudioPage.tsx`:

1. **New item mode (no `?id`) — brief form:**
   - Fields: Subject, Genre, Audience, Runtime (all required)
   - Validates all fields before submit
   - On submit: calls `contentService.createContentItem()`
     - Loading: disable form, show loading state on button
     - Error: show `ErrorMessage`
     - Success: transition to view mode (update URL to `?id=N`)

2. **View mode (`?id=N`) — item loaded:**
   - Show brief fields (read-only): subject, genre, audience, runtime
   - Generated content panel with: title, synopsis, description, story
     (or placeholders if not yet generated). Field order matches
     `history-detail.html` mockup
   - Match the field emphasis from the mockups — synopsis renders as a
     distinct row (per `detail-regenerate.html`), not buried inside the
     description block
   - Generate button → `contentService.generateContent(contentId)`
     - Loading: field-level loading state in the content panel only
     - Error: `ErrorMessage` in the content panel
     - Success: update displayed content with generated fields

3. **On mount with `?id` present:** call `contentService.getContentItem(id)`
   - Loading: `LoadingSpinner` for the whole page
   - Error: `ErrorMessage` (item not found, not owned)
   - Success: populate the view

4. Layout matches the studio mockup in `designs/mockup-pages/`.

5. Stage and commit with a Conventional Commit message.
```

15.
```
**Input:** Build the Home page for unauthenticated visitors.

**Context:**
- Read the home mockup in `designs/mockup-pages/` before building.
- Colors exclusively from `designs/COLOR_PALETTE.md`.
- Authenticated users are redirected away from `/` to `/studio` in `App.tsx`,
  so this page only ever renders to guests.

**Execution:**
Create `frontend/src/pages/HomePage.tsx`:
1. Brief hero section: app name, one-line description of what ScriptSprout does
2. Two CTAs: "Get Started" → `/register`, "Sign In" → `/login`
3. Uses brand assets from `designs/brand/` where appropriate
4. Layout matches the home mockup in `designs/mockup-pages/`
5. Stage and commit with a Conventional Commit message.
```

16.
```
**Input:** Write the frontend unit test suite and confirm all tests pass
before committing.

**Context:**
- Tests must cover submit success, validation failure, and loading/error
  states — per the functional and technical requirements.
- Mock all service calls using Vitest mocks — do NOT make real network calls.
- Setup file at `frontend/src/tests/setup.ts` was created in prompt 6
  alongside `vite.config.ts`; it extends Vitest matchers via
  `@testing-library/jest-dom` and is already wired in.
- If any test fails, follow the `validate-and-fix` skill: root cause, re-run,
  repeat. Do not commit until clean.

**Execution:**
1. Create `frontend/src/tests/LoginPage.test.tsx`:
   - `test_login_form_renders`: form fields and submit button present
   - `test_login_validation`: submitting empty form shows validation errors, no API call made
   - `test_login_loading_state`: on submit, button shows loading state, form is disabled
   - `test_login_error_state`: when `authService.login` rejects, `ErrorMessage` is displayed
   - `test_login_success`: when `authService.login` resolves, user is redirected to `/studio`

2. Create `frontend/src/tests/RegisterPage.test.tsx`:
   - `test_register_form_renders`: username, password, email fields and submit button present
   - `test_register_validation`: submitting empty form (username/password required) shows validation errors, no API call made
   - `test_register_loading_state`: on submit, button shows loading state, form is disabled
   - `test_register_error_state`: when `authService.register` rejects (e.g., 409 username taken), `ErrorMessage` is displayed
   - `test_register_success`: when `authService.register` resolves, user is redirected to `/studio`

3. Create `frontend/src/tests/StudioPage.test.tsx`:
   - `test_brief_form_renders`: all four brief fields present
   - `test_brief_validation`: submitting empty form shows validation, no API call made
   - `test_create_content_loading`: on submit, shows loading state
   - `test_create_content_error`: when `createContentItem` rejects, `ErrorMessage` shown
   - `test_create_content_success`: when `createContentItem` resolves, transitions to view mode
   - `test_generate_loading`: in view mode, clicking generate shows field-level loading
   - `test_generate_error`: when `generateContent` rejects, `ErrorMessage` shown in content panel

4. Create `frontend/src/tests/HistoryPage.test.tsx`:
   - `test_history_loading`: shows `LoadingSpinner` while fetching
   - `test_history_empty_state`: when list is empty, `EmptyState` is displayed
   - `test_history_shows_items`: when items present, each renders with subject and status
   - `test_history_error`: when `listMyContent` rejects, `ErrorMessage` shown

5. Run `npm run test` from inside `frontend/` and show me the full output.
   Fix any failures before committing.

6. Stage and commit with a Conventional Commit message.
```

17.
```
**Input:** Run the `validate-and-fix` skill on the frontend before we push.

**Context:**
- Use `/test-frontend` for Vitest and `/lint-frontend` for ESLint.
- Follow the `validate-and-fix` skill exactly: root cause, loop until clean.

**Execution:**
1. Run `/test-frontend`.
2. Run `/lint-frontend`.
3. If anything fails, follow the `validate-and-fix` skill and loop.
4. When done, confirm:
   - Total tests: `X passed, 0 failed`
   - ESLint: 0 errors
   - All changes committed
```

18.
```
Before starting the frontend, the backend needs to be running again and
`OPENAI_API_KEY` must be set in the project-root `.env`.

1. Confirm `OPENAI_API_KEY` is set in `.env` — the manual flow includes
   generating content, which calls OpenAI and will fail without it.

2. The backend was stopped at the end of VIDEO_2.1 (prompt 17). In a separate
   terminal, start it again:
   `cd backend && uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`

3. Then start the frontend dev server: navigate to `frontend/` and run
   `npm run dev`. Confirm it starts on port 5173 with no errors.

4. I will manually walk through the full MVP flow in the browser
   (register → login → create brief → generate content → view in history → logout).

5. After I confirm everything works, stop the frontend server. The backend
   can stay running for the next phase.
```

19.
```
**Input:** Run the **`log-claude-build`** procedure in **`.claude/skills/log-claude-build.md`** for **`VIDEO_2.2`**.

**Context:**
- The skill was installed in **VIDEO_1**. Execute it yourself now—do not ask the learner to trigger the skill manually.
- Stay on **`feat/frontend-mvp`**. Ground summaries in **`git log` / `git diff`** for harness paths only (`CLAUDE.md`, `.claude/`, and harness-related root **`.env.example`** if it changed this phase).

**Execution:**
1. Follow the skill end-to-end with **`VIDEO_ID=VIDEO_2.2`**.
2. Stage and commit with: `docs: VIDEO_2.2 harness build notes`
```

20.
```
**Input:** Summarize the commits on this branch, push it to origin, and open
a PR against `main` using the `gh` CLI.

**Context:**
- Remote is `origin`, base is `main`.
- Use `gh` CLI (GitHub MCP arrives in Phase 3).
- Tests and lint are already clean from the previous prompt.

**Execution:**
1. Show me a summary of all commits on `feat/frontend-mvp` so I can review
   what we've built.
2. Push `feat/frontend-mvp` to `origin`.
3. Open a pull request using `gh pr create` with:
   - Base branch: `main`
   - Title: `feat: MVP frontend — React/TypeScript/Vite wired to backend`
   - Body (verbatim):

## What this PR contains

Complete React/TypeScript/Vite frontend for the ScriptSprout MVP — routing, auth
session management, API service modules, all MVP pages, and unit tests.

### Architecture
- `frontend/src/auth/AuthContext.tsx` — session state, hydration, login/logout
- `frontend/src/auth/ProtectedRoute.tsx` — route guard with loading state handling
- `frontend/src/services/` — api.ts (base client), authService.ts, contentService.ts
- `frontend/src/types/` — TypeScript interfaces matching backend schemas exactly
- `frontend/src/components/` — Layout, LoadingSpinner, ErrorMessage, EmptyState
- `frontend/src/pages/` — HomePage, LoginPage, RegisterPage, StudioPage, HistoryPage

### Pages and behavior
- Home: landing for guests, CTAs to register/login
- Login / Register: form validation, all four async states, redirects on success
- Studio: new item brief form + view mode with generate action, field-level loading
- History: content item list with empty state, loading, error states

### Design compliance
- Colors exclusively from designs/COLOR_PALETTE.md
- Layout matching designs/mockup-pages/ for each page
- Logo and brand assets from designs/brand/

### Quality
- All unit tests passing (submit success, validation failure, loading/error states)
- ESLint clean
- Vite proxy configured — no CORS issues in development
- Full stack smoke tested end-to-end

### Config additions
- CLAUDE.md updated for Phase 2.2
- .claude/commands/ — test-frontend, lint-frontend, run-frontend
```


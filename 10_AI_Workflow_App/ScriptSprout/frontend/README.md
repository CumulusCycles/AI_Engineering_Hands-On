# ScriptSprout frontend

Vite + React + TypeScript UI for ScriptSprout.

- **Dev:** from this directory, `npm install` then `npm run dev` (see course module [`README.md`](../../README.md) for running the API in parallel).
- **Proxy:** `vite.config.ts` proxies `GET /health` and `/api/*` to the FastAPI backend (default `http://127.0.0.1:8000`).
- **Auth + author studio shell:** routed SPA pages for `/`, `/login`, `/register`, `/verify-email`, `/studio`, `/profile`, `/admin-dashboard`, `/admin-nlp` with shared session state from `/api/auth/me`, auth flows (`/api/auth/login`, `/api/auth/register`, `/api/auth/logout`), NLP extraction integration (`POST /api/nlp/extract-story-parameters`), draft creation (`POST /api/content/`), draft actions over `/api/content/*` (generate/approve/regenerate synopsis/title/description), story/media actions (`generate-story`, `generate-thumbnail`, `generate-audio` + media GET previews), admin metrics dashboard reads (`GET /api/admin/metrics`), and admin natural-language queries (`POST /api/admin/nlp-query` — parse plan in the API, then metrics / semantic search in app code). Legacy author routes (`/workspace`, `/draft-review`, `/story-media`) redirect to `/studio`.
- **Brand:** CSS tokens match the **Brand Colors** table in the course module [`README.md`](../../README.md) (`src/index.css`, `src/App.css`).

## Testing

### Unit tests (Vitest + React Testing Library)

Shell wrapper (lint + unit tests):

```bash
./test.sh
```

Equivalent npm commands:

```bash
npm run lint
npm run test
```

Watch mode:

```bash
npm run test:watch
```

### E2E tests (Playwright)

Install Playwright browser binaries once per machine:

```bash
npx playwright install
```

(On Linux CI you may need `npx playwright install --with-deps` for system libraries.)

Run browser automation:

```bash
npm run test:e2e
```

The cross-stack E2E runner is **`ScriptSprout/test-scripts/test-e2e.sh`**. From **`ScriptSprout/`**:

```bash
./test-scripts/test-e2e.sh
```

Headed (visible browser), also from **`ScriptSprout/`**:

```bash
./test-scripts/test-e2e.sh headed
```

If your shell is already in **`ScriptSprout/frontend/`**, use `../test-scripts/test-e2e.sh` or `cd ..` then `./test-scripts/test-e2e.sh`.

`playwright.config.ts` starts the Vite dev server on `http://127.0.0.1:4173` and runs the `e2e/` suite.

The template’s default ESLint expansion notes were removed here; use the stock Vite + React docs if you want to tighten lint rules.

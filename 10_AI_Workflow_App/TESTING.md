# ScriptSprout — testing

Instructions for **module 10** ([`10_AI_Workflow_App/`](.)). The runnable app lives in **[`ScriptSprout/`](ScriptSprout/)**; run all commands below from **`ScriptSprout/`** unless noted.

## Prerequisites

- **uv** ([install](https://docs.astral.sh/uv/getting-started/installation/)) — Python **3.11+** and backend tooling
- **Node.js 20+** (or current LTS) and **npm**

## One-time setup (fresh clone)

1. Clone the repository and go to the app root:

   ```bash
   cd 10_AI_Workflow_App/ScriptSprout
   ```

2. **Environment (recommended for local dev):**

   ```bash
   cp .env.example .env
   ```

   Backend **pytest** uses isolated DB paths via fixtures; a missing `.env` does not block **`backend/test.sh`**. Newman **safe mode** clears OpenAI for speed unless you opt into live calls.

3. **Backend** — install dependencies (from `ScriptSprout/`):

   ```bash
   cd backend
   uv sync --group dev
   cd ..
   ```

   If **`ruff`** or **`pytest`** are missing after sync, try **`uv sync --all-groups`** (depends on your **uv** version).

4. **Frontend:**

   ```bash
   cd frontend
   npm install
   cd ..
   ```

5. **Playwright** (needed for E2E only):

   ```bash
   cd frontend
   npx playwright install
   cd ..
   ```

6. If shell scripts are not executable:

   ```bash
   chmod +x backend/test.sh frontend/test.sh test-scripts/*.sh startup.sh shutdown.sh reset-db-and-chroma.sh
   ```

   The glob covers **`test-cleanup.sh`** as well. **`test-cleanup.sh`** is **manual only** and is **not** invoked by **`verify.sh`**.

## What each script does

| Script | Purpose |
|--------|---------|
| [`ScriptSprout/backend/test.sh`](ScriptSprout/backend/test.sh) | **Backend only:** Ruff, then pytest (extra args go to pytest). |
| [`ScriptSprout/frontend/test.sh`](ScriptSprout/frontend/test.sh) | **Frontend only:** ESLint, then Vitest. |
| [`ScriptSprout/test-scripts/test.sh`](ScriptSprout/test-scripts/test.sh) | Runs **`backend/test.sh`**, then **`frontend/test.sh`**. |
| [`ScriptSprout/test-scripts/test-e2e.sh`](ScriptSprout/test-scripts/test-e2e.sh) | Playwright: **`npm run test:e2e`** in **`frontend/`**. Use **`headed`** / **`--headed`** as first arg for a visible browser. |
| [`ScriptSprout/test-scripts/test-postman.sh`](ScriptSprout/test-scripts/test-postman.sh) | Ephemeral API + Newman on the Postman collection. Default **safe mode** (no real OpenAI). **`POSTMAN_LIVE=1`** allows live OpenAI if **`OPENAI_API_KEY`** is set. **`POSTMAN_INCLUDE_ADMIN_SMOKE=1`** adds admin smoke folders. |
| [`ScriptSprout/test-scripts/verify.sh`](ScriptSprout/test-scripts/verify.sh) | Full local gate: **`test.sh`** → **`test-e2e.sh`** → **`test-postman.sh`** → **`POSTMAN_INCLUDE_ADMIN_SMOKE=1 test-postman.sh`**. |
| [`ScriptSprout/test-scripts/test-cleanup.sh`](ScriptSprout/test-scripts/test-cleanup.sh) | **Manual only:** remove test/build caches and outputs; keeps **`.venv`**, **`node_modules`**, **`frontend/.vite`**, **`data/`**, **`.env`**. |

**Not a test runner:** [`ScriptSprout/reset-db-and-chroma.sh`](ScriptSprout/reset-db-and-chroma.sh) wipes local SQLite + Chroma (dev helper).

## Run tests individually

From **`ScriptSprout/`**:

```bash
./backend/test.sh
./frontend/test.sh
./test-scripts/test-e2e.sh
./test-scripts/test-postman.sh
```

Examples:

```bash
./backend/test.sh -v
./test-scripts/test-e2e.sh headed
POSTMAN_INCLUDE_ADMIN_SMOKE=1 ./test-scripts/test-postman.sh
```

## Run the combined gate

From **`ScriptSprout/`**:

```bash
./test-scripts/test.sh          # unit + lint only (backend then frontend)
./test-scripts/verify.sh        # unit + lint + E2E + Newman (author + admin smoke)
```

## Clean up test artifacts (optional)

From **`ScriptSprout/`** (does **not** wipe **`data/`** or reinstall dependencies):

```bash
./test-scripts/test-cleanup.sh
```

## More detail

- Module overview: [`README.md`](README.md)
- Layout and automation row: [`ARCHITECTURE.md`](ARCHITECTURE.md)
- **`test-scripts/`** index: [`ScriptSprout/test-scripts/README.md`](ScriptSprout/test-scripts/README.md)
- Postman / Newman: [`ScriptSprout/backend/postman/README.md`](ScriptSprout/backend/postman/README.md)

Test artifacts (e.g. **`.pytest_cache/`**, **`node_modules/`**, **`data/`**, Playwright output) are listed in **[`ScriptSprout/.gitignore`](ScriptSprout/.gitignore)** and the repo root **`.gitignore`**; they should not be committed.

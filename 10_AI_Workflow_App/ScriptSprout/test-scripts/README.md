# ScriptSprout test automation (`test-scripts/`)

Cross-stack **test / verify / Postman** helpers live here only (no duplicate copies at **`ScriptSprout/`** root). Run them from **`ScriptSprout/`**, e.g. **`./test-scripts/test.sh`**.

**Dev helpers at `ScriptSprout/` root:** **`startup.sh`**, **`shutdown.sh`**, and **[`reset-db-and-chroma.sh`](../reset-db-and-chroma.sh)** (SQLite + Chroma wipe — not part of the test suite).

| Script | Purpose |
|--------|---------|
| [`test.sh`](test.sh) | Ruff + pytest (`backend/test.sh`), then ESLint + Vitest (`frontend/test.sh`). Pytest args pass through. |
| [`test-e2e.sh`](test-e2e.sh) | Playwright (`npm run test:e2e` in `frontend/`). Supports `headed` / extra Playwright CLI args. |
| [`test-postman.sh`](test-postman.sh) | Ephemeral API + Newman on `backend/postman/ScriptSprout.postman_collection.json`. See [`backend/postman/README.md`](../backend/postman/README.md). |
| [`verify.sh`](verify.sh) | `test.sh` → `test-e2e.sh` → `test-postman.sh` → admin Postman smoke. |
| [`test-cleanup.sh`](test-cleanup.sh) | **Manual only** (not chained elsewhere): delete test/build caches and outputs; keeps **`backend/.venv`**, **`frontend/node_modules`**, **`frontend/.vite`**, **`data/`**, **`.env`**. |

**Stack-local** gates stay in **`backend/test.sh`** and **`frontend/test.sh`**.

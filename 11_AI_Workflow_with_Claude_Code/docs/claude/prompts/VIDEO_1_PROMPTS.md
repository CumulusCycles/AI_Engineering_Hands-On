1.
```
**Role:** You are a senior full-stack engineer preparing to scaffold a greenfield
project. Your job right now is to deeply understand the specs before writing
a single file.

**Input:** Read and internalize the project's specification package, then give
me a concise summary so I can confirm you understand it correctly.

**Context:**
- This is the very first thing happening in the project — no application code
  exists yet, only specs and designs.
- A global `~/.claude/CLAUDE.md` with general engineering defaults is already
  loaded. Focus on what is specific to this project.
- Everything you build from here on must be derived from these specs — not
  invented or inferred from general patterns.

**Execution:**
1. Read these files in this exact order:
   - README.md
   - docs/README.md
   - docs/reqs/BUSINESS_REQS.md
   - docs/reqs/FUNCTIONAL_REQS.md
   - docs/reqs/TECHNICAL_REQS.md
   - designs/README.md
   - designs/COLOR_PALETTE.md
2. After reading, give me a concise summary covering:
   - What this application does
   - Who it's for
   - The tech stack
   - Any constraints or rules I should know about before we start building
3. Do not create any files yet.
```

2.
```
Before we create any files, let's establish proper Git workflow.

Please:
1. Check the current git status
2. Create and checkout a new feature branch called feat/claude-config
3. Confirm we are on the new branch
```

3.
```
**Input:** Create two files together — `.gitignore` and `.env.example` — and
commit them in a single commit.

**Context:**
- Stack: Python/FastAPI backend, React/TypeScript/Vite frontend, SQLite database.
- The local `.env` file already exists with real GitHub credentials — it must
  never be committed.
- `.env.example` is the committed template that shows contributors which
  variables they need, with placeholder values only.
- Environment variables are added to `.env.example` incrementally as each phase
  introduces new dependencies. Do NOT preemptively include database, OpenAI,
  Chroma, or media variables — those come in later phases.

**Execution:**
1. Create `.gitignore` covering Python, Node, SQLite, OS/IDE artifacts. Explicitly
   include entries for:
   - `.env` and `*.env` (secrets must never be committed)
   - `*.db` and `*.sqlite` (database files)
   - `CLAUDE.local.md` (Claude Code local overrides)
2. Create `.env.example` with two top comments:
   - `# Copy to .env and fill in values. Never commit .env.`
   - `# Variables are added to this file incrementally as each phase of the build introduces new dependencies.`
   And include ONLY these variables with placeholder values:
   ```
   # GitHub (required for git workflow and PR automation)
   GH_USERNAME=your_github_username
   GH_REPO=your_repo_name
   GH_PAT=your_fine_grained_pat_here
   ```
3. Stage both files and commit with a Conventional Commit message
   (e.g. `chore: add .gitignore and .env.example`).
```

4.
```
**Input:** Create `CLAUDE.md` at the project root based on the specs you just
read. It is the most important file in the project — it shapes every future
Claude Code session.

**Context:**
- A global `~/.claude/CLAUDE.md` already exists with general engineering defaults
  (working style, code quality, backend/frontend patterns, testing, communication).
  Do NOT repeat those defaults — add only what is specific to this project.
- This file is a **living artifact**. It will be updated at the start of each
  phase to reflect current scope, what's been built, and what comes next.
- Specific and actionable beats comprehensive. If a rule cannot be enforced or
  is not specific to ScriptSprout, leave it out.

**Execution:**
Create `CLAUDE.md` with these sections, in this order:

1. **Project overview** — what ScriptSprout is and who it's for (2-3 sentences max).
2. **Tech stack** — be explicit:
   - Backend: Python, FastAPI, SQLAlchemy 2.x, SQLite, Pydantic Settings
   - Frontend: React, TypeScript, Vite
   - AI provider: OpenAI SDK (NOT the Anthropic API — this project calls OpenAI
     for all generation, embeddings, images, and TTS)
   - Package managers: uv for Python, npm for Node
3. **Project layout** — `backend/` and `frontend/` as siblings in the repo root
   (these directories do not exist yet — they will be created during the build).
4. **Current phase** — Phase 1: Config scaffold. No application code yet.
5. **Initial build scope (Phase 2)** — what we ARE building next:
   auth, single-pass generation, history/detail, persistence, model-call logging.
6. **Out of scope for now** — what we are NOT building yet:
   regeneration, admin, embeddings, Chroma, thumbnails, audio.
7. **Hard rules specific to this project:**
   - Every OpenAI API call MUST be logged to the `model_call_log` table
   - Author data MUST never be visible to other authors — enforce at the dependency level
   - No stack traces in API error responses to the client
   - SQLite file path MUST be configurable via environment variable
   - Schema MUST bootstrap automatically on startup — no manual migration step

At the bottom of the file, add the line:
"This file is updated at the start of each phase to reflect current scope and context."

After creating the file, stage and commit with a Conventional Commit message.
```

5.
```
**Input:** Create the `.claude/` directory with two files — a `README.md`
documenting load order, and a `settings.json` with the project's Claude Code
permission mode.

**Context:**
- This folder is a living artifact. Commands, agents, and additional MCP
  servers are added in future phases — the README should preview them even
  though their folders don't exist yet.
- `acceptEdits` permission mode auto-accepts file edits but still prompts for
  bash commands — the right balance for a recording session.

**Execution:**
1. Create `.claude/README.md` as a brief index explaining the Claude Code load
   order and what lives in each subfolder:
   - Global `~/.claude/CLAUDE.md` loads first (personal engineering defaults)
   - Project `CLAUDE.md` loads next (ScriptSprout-specific context, updated each phase)
   - Scoped rules in `.claude/rules/` load when relevant files are touched
   - Skills in `.claude/skills/` are reusable procedural workflows Claude can invoke
   - Commands in `.claude/commands/` are available as slash commands (added in Phase 2)
   - Agents in `.claude/agents/` are autonomous task runners (added in Phase 3)
   - MCP servers in `.claude/mcp/` extend Claude's capabilities (Context7 active now,
     GitHub MCP added in Phase 3)
2. Create `.claude/settings.json` containing exactly:
   ```json
   {
     "permissionMode": "acceptEdits"
   }
   ```
3. Stage both files and commit with a Conventional Commit message.
```

6.
```
**Input:** Create two scoped rules files in `.claude/rules/` — one for FastAPI
conventions, one for database/migrations — derived directly from
`docs/reqs/TECHNICAL_REQS.md`. Keep each focused and under 50 lines.

**Context:**
- These rules govern every line of backend code Claude writes starting in
  Phase 2.1. They must read as engineering decisions for this project, not
  generic advice.
- All the rules below are derived from TECHNICAL_REQS.md. If any rule feels
  arbitrary, re-check that doc before writing.

**Execution:**
1. Create `.claude/rules/backend-fastapi.md` with these rules:
   - Route handlers must be thin — no business logic, only parse input, call service, return response
   - Business logic lives in service modules under `backend/app/services/`
   - All database access goes through repository modules — no queries in routes or services
   - Every request/response shape uses a Pydantic schema — no raw dicts across API boundaries
   - Pydantic v2 response schemas that wrap ORM rows MUST set
     `model_config = ConfigDict(from_attributes=True)` so FastAPI can
     serialize SQLAlchemy instances directly via `response_model=...`
   - Auth/session checking uses a single shared FastAPI dependency
   - Ownership enforcement (author can only access own content) uses a single shared dependency
     that returns 404 for wrong owner — never 200 with empty body
   - Admin-only routes use a separate admin guard dependency — never copy-pasted per route
   - Our auth `Session` model (`app/models/session.py`) collides with
     SQLAlchemy's `Session`. Project-wide convention: ALWAYS alias OUR model
     as `AuthSession` (`from app.models.session import Session as AuthSession`)
     and leave SQLAlchemy's `Session` un-aliased. Apply consistently in every
     file that touches both
   - Error responses follow a consistent JSON shape: `{"code": "...", "message": "..."}`.
     No stack traces, no internal details exposed to the client.
   - Every OpenAI API call must be logged to the `model_call_log` table before returning
2. Create `.claude/rules/database-and-migrations.md` with these rules:
   - SQLAlchemy 2.x declarative models — one model class per file under `backend/app/models/`
   - Schema must bootstrap automatically on app startup — no manual migration step for dev
   - No raw SQL strings anywhere in the codebase — use SQLAlchemy query API only
   - All model relationships declared explicitly with `relationship()` and foreign keys
   - SQLite for this project — database file path loaded from environment variable, never hardcoded
   - Session management via FastAPI dependency injection — never create sessions manually in routes
3. Stage both files and commit with a Conventional Commit message.
```

7.
```
**Input:** Create two more scoped rules files in `.claude/rules/` — one for
React/TypeScript conventions, one for general coding standards that apply
across the whole codebase.

**Context:**
- Frontend rules must reference real design asset paths in this project:
  `designs/COLOR_PALETTE.md`, `designs/mockup-pages/`, `designs/brand/`.
- The role model for route guards comes from `docs/reqs/FUNCTIONAL_REQS.md`.
- Coding standards apply to BOTH backend and frontend — keep them cross-cutting.

**Execution:**
1. Create `.claude/rules/frontend-react-vite-typescript.md` with these rules:
   - All API calls must live in dedicated client/service modules under
     `frontend/src/services/`. Never use `fetch()` or `axios` directly inside
     a component
   - TypeScript types/interfaces required for all API request and response shapes
   - Route guards must explicitly protect auth-required and admin-required routes
     consistent with the role model in `FUNCTIONAL_REQS.md`
   - Every async operation must handle all four states: loading, error, empty
     (where applicable), and success
   - Colors must come exclusively from `designs/COLOR_PALETTE.md` — no hardcoded
     hex values that are not in the palette
   - Layout and component structure must match the relevant mockup in
     `designs/mockup-pages/`
   - Logo and favicon must use assets from `designs/brand/`
2. Create `.claude/rules/coding-standards.md` with these rules:
   - Function names must be explicit and specific — avoid vague names like
     `handle`, `process`, `do`
   - No duplicated logic — extract a shared helper when the same pattern appears twice
   - Errors must be handled intentionally — no silent failures, no bare `except`
     or `catch` clauses
   - No secrets, tokens, or credentials in source code — environment variables only
   - Tests must cover changed behavior including at least one negative or edge case
   - Commit messages must use Conventional Commits format:
     `feat:` / `fix:` / `chore:` / `docs:` / `test:` / `refactor:`
3. Stage both files and commit with a Conventional Commit message.
```

8.
```
**Input:** Create a `validate-and-fix` skill at `.claude/skills/validate-and-fix.md`
that defines the build → test → fix → repeat loop Claude must follow whenever
asked to validate and fix a codebase.

**Context:**
- This skill is invoked by name in every subsequent phase of this project.
- The backend uses pytest; the frontend uses Vitest.
- The skill must apply to full-stack changes too, not just single-language work.

**Execution:**
1. Create `.claude/skills/validate-and-fix.md` defining the skill with these steps:
   1. Determine context — backend (pytest) or frontend (Vitest) based on what
      was changed, or both if the task spans the full stack
   2. Run the relevant test suite
   3. If all tests pass — report clean and stop
   4. If tests fail:
      - Analyze each failure carefully before touching any code
      - Fix the root cause — not just the symptom
      - Re-run the test suite
      - Repeat until all tests pass
   5. Report a concise summary of what was fixed and confirm the suite is clean
2. Include these hard rules within the skill:
   - Never skip a failing test — every failure must be resolved
   - Never modify a test to make it pass unless the test itself is provably wrong
   - Fix one logical problem at a time — do not batch unrelated changes
   - If a fix introduces a new failure, treat it as a new problem and loop again
   - When done, always confirm the final test count: `X passed, 0 failed`
3. Stage the file and commit with a Conventional Commit message.
```

9.
```
**Input:** Add the **`log-claude-build`** skill file only — do **not** run it yet.

**Context:**
- A later prompt will run this procedure for **`VIDEO_1`**, matching how other **`VIDEO_*`** modules install the skill once (here) then call it at the end of the phase.
- Create **`.claude/skills/log-claude-build.md`** by copying **`docs/claude/templates/log-claude-build.skill.md`** from the **first line after** the first `---` horizontal rule through end of file (exclude the template title and maintainer note above that rule).

**Execution:**
1. Create **`.claude/skills/log-claude-build.md`** from the template.
2. Update **`.claude/README.md`** so the skills list mentions both **`validate-and-fix`** and **`log-claude-build`** (how to invoke / what each is for — one line each).
3. Stage and commit with: `feat: add log-claude-build skill`
```

10.
```
**Input:** Configure the Context7 MCP server for this project and register it
in the `.claude/` folder.

**Context:**
- Context7 provides up-to-date library documentation at query time, so when
  Claude writes code against FastAPI, SQLAlchemy 2.x, Pydantic, React,
  TypeScript, or Vite in Phase 2, it works from current docs — not potentially
  stale training data.
- Context7 is the only MCP server needed in this phase. GitHub MCP comes later
  in Phase 3.
- If you are unsure of the exact JSON shape for the Context7 server
  configuration, consult Context7's official documentation before writing
  the file.

**Execution:**
1. Create `.claude/mcp/context7.json` with the correct Context7 server
   configuration.
2. If `.claude/README.md` needs to be updated to reflect that Context7 is now
   active, update it.
3. Stage all changes and commit with a Conventional Commit message.
```

11.
```
**Input:** Run the **`log-claude-build`** procedure in **`.claude/skills/log-claude-build.md`** for **`VIDEO_1`**.

**Context:**
- The skill file was created in **prompt 9**; **Context7** was added in **prompt 10** — this run must reflect the **full** Phase 1 harness through **prompt 10**.
- Execute it yourself—do not ask the learner to trigger the skill manually.
- Stay on **`feat/claude-config`**. Use **`git log`** / **`git diff`** for harness paths only (`CLAUDE.md`, `.claude/`, harness-related root **`.gitignore`** / **`.env.example`**). Do **not** describe future **`backend/`** or **`frontend/`** work.

**Execution:**
1. Follow the skill end-to-end with **`VIDEO_ID=VIDEO_1`** (write **`docs/claude/build-notes/VIDEO_1.md`**, update **`docs/claude/CLAUDE_CODE_BUILD_LOG.md`**).
2. Stage and commit with: `docs: VIDEO_1 harness build notes`
```

12.
```
**Input:** Push the branch, summarize the commits, and open a PR against `main`.

**Context:**
- Remote is `origin`. Base branch is `main`.
- Use the `gh` CLI for the push and PR creation — this project has not yet
  configured the GitHub MCP server (that comes in Phase 3).

**Execution:**
1. Push the `feat/claude-config` branch to `origin`.
2. Show me a summary of all commits on this branch so I can review what was built.
3. Open a pull request using `gh pr create` with:
   - Base branch: `main`
   - Title: `feat: scaffold Claude Code configuration`
   - Body (verbatim):

## What this PR contains

Initial Claude Code configuration scaffold for the ScriptSprout project,
derived from the project requirements and design specifications.

### Files added
- `.gitignore` — Python, Node, SQLite, env file exclusions
- `.env.example` — GH credentials template (populated incrementally each phase)
- `CLAUDE.md` — project context, stack, current phase, hard rules (living artifact)
- `.claude/README.md` — configuration load order and folder structure reference
- `.claude/settings.json` — acceptEdits permission mode
- `.claude/rules/backend-fastapi.md` — FastAPI layering, ownership rules, error shape
- `.claude/rules/database-and-migrations.md` — SQLAlchemy models, SQLite, schema bootstrap
- `.claude/rules/frontend-react-vite-typescript.md` — React/TS conventions, design alignment
- `.claude/rules/coding-standards.md` — code quality, naming, error handling, commit format
- `.claude/skills/validate-and-fix.md` — reusable build→test→fix→repeat loop skill
- `.claude/skills/log-claude-build.md` — per-video Claude Code learning log (harness only)
- `.claude/mcp/context7.json` — Context7 MCP server for live library documentation
- `docs/claude/build-notes/VIDEO_1.md` — VIDEO_1 harness learning notes
- `docs/claude/CLAUDE_CODE_BUILD_LOG.md` — cumulative harness log (VIDEO_1 section added or updated)

### Why configuration before application code
Grounding Claude in the project architecture, constraints, and conventions before
writing application code ensures every session starts with the right context.
CLAUDE.md and .claude/ are intentionally minimal here — both grow with each phase.
```


# `docs/claude/prompts/` — hands-on prompt modules

This folder holds **numbered `VIDEO_*_PROMPTS.md` files**: the exact multi-step prompts you paste into **Claude Code** (or another agent) to build ScriptSprout **in a working tree** on your machine.

- These files are **instructions for the agent**, not product requirements. Product truth stays under [`docs/reqs/`](../../reqs/) and [`designs/`](../../../designs/).
- Run the modules in **lexicographic filename order** (`VIDEO_1` → `VIDEO_2.1` → `VIDEO_2.2` → `VIDEO_3` → `VIDEO_4.1a` → `VIDEO_4.1b` → `VIDEO_4.2`). Do not skip modules unless you intentionally change the curriculum.
- Higher-level context: chapter [`README.md`](../../../README.md), map [`docs/README.md`](../../README.md), Claude teaching notes [`docs/claude/README.md`](../README.md).

---

## Human developer setup (before you open a prompt file)

Do **all** of the following **yourself** before you paste **VIDEO_1** prompt **1** into Claude Code. The shipped prompts **assume** this groundwork exists; most of it is **not** spelled out inside each `VIDEO_*` file.

### 1. Accounts and access

1. **GitHub** — Account and permission to create (or use) a repository where this project will live.
2. **Anthropic / Claude Code** — Install and sign in per current Claude Code documentation for your OS (see chapter [`README.md`](../../../README.md) prerequisites).
3. **OpenAI** — Create an account and an API key **before** you need live generation (backend phase and later). You do **not** need the key on day one for **VIDEO_1** prompt **1**, but you will need it in `.env` before exercising generation in **VIDEO_2.1** and beyond. Never commit keys.

### 2. Runtime tooling (matches the technical spec)

Install tooling consistent with [`docs/reqs/TECHNICAL_REQS.md`](../../reqs/TECHNICAL_REQS.md) §2 (stack), including at minimum:

- **Git**
- **Python 3.11+** and **`uv`** (used in prompts for the backend)
- **Node.js** and **`npm`** (used for the Vite/React frontend in later modules)
- **`gh` CLI** (GitHub CLI) — **required** for **VIDEO_1** through **VIDEO_2.x** prompts that use `gh pr create` / push flows against `origin`. Authenticate with `gh auth login` and confirm `gh auth status`.

Later modules use **GitHub MCP** instead of `gh` for some operations; the CLI remains useful as a fallback.

### 3. Git repository on your machine

Choose **one** path that matches how you obtained this starter pack:

**A. You already have this folder as a Git clone** (e.g. from GitHub)

- `cd` into the repo root.
- Confirm `git remote -v` shows **`origin`** pointing at **your** GitHub repo (or a fork you control).
- Ensure you are on the default branch you will use as **`main`** (or rename to match what the prompts expect: **`main`** as base in PR prompts).

**B. You have an unzipped / copied folder with no remote (or no Git yet)**

1. `cd` into the project root (the directory that contains `README.md`, `docs/`, `designs/`).
2. `git init` (if there is no `.git` yet).
3. Create an **empty** repository on GitHub (no README/license added by GitHub, **or** be ready to merge/reconcile if you did add files).
4. Stage everything that should be versioned: `git add` for `README.md`, `docs/`, `designs/`, and any other shipped files. **Do not** add `.env` or editor junk (a root `.gitignore` will be created by **VIDEO_1** prompt **3** — until then, avoid `git add .` blindly if secrets exist).
5. `git commit -m "chore: initial spec and design import"` (or similar).
6. `git branch -M main` if your default branch should be **`main`**.
7. `git remote add origin https://github.com/<OWNER>/<REPO>.git` (or SSH equivalent).
8. **`git push -u origin main`** so **`origin/main`** exists. Later prompts assume a remote named **`origin`** and base branch **`main`**.

### 4. GitHub credentials (local only)

1. On GitHub, create a **fine-grained Personal Access Token** (or a classic PAT if you standardize on that) with the repository permissions **`gh`** and/or **GitHub MCP** need:

   - **Contents** — Read and write (push commits, create/read files and branches)
   - **Pull requests** — Read and write (create PRs, post review comments, merge)
   - **Metadata** — Read-only (mandatory for all fine-grained PATs; GitHub adds this automatically)
   - **Workflows** — Read and write (only if the prompt series modifies `.github/workflows/` files; skip if not using GitHub Actions)
2. In the **project root**, create a file named **`.env`** (this file is **never** committed). Add placeholders first, then real values:

   ```bash
   GH_USERNAME=<your_github_username_or_org>
   GH_REPO=<repository_name>
   GH_PAT=<your_pat>
   ```

   **VIDEO_1** prompt **3** will add a committed **`.env.example`** template; your real **`.env`** is **your** responsibility **before** prompt **3** runs, because that prompt’s context assumes GitHub credentials already exist locally for later `gh` steps.

3. Keep **`.env` out of git**. After **VIDEO_1** prompt **3**, `.gitignore` will ignore `.env` — until then, **do not** `git add .env`.

### 5. Read the specs (human understanding)

Before **VIDEO_1** prompt **1**, read and internalize the same stack the first prompt tells the agent to read (see [`docs/README.md`](../../README.md) reading order):

1. [`README.md`](../../../README.md) (chapter overview)
2. [`docs/README.md`](../../README.md)
3. [`docs/reqs/BUSINESS_REQS.md`](../../reqs/BUSINESS_REQS.md)
4. [`docs/reqs/FUNCTIONAL_REQS.md`](../../reqs/FUNCTIONAL_REQS.md)
5. [`docs/reqs/TECHNICAL_REQS.md`](../../reqs/TECHNICAL_REQS.md)
6. [`designs/README.md`](../../../designs/README.md)
7. [`designs/COLOR_PALETTE.md`](../../../designs/COLOR_PALETTE.md)

[`docs/README.md`](../../README.md) states that the prompts assume you have already absorbed the **master `reqs/`** reading before **VIDEO_1**.

### 6. Open the project in Claude Code

1. Open the **repository root** in your editor / Claude Code so the agent’s cwd is the folder that contains `README.md`, `docs/`, and `designs/`.
2. Confirm `git status` is clean (or only intentional WIP) and `git branch` shows you are ready to create **`feat/claude-config`** when **VIDEO_1** prompt **2** runs.

### 7. Only then: open the prompt files

Start with **[`VIDEO_1_PROMPTS.md`](VIDEO_1_PROMPTS.md)** and run prompts **in numerical order** inside that file (1, 2, 3, …). After **VIDEO_1** is complete, move to **`VIDEO_2.1`**, then **`VIDEO_2.2`**, and so on.

---

## Files in this folder

| File | Role in the curriculum |
|------|-------------------------|
| [`VIDEO_1_PROMPTS.md`](VIDEO_1_PROMPTS.md) | **Phase 1 — Project harness.** Read specs; Git branch `feat/claude-config`; `.gitignore` + `.env.example`; root `CLAUDE.md`; `.claude/` (`README`, `settings.json`, rules, skills including `validate-and-fix` and `log-claude-build`, Context7 MCP); harness build notes; push + PR with **`gh`**. No application `backend/` / `frontend/` yet. |
| [`VIDEO_2.1_PROMPTS.md`](VIDEO_2.1_PROMPTS.md) | **Phase 2.1 — MVP backend.** Update `CLAUDE.md` for backend phase; read MVP reqs; branch `feat/backend-mvp`; slash commands; `uv` project; FastAPI layered app (models, repos, services, routes, auth, content, OpenAI single-pass generation, tests, Postman); validate-and-fix; `log-claude-build` for **VIDEO_2.1**; PR with **`gh`**. |
| [`VIDEO_2.2_PROMPTS.md`](VIDEO_2.2_PROMPTS.md) | **Phase 2.2 — MVP frontend.** Update `CLAUDE.md` for frontend; read MVP functional + designs; branch `feat/frontend-mvp`; Vite React/TS app; proxy, types, API services, auth context, protected routes, pages (Home, Login, Register, Studio, History), Vitest tests; manual full-stack smoke; `log-claude-build` for **VIDEO_2.2**; PR with **`gh`**. |
| [`VIDEO_3_PROMPTS.md`](VIDEO_3_PROMPTS.md) | **Phase 3 — GitHub automation in Claude Code.** `CLAUDE.md` for Phase 3; branch `feat/extending-claude-code`; **GitHub MCP** config (`.claude/mcp/github.json`); `.env.example` note for dual OpenAI consumers; **`pr-reviewer`** agent; `log-claude-build`; push/PR/review/merge via **GitHub MCP** (not `gh` for those steps). |
| [`VIDEO_4.1a_PROMPTS.md`](VIDEO_4.1a_PROMPTS.md) | **Phase 4.1a — Author-facing backend enhancements.** E1 regeneration, E3 thumbnail, E4 audio; config and models; services and routes; tests; Postman update; validate-and-fix; `log-claude-build`; push/PR + **`pr-reviewer`** via GitHub MCP. |
| [`VIDEO_4.1b_PROMPTS.md`](VIDEO_4.1b_PROMPTS.md) | **Phase 4.1b — Admin backend.** E2 Chroma/embeddings + E5 admin dashboard; `admin-and-search` rules; Chroma + admin bootstrap in startup; embedding index; admin service/routes; tests; Postman; validate-and-fix; `log-claude-build`; push/PR + **`pr-reviewer`**. |
| [`VIDEO_4.2_PROMPTS.md`](VIDEO_4.2_PROMPTS.md) | **Phase 4.2 — Enhancements frontend (final).** Wire E1–E5 in React: Studio regen/thumbnail/audio, History thumbnails, admin pages + `AdminRoute`, types/services/tests; validate-and-fix; smoke test; `log-claude-build`; push/PR + **`pr-reviewer`**. |

---

## Directory listing (prompt modules)

Lexicographic run order:

```
docs/claude/prompts/
├── README.md                 ← this file
├── VIDEO_1_PROMPTS.md        ← start here
├── VIDEO_2.1_PROMPTS.md
├── VIDEO_2.2_PROMPTS.md
├── VIDEO_3_PROMPTS.md
├── VIDEO_4.1a_PROMPTS.md
├── VIDEO_4.1b_PROMPTS.md
└── VIDEO_4.2_PROMPTS.md
```

---

## Cross-links

- Chapter overview (repo root): [`../../../README.md`](../../../README.md)
- Map of all `docs/`: [`../../README.md`](../../README.md)
- Parent Claude docs: [`../README.md`](../README.md)
- Build notes (who runs `log-claude-build`): [`../build-notes/README.md`](../build-notes/README.md)
- Logger skill template: [`../templates/log-claude-build.skill.md`](../templates/log-claude-build.skill.md)

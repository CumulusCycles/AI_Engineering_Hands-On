# Claude documentation

This folder is for **people** reading the repo: **reference** material and **numbered prompts** (`VIDEO_*`) that you paste into **Claude Code** when you build ScriptSprout in a working tree. It is **not** the generated project harness—root **`CLAUDE.md`**, **`.claude/`**, **`backend/`**, and **`frontend/`** appear **after** you run those prompts (see the chapter **`README.md`** one level up).

---

## Claude Code features used in this chapter

These are the Claude Code capabilities the prompt series actually sets up or relies on:

| Feature | What it does here |
|---------|---------------------|
| **Project `CLAUDE.md`** (repo root, generated) | ScriptSprout-specific stack, phase, scope, and hard rules; updated each phase so sessions stay aligned. |
| **Global `~/.claude/CLAUDE.md`** (your machine, assumed) | Personal defaults that load before the project file; prompts tell Claude not to duplicate them in repo `CLAUDE.md`. |
| **`.claude/README.md`** (generated) | Load order and what lives under **`.claude/`** (rules, skills, commands, agents, MCP). |
| **`.claude/settings.json`** (generated) | **`permissionMode`: `acceptEdits`** so file edits auto-apply while shell commands still prompt. |
| **`.claude/rules/*.md`** (generated) | Scoped guardrails (FastAPI layering, DB/SQLAlchemy, React/services/mockups, coding style; later admin/semantic rules). |
| **`.claude/skills/validate-and-fix.md`** (generated) | Packaged **run tests → fix → repeat** loop for backend and/or frontend. |
| **`.claude/skills/log-claude-build.md`** (generated, **VIDEO_1** prompt **9**) | **VIDEO_1** prompt **11** runs it the first time (after Context7); each other **`VIDEO_*`** file embeds a run **before that module’s push/PR** (not always the last numbered prompt—e.g. **VIDEO_3** before the first MCP push). Writes **[`build-notes/VIDEO_*.md`](build-notes/README.md)** and updates **[`CLAUDE_CODE_BUILD_LOG.md`](CLAUDE_CODE_BUILD_LOG.md)**. |
| **`.claude/commands/*.md`** (generated) | Slash commands for **`uv run pytest`**, **`ruff`**, **`uvicorn`**, **`npm test`**, **`npm run lint`**, **`npm run dev`**. |
| **`.claude/mcp/context7.json`** (generated) | **Context7 MCP** — live library docs for stack dependencies while coding. |
| **`.claude/mcp/github.json`** (generated) | **GitHub MCP** — branches, PRs, diffs, comments, merge using env-based credentials (no secrets in git). |
| **`.claude/agents/pr-reviewer.md`** (generated) | **`pr-reviewer` agent** — fetch PR diff via GitHub MCP, send to OpenAI for review, post a PR review comment. |

Hooks, plugins, plan mode, and headless/scheduled runs are **out of scope** for this prompt track.

---

## Learning logs (Claude Code–focused)

Prompts **run** **`log-claude-build` for you** (install from **[`templates/log-claude-build.skill.md`](templates/log-claude-build.skill.md)** in **VIDEO_1** prompt **9**, first execution in **prompt 11**). Learners do not copy the template by hand or invoke the skill manually. **Automated vs manual** for this slice (only): see **[`build-notes/README.md` § Who does what](build-notes/README.md#who-does-what-pedagogy-logging-only)**.

- **[`build-notes/README.md`](build-notes/README.md)** — per-video notes (`VIDEO_1.md`, …) + pointer to the cumulative log.
- **[`CLAUDE_CODE_BUILD_LOG.md`](CLAUDE_CODE_BUILD_LOG.md)** — cumulative summary across videos (one **`## VIDEO_*`** block per module; same-id re-runs **replace** that block per the skill).
- **[`templates/log-claude-build.skill.md`](templates/log-claude-build.skill.md)** — source template for **`.claude/skills/log-claude-build.md`**.

**Why a template file instead of defining this skill only inside a prompt?** Most harness pieces here (e.g. **`validate-and-fix`**, rules, commands, **`pr-reviewer`**) are **authored inline** in **`VIDEO_*`** prompts so learners see the full text in one place. **`log-claude-build`** is **longer** (git grounding, two output paths, cumulative-log replace rules) and is **revised across chapter releases**, so it lives as a **single maintainable source** under **`templates/`**; **VIDEO_1** prompt **9** tells Claude to copy it into **`.claude/skills/`**. That is a **curriculum convenience**, not a Claude Code requirement—you could inline the same skill body in **`VIDEO_1_PROMPTS.md`** if you preferred one style everywhere.

## Reference in this folder

- **[`GLOBAL.CLAUDE.md`](GLOBAL.CLAUDE.md)** — global-style Claude guidance (reference copy; not the same as your generated project-root `CLAUDE.md`).

---

## `prompts/`

Numbered prompt files—**one file per video module**—in the order you run them in Claude Code:

- [prompts/VIDEO_1_PROMPTS.md](prompts/VIDEO_1_PROMPTS.md)
- [prompts/VIDEO_2.1_PROMPTS.md](prompts/VIDEO_2.1_PROMPTS.md)
- [prompts/VIDEO_2.2_PROMPTS.md](prompts/VIDEO_2.2_PROMPTS.md)
- [prompts/VIDEO_3_PROMPTS.md](prompts/VIDEO_3_PROMPTS.md)
- [prompts/VIDEO_4.1a_PROMPTS.md](prompts/VIDEO_4.1a_PROMPTS.md)
- [prompts/VIDEO_4.1b_PROMPTS.md](prompts/VIDEO_4.1b_PROMPTS.md)
- [prompts/VIDEO_4.2_PROMPTS.md](prompts/VIDEO_4.2_PROMPTS.md)

Run **`VIDEO_1`** through **`VIDEO_4.2`** in **lexicographic** filename order.

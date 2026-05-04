# Greenfield build with Claude Code

This folder is a **self-contained starting point** for implementing a full-stack web application **from prompts**, using **Claude Code** alongside the specifications and UI artifacts checked in here.

This repository intentionally ships **no application source code** and **no project-root `CLAUDE.md` or `.claude/` tree**—those are created in your working tree when you follow the prompt series. It *does* ship **reference** material under **`docs/claude/`** (global guidance, README, and the numbered `VIDEO_*` prompts). This is a specification-first workspace used to teach phased application development with Claude Code.

**What exists today:**
- **`docs/`** — map in [`docs/README.md`](docs/README.md); master requirements and milestone slices under **`docs/reqs/`** (including **`docs/reqs/mvp/`** and **`docs/reqs/enhancements/`**); Claude-oriented material under **`docs/claude/`** (**[`docs/claude/prompts/README.md`](docs/claude/prompts/README.md)** for **human setup before any prompts**, then **`VIDEO_*`** files under **`docs/claude/prompts/`**, **[`GLOBAL.CLAUDE.md`](docs/claude/GLOBAL.CLAUDE.md)**, **[`build-notes/`](docs/claude/build-notes/)**, **[`templates/`](docs/claude/templates/)** including **`log-claude-build.skill.md`**, **[`CLAUDE_CODE_BUILD_LOG.md`](docs/claude/CLAUDE_CODE_BUILD_LOG.md)** stub); optional long-form HTML under **`docs/supplementary/`**
- **`designs/`** — visual source of truth (mockups, palette, brand assets)
- **Application source code is not part of this package** — you generate it in a working tree with Claude Code, guided by those documents and prompts

There is **no** assumed prior codebase, sibling project, or external chapter to reconcile with. Treat everything under this directory as the **sole** specification set for the build.

---

## Goals

- **Phased delivery (aligned with [`docs/claude/prompts/`](docs/claude/prompts/)):** complete **[human developer setup](docs/claude/prompts/README.md#human-developer-setup-before-you-open-a-prompt-file)** in **[`docs/claude/prompts/README.md`](docs/claude/prompts/README.md)** *before* opening **`VIDEO_*`** files; then follow the **numbered** prompt files in order—**[`VIDEO_1_PROMPTS.md`](docs/claude/prompts/VIDEO_1_PROMPTS.md)** through **`VIDEO_4.2`** (see **[`prompts/README.md`](docs/claude/prompts/README.md)** for a directory listing and module summaries). Each phase mixes specs, designs, and prompts differently so scope stays explicit.
  - **1 — Claude project harness** ([`VIDEO_1_PROMPTS.md`](docs/claude/prompts/VIDEO_1_PROMPTS.md)): read **`docs/reqs/`** and **`designs/`**, then add **`CLAUDE.md`**, **`.claude/`** (rules; **`validate-and-fix`** from prompts; **`log-claude-build`** from **[`docs/claude/templates/`](docs/claude/templates/)**; Context7 MCP; settings), baseline git/env files, and the first [**harness learning logs**](docs/claude/build-notes/README.md)—**no application source yet**.
  - **2 — MVP application** ([`VIDEO_2.1_PROMPTS.md`](docs/claude/prompts/VIDEO_2.1_PROMPTS.md) backend, then [`VIDEO_2.2_PROMPTS.md`](docs/claude/prompts/VIDEO_2.2_PROMPTS.md) frontend): FastAPI + React MVP—author auth, single-pass generation, history/detail, persistence, model-call logging. Scoped by **`docs/reqs/mvp/`** on top of the master **`docs/reqs/`** and **`designs/`**; this phase adds slash **commands** under **`.claude/commands/`** for test/lint/run loops.
  - **3 — GitHub workflow in Claude Code** ([`VIDEO_3_PROMPTS.md`](docs/claude/prompts/VIDEO_3_PROMPTS.md)): **GitHub MCP**, the **`pr-reviewer`** agent, and PR automation—**engineering workflow**, not the E1–E5 enhancement tracks. Still driven only from the prompt series (not from **`docs/reqs/enhancements/`**).
  - **4 — Product enhancements** ([`VIDEO_4.1a_PROMPTS.md`](docs/claude/prompts/VIDEO_4.1a_PROMPTS.md), [`VIDEO_4.1b_PROMPTS.md`](docs/claude/prompts/VIDEO_4.1b_PROMPTS.md), [`VIDEO_4.2_PROMPTS.md`](docs/claude/prompts/VIDEO_4.2_PROMPTS.md)): E1–E5 (regeneration, admin NLP/semantic, thumbnails, audio, admin dashboard). Scoped by **`docs/reqs/enhancements/`** plus **`designs/`**; **4.1b** adds **`.claude/rules/admin-and-search.md`** for admin/semantic boundaries.
- **Honor two contracts:** when a mockup and **`docs/reqs/`** disagree, follow [`designs/README.md`](designs/README.md): **[`FUNCTIONAL_REQS.md`](docs/reqs/FUNCTIONAL_REQS.md)** wins on **security and data rules**; **`designs/`** wins on **pure layout/visuals**.
  - **`docs/`** — behavior, security, data rules, and architecture
  - **`designs/`** — layout, states, colors, and branding
- **Use Claude Code deliberately:** small, verifiable steps; explicit file context in prompts; frequent test and lint runs; commits at natural boundaries—aligned with how teams ship **modern** web apps, not a single mega-prompt.

---

## What to read first

| Order | Path | Role |
|------:|------|------|
| 0 | [`docs/README.md`](docs/README.md) | Map of `docs/` and reading order |
| 1 | [`docs/reqs/BUSINESS_REQS.md`](docs/reqs/BUSINESS_REQS.md) | Vision, personas, scope, business rules |
| 2 | [`docs/reqs/FUNCTIONAL_REQS.md`](docs/reqs/FUNCTIONAL_REQS.md) | Observable behavior, roles, journeys, acceptance-oriented requirements |
| 3 | [`docs/reqs/TECHNICAL_REQS.md`](docs/reqs/TECHNICAL_REQS.md) | Stack, layering, auth, APIs, data concepts, AI, testing, deployment |
| 4 | [`designs/README.md`](designs/README.md) | How to use mockups, palette, and brand assets |

**Milestone slices (do not skip the master trio above):**

| Milestone | Business | Functional | Technical |
|-----------|----------|------------|-----------|
| **MVP** | [`docs/reqs/mvp/MVP_BUSINESS_REQS.md`](docs/reqs/mvp/MVP_BUSINESS_REQS.md) | [`docs/reqs/mvp/MVP_FUNCTIONAL_REQS.md`](docs/reqs/mvp/MVP_FUNCTIONAL_REQS.md) | [`docs/reqs/mvp/MVP_TECH_REQS.md`](docs/reqs/mvp/MVP_TECH_REQS.md) |
| **Enhancements** | [`docs/reqs/enhancements/ENHANCEMENTS_BUSINESS_REQS.md`](docs/reqs/enhancements/ENHANCEMENTS_BUSINESS_REQS.md) | [`docs/reqs/enhancements/ENHANCEMENTS_FUNCTIONAL_REQS.md`](docs/reqs/enhancements/ENHANCEMENTS_FUNCTIONAL_REQS.md) | [`docs/reqs/enhancements/ENHANCEMENTS_TECH_REQS.md`](docs/reqs/enhancements/ENHANCEMENTS_TECH_REQS.md) |

The MVP and enhancement files **point into** the master documents; they do not replace them. If anything disagrees, **the master `docs/reqs/*_REQS.md` files win**.

---

## Suggested workflow with Claude Code

1. **Bootstrap context** — Ground every session in [`docs/README.md`](docs/README.md), the master trio under [`docs/reqs/`](docs/reqs/), and [`designs/README.md`](designs/README.md). Prefer **attaching or referencing specific paths** over vague “build the app” prompts. For the **guided video path**, read **[`docs/claude/prompts/README.md`](docs/claude/prompts/README.md)** first (human setup, then what each **`VIDEO_*`** file covers); drive work from [`docs/claude/prompts/`](docs/claude/prompts/) in **lexicographic file order** (`VIDEO_1` → `VIDEO_2.1` → `VIDEO_2.2` → `VIDEO_3` → `VIDEO_4.1a` → `VIDEO_4.1b` → `VIDEO_4.2`).
2. **Respect phase boundaries** — **Project harness** (root `CLAUDE.md` + `.claude/`, [`VIDEO_1_PROMPTS.md`](docs/claude/prompts/VIDEO_1_PROMPTS.md)) before **application** code; **MVP** ([`docs/reqs/mvp/`](docs/reqs/mvp/) + [`VIDEO_2.1`](docs/claude/prompts/VIDEO_2.1_PROMPTS.md) / [`VIDEO_2.2`](docs/claude/prompts/VIDEO_2.2_PROMPTS.md)) before **GitHub automation** ([`VIDEO_3_PROMPTS.md`](docs/claude/prompts/VIDEO_3_PROMPTS.md)); only then **enhancements** ([`docs/reqs/enhancements/`](docs/reqs/enhancements/) + `VIDEO_4.x`). The master **`docs/reqs/*_REQS.md`** files stay authoritative throughout (same rule as **What to read first** / milestone table above).
3. **One capability at a time** — e.g. session + ownership guards before new surfaces; generation happy path before polish. After each step: **run tests/lint** (thresholds are in [`docs/reqs/TECHNICAL_REQS.md`](docs/reqs/TECHNICAL_REQS.md) §14 and the MVP/enhancement tech slices).
4. **UI work** — Open relevant files under [`designs/mockup-pages/`](designs/mockup-pages/) in a browser; mirror structure and states; follow [`designs/COLOR_PALETTE.md`](designs/COLOR_PALETTE.md) and [`designs/brand/`](designs/brand/) for visuals.
5. **Secrets and config** — Never commit API keys or real `.env` values. The technical requirements describe **categories** of configuration; the prompt series starts a root **`.env.example`** in [`VIDEO_1_PROMPTS.md`](docs/claude/prompts/VIDEO_1_PROMPTS.md) and extends it phase by phase—keep that pattern.
6. **Teach / record clearly** — When producing a walkthrough, narrate **which doc** justified each prompt and how you **verified** the result (tests, manual check against a mockup, or both).
7. **Harness learning logs** — Each **`VIDEO_*`** prompt file embeds a **`log-claude-build`** step before push/PR (after **VIDEO_1** prompt **9** installs the skill and **11** runs it the first time). You do **not** copy the template or invoke the skill yourself; outputs live under **`docs/claude/build-notes/`** and **`docs/claude/CLAUDE_CODE_BUILD_LOG.md`** (see **[`docs/claude/build-notes/README.md`](docs/claude/build-notes/README.md)**).

---

## Prerequisites (typical)

Details live in [`docs/reqs/TECHNICAL_REQS.md`](docs/reqs/TECHNICAL_REQS.md) (stack §2). At a high level you will need:

- **Claude Code**, with **sign-in / plan access as Claude Code requires**—typically an **Anthropic** account; follow current Claude Code product documentation for your environment.
- **Runtime tooling** consistent with the technical spec (e.g. Python and Node ecosystems as specified there)
- **OpenAI API key** — for **chat** generation in the baseline stack; enhancement milestones add **embedding** calls (admin semantic / vector index), plus **image** and **TTS** APIs where implemented—all as the same OpenAI integration described in the technical and enhancement requirements. If you follow [`docs/claude/prompts/`](docs/claude/prompts/), **Phase 3** also uses OpenAI for the **`pr-reviewer`** agent (diff-based PR review). Never commit keys; use environment variables only.
- **GitHub account + PAT** — full human-side checklist (repo on GitHub, local **`git push`**, **`.env`**, **`gh auth login`**) lives in **[`docs/claude/prompts/README.md` § Human developer setup](docs/claude/prompts/README.md#human-developer-setup-before-you-open-a-prompt-file)**. The prompt track expects **`GH_USERNAME`**, **`GH_REPO`**, and a fine-grained **`GH_PAT`** in `.env` (committed templates start in [`VIDEO_1_PROMPTS.md`](docs/claude/prompts/VIDEO_1_PROMPTS.md) prompt **3**). Phases **1–2** use the **`gh`** CLI for push/PR against **`origin`**; from **Phase 3** onward, prompts move remote GitHub steps to **GitHub MCP** while still reading those same variables—never commit the PAT.
- **Anything else** your tooling needs (for example **Context7** or other MCP credentials)—only if you enable those servers; keep secrets in the environment, not in git.

---

## Repository layout (artifacts only)

```
README.md         # This chapter’s overview (you are here)
docs/
  README.md       # Map of docs/ and reading order
  reqs/           # Master BUSINESS / FUNCTIONAL / TECHNICAL requirements
    mvp/          # MVP milestone pointers
    enhancements/ # Post-MVP enhancement pointers
  claude/         # Claude Code helpers: phased prompt series, templates, learning logs
    README.md     # How to use docs/claude/
    prompts/
      README.md   # Human setup before prompts + dir listing + summary of each VIDEO_* file
      VIDEO_*_PROMPTS.md  # Follow-along build prompts (run in lexicographic order)
    build-notes/  # Per-video harness notes (README + learner-generated VIDEO_*.md)
    templates/    # e.g. log-claude-build.skill.md → .claude/skills/
    CLAUDE_CODE_BUILD_LOG.md  # Cumulative harness log (stub; VIDEO_1 prompts 9+11, then each VIDEO_* before PR)
    GLOBAL.CLAUDE.md
  supplementary/ # Optional long-form HTML (e.g. tooling comparisons, fundamentals)
designs/          # mockup-pages/, brand/, COLOR_PALETTE.md, README — UI contract
LICENSE           # License for materials in this folder
```

Generated application folders (for example `backend/` and `frontend/` as described in the MVP technical slice) appear **after** you begin implementation; they are not shipped as part of this artifact-only package.

---

## License

See [`LICENSE`](LICENSE).

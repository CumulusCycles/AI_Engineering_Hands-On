# Documentation

Use this file as the **map of `docs/`**. Material falls into three areas:

- **`reqs/`** — product specifications: the **master trio** (business, functional, technical), plus **MVP** and **post-MVP enhancement** milestone slices.
- **`claude/`** — Claude Code teaching artifacts: **numbered `VIDEO_*` prompts** (hands-on build order), **[`claude/GLOBAL.CLAUDE.md`](claude/GLOBAL.CLAUDE.md)** (reference guidance), and **[`claude/README.md`](claude/README.md)** (**Claude Code features used in this chapter** + prompt index and order).
- **`supplementary/`** — optional standalone HTML (e.g. fundamentals, tooling comparisons). Not required to implement ScriptSprout.

**UI contract** (mockups, palette, brand): **[`../designs/README.md`](../designs/README.md)** (sibling of `docs/`, not inside it).

---

## Layout

| Path | Role |
|------|------|
| **`README.md`** | This file — how `docs/` is organized and what to read first. |
| **[`reqs/BUSINESS_REQS.md`](reqs/BUSINESS_REQS.md)** | Business requirements: vision, personas, scope, business rules. |
| **[`reqs/FUNCTIONAL_REQS.md`](reqs/FUNCTIONAL_REQS.md)** | Functional requirements: observable behavior, roles, journeys — **authoritative** for *what the system does*. |
| **[`reqs/TECHNICAL_REQS.md`](reqs/TECHNICAL_REQS.md)** | Technical requirements: stack, architecture, security, data and AI integration intent. |
| **[`reqs/mvp/`](reqs/mvp/)** | MVP milestone: which master sections apply first; pointers, not a second spec. |
| **[`reqs/enhancements/`](reqs/enhancements/)** | Post-MVP tracks (E1–E5): same pattern on top of MVP. |
| **[`claude/README.md`](claude/README.md)** | **Claude Code features used here** (human-readable table) + **prompt file order** for the hands-on path. |
| **[`claude/GLOBAL.CLAUDE.md`](claude/GLOBAL.CLAUDE.md)** | Reference Claude guidance (not the generated project-root `CLAUDE.md`). |
| **[`claude/prompts/`](claude/prompts/)** | **`VIDEO_*_PROMPTS.md`** — prompts given to Claude Code in order; start at **`VIDEO_1`**. |
| **[`claude/build-notes/`](claude/build-notes/)** | Learner-generated **per-video** Claude Code learning logs (`VIDEO_*.md`); see README there. |
| **[`claude/CLAUDE_CODE_BUILD_LOG.md`](claude/CLAUDE_CODE_BUILD_LOG.md)** | **Cumulative** harness log (one section per **`VIDEO_*`**; updated by the embedded **`log-claude-build`** step before that module’s push/PR—see prompts). |
| **[`claude/templates/`](claude/templates/)** | Source templates (e.g. **`log-claude-build.skill.md`**) copied into **`.claude/`** during the build. |
| **[`supplementary/`](supplementary/)** | Optional long-form HTML; for depth reading, not blocking implementation. |

---

## Reading order

### Product requirements (always)

1. **`reqs/`** (master trio) — `BUSINESS_REQS.md` → `FUNCTIONAL_REQS.md` → `TECHNICAL_REQS.md` (follow cross-links inside each file as needed).
2. **`reqs/mvp/`** — the three `MVP_*` files after the master trio, for the first shippable slice.
3. **`reqs/enhancements/`** — the three `ENHANCEMENTS_*` files after MVP, in the order described in those files.

If anything in **`reqs/mvp/`** or **`reqs/enhancements/`** disagrees with the master **`reqs/*_REQS.md`** files at the root of **`reqs/`**, the **master trio wins**.

### Claude Code hands-on path (when using the shipped prompts)

4. **[`claude/README.md`](claude/README.md)** — see which Claude Code features this chapter uses, then confirm prompt filenames and order.
5. **`claude/prompts/`** — run **`VIDEO_1`** through **`VIDEO_4.2`** in **lexicographic order** (same order as listed in `claude/README.md`).
6. **Harness teaching artifacts** — **[`claude/build-notes/`](claude/build-notes/)** (per-module **`VIDEO_*.md`** after you run the prompts) and **[`claude/CLAUDE_CODE_BUILD_LOG.md`](claude/CLAUDE_CODE_BUILD_LOG.md)** (cumulative); the **`log-claude-build`** procedure is defined in **[`claude/templates/log-claude-build.skill.md`](claude/templates/log-claude-build.skill.md)** and installed into **`.claude/skills/`** during **VIDEO_1** (see **[`build-notes/README.md`](claude/build-notes/README.md)**).

The prompts assume you have already internalized the **master `reqs/`** reading (especially before **`VIDEO_1`**, which tells Claude to read those specs first).

---

## Revision

| Version | Notes |
|---------|-------|
| 1.0 | Baseline map: **`docs/README.md`**, **`reqs/`** master trio, **`reqs/mvp/`**, **`reqs/enhancements/`**. |
| 1.1 | Document **`claude/`** and **`supplementary/`**; add hands-on reading order; lexicographic prompt order. |
| 1.2 | **`claude/README.md`**: human-facing Claude Code feature table + intro; **`docs/README.md`**: pointers updated. |
| 1.3 | **`log-claude-build`** skill template, **`build-notes/`**, **`CLAUDE_CODE_BUILD_LOG.md`**; **VIDEO_1** prompt **9** installs skill, **11** first log run. |
| 1.4 | **`log-claude-build`** runs before push/PR in each module (skill installed in **VIDEO_1** prompt **9**, first run in **11**); learners never invoke the skill manually; cumulative log sections **replace** on re-run per skill. |
| 1.5 | Chapter **`README.md`**, **`docs/README.md`** hands-on path, **`docs/claude/README.md`** learning-log intro, **`CLAUDE_CODE_FUNDAMENTALS.html`** callout — aligned with **`build-notes/`**, **`templates/`**, and prompt-driven logger. |
| 1.6 | Logger docs: step is **before push/PR** (e.g. **VIDEO_3** before first MCP push), not “last prompt in file”; phase 1 **`validate-and-fix`** is prompt-defined, **`log-claude-build`** from **`templates/`**. |

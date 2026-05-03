# `log-claude-build` skill (copy to `.claude/skills/log-claude-build.md`)

Maintainers: **VIDEO_1** prompt **9** copies everything **below** the horizontal rule into **`.claude/skills/log-claude-build.md`** (skip the title and this paragraph).

---

You are documenting **Claude Code harness changes** for learners.

**When invoked** — the user will say which video phase this is (e.g. `VIDEO_1`, `VIDEO_2.1`). Treat that string as **`VIDEO_ID`**.

**Steps:**

1. **Gather facts from git** — On the current feature branch, list commits and/or use `git diff` / `git show` to identify files under **`CLAUDE.md`**, **`.claude/`**, and (only if changed for harness reasons) **`.gitignore`** or **`.env.example`** at the repo root. Do **not** summarize `backend/` or `frontend/` here unless the user explicitly asks.

2. **Classify each path** — For each file, note which Claude Code idea it illustrates, e.g. **project `CLAUDE.md`**, **`.claude/settings.json` (permissions)**, **scoped rule**, **skill**, **slash command**, **MCP config**, **agent definition**, **`.claude/README.md` (load order)**.

3. **Write the per-video note** — Create or overwrite **`docs/claude/build-notes/{VIDEO_ID}.md`** with:
   - **Video / phase** — `VIDEO_ID`
   - **What we added or changed** — short paragraph
   - **Claude Code features exercised** — bullet list (rules vs skills vs commands vs MCP vs agents vs settings)
   - **Files touched** — table or bullets: path → one-line purpose
   - **Try it** — one concrete action (e.g. invoke a slash command, open an MCP config) optional

4. **Update the cumulative log** — Open **`docs/claude/CLAUDE_CODE_BUILD_LOG.md`**. If it does not exist, create it with title `# Claude Code build log`. Search for a section whose heading starts with **`## {VIDEO_ID}`** (same `VIDEO_ID`). If it exists, replace that whole section—from that heading through the line before the next `## ` heading (or end of file)—with a fresh section; otherwise **append** at the end. Each section uses:
   - Heading: `## {VIDEO_ID} — <today’s date>`
   - 3–6 bullets summarizing harness changes only (no app code).

5. **Report** — Tell the user both files were updated and their paths.

**Hard rules:**

- Never invent files that git does not show as changed in this phase.
- Keep entries **concise**; link paths in backticks.
- Do not duplicate long excerpts from `CLAUDE.md` — summarize.

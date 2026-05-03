# Claude Code build notes (learner-generated)

This folder holds **per-video learning logs** produced while you follow the **`VIDEO_*`** prompts. Files here are **not** part of the ScriptSprout product spec—they explain **what you configured in Claude Code** (`CLAUDE.md`, `.claude/`, harness-related root files).

## Who does what (pedagogy logging only)

**Claude (when you run the prompts):** follows **`log-claude-build`** as embedded in each **`VIDEO_*`** file—reads git for harness paths, writes **`docs/claude/build-notes/{VIDEO_ID}.md`**, updates **`docs/claude/CLAUDE_CODE_BUILD_LOG.md`**, and commits when the prompt says to. In **VIDEO_1**, prompt **9** installs **`.claude/skills/log-claude-build.md`** from **[`../templates/log-claude-build.skill.md`](../templates/log-claude-build.skill.md)**; prompt **11** runs the procedure the first time.

**You:** send the **`VIDEO_*`** prompts in Claude Code and **approve** file/shell actions when asked so those steps can run. You **do not** hand-maintain these log files or separately invoke the skill in normal flow. If a logger step fails, fix the blocker and **re-run** that prompt.

This section is **only** about harness pedagogy logs—not application code, tests, or PRs.

## Files

| File pattern | Purpose |
|--------------|---------|
| **`VIDEO_1.md`**, **`VIDEO_2.1.md`**, … | One note per **`VIDEO_*`** module, written when Claude runs the embedded **`log-claude-build`** step **before push/PR** in that file (**VIDEO_1**: **prompt 11**, after **Context7** in **prompt 10**). You do not invoke the skill yourself. |
| **[`../CLAUDE_CODE_BUILD_LOG.md`](../CLAUDE_CODE_BUILD_LOG.md)** | **Cumulative** harness log: one **`## VIDEO_*`** section per module (re-running the logger for the same **`VIDEO_ID`** **replaces** that section—see the skill). |

The **canonical skill definition** lives in **[`../templates/log-claude-build.skill.md`](../templates/log-claude-build.skill.md)**; your working copy is **`.claude/skills/log-claude-build.md`** after **VIDEO_1** prompt **9** (prompt **11** runs it for the first time).

Until you run the prompts, this directory may be empty except for this README.

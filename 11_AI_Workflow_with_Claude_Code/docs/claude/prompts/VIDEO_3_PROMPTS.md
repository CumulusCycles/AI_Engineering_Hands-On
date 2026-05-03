1.
```
**Role:** You are a senior engineer extending Claude Code's capabilities on
the ScriptSprout project. This phase adds native GitHub access (MCP) and a
custom review agent built on top of it. Priorities: keep secrets out of
committed files, document the complete PR review lifecycle so the workflow is
reproducible, and keep CLAUDE.md a living source of truth for future sessions.

**Input:** Update the existing `CLAUDE.md` at the project root to reflect
Phase 3. Do not create a new file.

**Context:**
- CLAUDE.md was last updated at the end of Phase 2.2 (frontend MVP).
- Phase 3 has two parts: Part A adds GitHub MCP, Part B adds the
  `pr-reviewer` agent. Both belong in one phase because the agent depends on
  GitHub MCP.
- Raw `git add` / `git commit` continue to be used locally. Only the *remote*
  GitHub operations shift from `gh` CLI to GitHub MCP from this phase on.
- `GH_PAT`, `GH_USERNAME`, `GH_REPO` are already populated in `.env`
  (documented in `.env.example` since **VIDEO_1**).
- MCP servers themselves are listed in `.claude/README.md` (updated in
  prompt 4 of this file), NOT in `CLAUDE.md` — keep `CLAUDE.md` focused on
  project-level concerns.
- Do NOT change sections unrelated to Phase 3 (coding standards, validate-
  and-fix skill, commands, rules).

**Execution:**
1. Edit `CLAUDE.md` with the following changes:

   a. Current phase → change to:
      "Phase 3: Extending Claude Code — adding GitHub MCP server and the
      pr-reviewer agent"

   b. Current build scope → replace with:
      Part A — GitHub MCP server:
        Register GitHub MCP as a project MCP server
        Authenticate via GH_PAT from .env, scoped to GH_USERNAME/GH_REPO
        Replace gh CLI for: branch creation, push, PR open/diff/comment/merge
      Part B — PR review agent (.claude/agents/pr-reviewer.md):
        Fetches PR diff via GitHub MCP
        Sends diff to OpenAI for code review (focus on bugs, security,
        architecture violations — skip style nitpicks)
        Posts review as a PR comment via GitHub MCP
        Signals completion back to Claude Code

   c. Add a new section: Git Workflow
      - Feature branches for all phases — nothing goes straight to main
      - GitHub MCP (active from Phase 3) handles: creating branches, pushing,
        opening PRs, fetching diffs, posting comments, merging PRs
      - Use GitHub MCP for all GitHub interactions — not gh CLI or raw git push
      - Raw git commands (git add, git commit) still used locally for staging
        and committing
      - GH_PAT, GH_USERNAME, GH_REPO are in .env — GitHub MCP reads these
      - PR review lifecycle:
        * After opening a PR via GitHub MCP, spawn the pr-reviewer agent on it
        * Agent fetches the diff, calls OpenAI for review, posts comments via
          GitHub MCP
        * Claude alerts you: "PR #N is ready for your review — X comments posted"
        * You review: add comments or say "looks good"
        * If changes requested: Claude fixes, pushes to same branch, agent
          re-reviews
        * If approved: ask Claude to merge via GitHub MCP, then pull to local
          main

2. Stage and commit with:
   `docs: update CLAUDE.md for Phase 3 GitHub MCP and PR review agent`
```

2.
```
Please check git status, then create and checkout a new feature branch called
feat/extending-claude-code. Confirm we are on the new branch.

Note: this is the last time we create a branch with raw `git checkout -b`.
After this phase, **remote** branch creation moves to GitHub MCP. The
**local** checkout still uses `git fetch && git checkout` since Claude
Code's shell has no native MCP-checkout — see VIDEO_4.1a/4.1b/4.2 prompt 3
for the two-step pattern.
```

3.
```
**Input:** Register the GitHub MCP server for this project by creating
`.claude/mcp/github.json`.

**Context:**
- `GH_PAT`, `GH_USERNAME`, `GH_REPO` are already populated in `.env` and
  documented in `.env.example`.
- Use the standard MCP server JSON config format. Context7 and GitHub MCP
  may use different transports (e.g. SSE/HTTP vs stdio), so the exact shape
  may differ from `.claude/mcp/context7.json`. If unsure of GitHub MCP's
  exact config shape, consult Context7 documentation for the official GitHub
  MCP server (e.g. `@modelcontextprotocol/server-github` or current
  equivalent) before writing the file. Keep secrets out of the file via
  env-variable references.
- The PAT value MUST be referenced by environment variable name. Do NOT
  hardcode the PAT string into the config file under any circumstances — the
  config is committed to git; the PAT is not.
- No other files change in this prompt (`.claude/README.md` gets its update
  in the next prompt).

**Execution:**
1. Create `.claude/mcp/github.json`. Configure the GitHub MCP server to:
   - Authenticate using `GH_PAT` from the environment
   - Scope to the repository identified by `GH_USERNAME` and `GH_REPO`
   - Enable these capabilities:
     * Create and push branches
     * Open pull requests
     * Fetch PR diffs
     * Post PR review comments
     * Merge pull requests
     * Read repository contents

2. After creating the file, print its contents to the terminal so I can
   verify the config before we commit it. Do NOT stage or commit yet — I
   want to eyeball the PAT handling first.
```

4.
```
**Input:** Update `.claude/README.md` so both MCP servers are documented and
the git workflow change from Phase 3 is recorded.

**Context:**
- `.claude/README.md` currently documents only Context7 MCP (added in Phase 1).
- `.claude/mcp/github.json` was just created in the previous prompt and
  should now be reflected in the README.
- Do NOT touch `CLAUDE.md` — it was already updated in PROMPT 1.
- The `.claude/agents/` folder does not exist yet (created in PROMPT 7) —
  don't document it here; that comes later.

**Execution:**
1. Update the MCP servers section to list both servers active:
   - Context7 MCP (active since Phase 1): provides up-to-date library
     documentation for FastAPI, SQLAlchemy, React, Vite, and other stack
     dependencies
   - GitHub MCP (active from Phase 3): handles all GitHub interactions —
     branch creation, push, PR open, diff fetch, review comments, merge

2. Add a note about the git workflow change:
   - Raw git (`git add`, `git commit`) still used locally for staging/committing
   - GitHub MCP used for all remote GitHub operations from Phase 3 onward
   - `gh` CLI remains installed as a fallback but is no longer the primary tool

3. Stage and commit with:
   `docs: document GitHub MCP in .claude/README.md`
```

5.
```
**Input:** Verify that both MCP servers (Context7 and GitHub) are reachable
and authenticated before we rely on them for the rest of this phase.

**Context:**
- Context7 has been active since Phase 1 — this is a sanity check, not a
  first use.
- GitHub MCP was just configured in `.claude/mcp/github.json` in PROMPT 3.
- If GitHub MCP fails here, the rest of the video cannot proceed — so this
  is an explicit early-failure checkpoint.
- Do NOT push, create branches, or modify the remote in this prompt — we are
  only reading.

**Execution:**
1. Use Context7 to look up current documentation for SQLAlchemy 2.x session
   management — specifically how to use `Session` as a context manager.
   Paste the relevant excerpt back so I can confirm we are reading live docs.

2. Using GitHub MCP, perform two read-only checks:
   - Fetch the list of branches on the remote (should show at least `main`
     and `feat/extending-claude-code`).
   - Show the authenticated user.

3. Report the outcome of both checks. If GitHub MCP fails, stop and tell me
   the exact error — do not continue to the next prompt.
```

6.
```
**Input:** Annotate the existing `OPENAI_API_KEY` entry in `.env.example`
to document its second consumer (the pr-reviewer agent).

**Context:**
- `OPENAI_API_KEY` is already in `.env.example` from VIDEO_2.1 prompt 7
  (under the `# AI (OpenAI)` sub-section of the Phase 2.1 backend block).
  It is consumed there via Pydantic Settings.
- Phase 3 introduces a SECOND consumer: the pr-reviewer agent calls OpenAI
  *directly* (outside of the backend's Pydantic Settings layer).
- We are NOT duplicating the variable — both consumers read the same env
  variable. We only update the comment so future readers understand the key
  now serves two callers.

**Execution:**
1. Edit `.env.example`. Find the existing `OPENAI_API_KEY=...` line in the
   Phase 2.1 backend section and replace its preceding comment to note both
   consumers. The `# AI (OpenAI)` line becomes:

   ```
   # AI (OpenAI) — used by the backend (via Pydantic Settings) AND by the
   # pr-reviewer agent (which calls OpenAI directly). Same key, two consumers.
   OPENAI_API_KEY=your_openai_api_key_here
   OPENAI_CHAT_MODEL=gpt-4o-mini
   ```

   Do NOT add a new `# --- Phase 3: PR Review Agent ---` section — the
   variable already lives in the Phase 2.1 block. Other variables in that
   block (DATABASE_URL, sessions, auth, etc.) stay untouched.

2. Stage and commit with:
   `docs: annotate OPENAI_API_KEY in .env.example for pr-reviewer agent`
```

7.
```
**Input:** Create the `.claude/agents/` folder and the `pr-reviewer` agent
definition at `.claude/agents/pr-reviewer.md`. Then update `.claude/README.md`
to document the new folder and the agent.

**Context:**
- This is the first custom agent in the project — `.claude/agents/` does not
  yet exist.
- The agent depends on GitHub MCP (just added) for diff fetching and comment
  posting, and on `OPENAI_API_KEY` (just added to `.env.example`) for the
  review call itself.
- Deliberately opinionated review scope: the agent must focus on *meaningful*
  issues (bugs, security, architecture violations, missing error handling,
  logic errors) and explicitly skip style/formatting/whitespace nitpicks. A
  noisy reviewer gets ignored.
- Use `gpt-4o` for the review model — capable enough for code review and
  already justified as the app's OpenAI model.
- The agent must never silently fail — every failure mode should be reported
  back so the diff review is not lost.

**Execution:**
1. Create `.claude/agents/pr-reviewer.md` with the following structure:

   ## Purpose
   Review a pull request by fetching its diff, sending it to OpenAI for
   analysis, posting review comments to the PR via GitHub MCP, and reporting
   completion.

   ## Trigger
   Invoked after a PR is opened. Called as:
   "Run the pr-reviewer agent on PR #N"

   ## Inputs
   - PR number (provided when invoked)
   - Repository: read from `GH_USERNAME` and `GH_REPO` environment variables
   - OpenAI API key: read from `OPENAI_API_KEY` environment variable

   ## Steps

   ### Step 1 — Fetch the PR diff
   Using GitHub MCP, fetch the full diff for the specified PR number. Also
   fetch the PR title and description for context.

   ### Step 2 — Send to OpenAI for review
   `OPENAI_API_KEY` lives in the project-root `.env`, which is NOT
   automatically loaded into Claude Code's shell. Load it explicitly before
   calling OpenAI. Either approach is acceptable:
   - Run a one-off Python helper that loads `.env` (e.g. via `python-dotenv`
     or by reading the file directly) and POSTs to the OpenAI API, OR
   - In bash: `set -a && . ./.env && set +a` to export `.env` vars, then
     use `curl` with `Authorization: Bearer $OPENAI_API_KEY`.

   Call the OpenAI chat completions endpoint with:
   - Model: `gpt-4o`
   - System prompt:
     "You are an experienced senior software engineer conducting a pull
     request review. Your job is to identify meaningful issues: bugs,
     security problems, violated architecture patterns, missing error
     handling, and logic errors. Do NOT comment on: formatting, naming
     style, whitespace, or minor style preferences. Do NOT be nitpicky.
     Focus only on issues that matter. For each issue found, provide:
     - The file and approximate line reference
     - A clear description of the problem
     - A concrete suggestion for how to fix it
     If the code looks good, say so clearly and briefly. Respond in plain
     text — no markdown headers."
   - User message: the PR title, description, and full diff.

   ### Step 3 — Post review comments to the PR
   Using GitHub MCP, post the OpenAI review response as a PR review comment
   (not a regular comment) so it appears in the review tab. Prefix the
   comment with: `Automated review via OpenAI gpt-4o:`

   ### Step 4 — Signal completion
   Report back to Claude Code:
   - PR number reviewed
   - Number of issues identified (or "no issues found")
   - Confirmation that comments have been posted

   Claude Code then alerts the user:
   "PR #N has been reviewed. [X issues / No issues] found. Review comments
   are posted — check the PR when you're ready."

   ## Error handling
   - If GitHub MCP fails to fetch the diff: report the error, do not proceed
   - If the OpenAI call fails: report the error with the failure reason
   - If posting comments fails: report the OpenAI review output directly so
     it is not lost
   - Never silently fail — always report what went wrong

2. Update `.claude/README.md` to:
   - Document the new `agents/` folder
   - Describe the `pr-reviewer` agent (one short paragraph + trigger phrase)

3. Stage and commit with:
   `feat: add pr-reviewer agent and document .claude/agents/`
```

8.
```
**Input:** Run the **`log-claude-build`** procedure in **`.claude/skills/log-claude-build.md`** for **`VIDEO_3`**.

**Context:**
- The skill was installed in **VIDEO_1**. Execute it yourself now—do not ask the learner to trigger the skill manually.
- Stay on **`feat/extending-claude-code`** so the learning-log commit is included when you push the PR in the next prompt.
- Ground summaries in **`git log` / `git diff`** for harness paths only (`CLAUDE.md`, `.claude/`, **`.env.example`**).

**Execution:**
1. Follow the skill end-to-end with **`VIDEO_ID=VIDEO_3`**.
2. Stage and commit with: `docs: VIDEO_3 harness build notes`
```

9.
```
**Input:** Push the branch and open the PR using GitHub MCP — the first real
GitHub MCP push and the first GitHub MCP PR in this project.

**Context:**
- Remote is `origin`, base branch is `main`.
- Use **GitHub MCP** for push and PR open — do NOT use `git push` or
  `gh pr create`. This is the transition prompt where the workflow flips.
- Tests and lint are not relevant on this branch (no application code changed
  — only MCP config, agent definition, docs).
- After this prompt, PROMPT 10 runs the new agent on the PR opened here, so
  the PR URL must be returned.

**Execution:**
1. Using GitHub MCP, push `feat/extending-claude-code` to `origin`.

2. Show me the commits on this branch so I can narrate them on camera before
   the PR body appears.

3. Using GitHub MCP, open a pull request with:
   - Base branch: `main`
   - Title: `feat: add GitHub MCP and pr-reviewer agent`
   - Body (verbatim):

   ```
   ## What this PR contains

   Phase 3 — extending Claude Code with native GitHub access and an automated
   PR review agent built on top of it.

   ### Part A — GitHub MCP
   - `.claude/mcp/github.json` — GitHub MCP server configuration (PAT from env)
   - Branch creation, push, PR open/diff/comment/merge now run natively through MCP
   - `gh` CLI remains as fallback but is no longer the primary tool

   ### Part B — PR review agent
   - `.claude/agents/pr-reviewer.md` — fetches PR diff, calls OpenAI, posts review
   - Focused review prompt: bugs, security, architecture, missing error handling
   - Explicitly skips formatting and style nitpicks
   - `.env.example` — `OPENAI_API_KEY` added (used by the agent)

   ### Documentation
   - `CLAUDE.md` — Phase 3 scope, full git workflow and PR review lifecycle documented
   - `.claude/README.md` — both MCP servers and the agents/ folder documented

   ### What does NOT change
   - All application code — unchanged
   - Rules files, skills — unchanged
   - validate-and-fix workflow — unchanged
   ```

4. Return the PR URL so I can open it in the browser and pass the PR number
   to the next prompt.
```

10.
```
**Input:** Run the `pr-reviewer` agent on the PR that was just opened for
`feat/extending-claude-code`.

**Context:**
- The agent definition lives at `.claude/agents/pr-reviewer.md` — follow
  it exactly. Do not improvise new steps or skip any.
- The PR number is the one returned by the previous prompt — use that exact
  number.
- The review MUST post back to the same PR via GitHub MCP, not to stdout.
- This is the meta moment of the video: the agent is reviewing the very PR
  that introduced it. Make sure the completion alert is explicit so it's
  narratable on camera.

**Execution:**
1. Invoke the `pr-reviewer` agent on the PR. Follow the agent steps in
   order:
   a. Fetch the PR diff and title via GitHub MCP
   b. Send to OpenAI `gpt-4o` using the system prompt defined in the agent
   c. Post the review as a PR review comment via GitHub MCP
   d. Report back with: PR number, issue count (or "no issues"), and
      confirmation that the comment was posted

2. Surface the completion alert back to me in the exact form documented in
   the agent: "PR #N has been reviewed. [X issues / No issues] found.
   Review comments are posted — check the PR when you're ready."
```

11.
```
**Input:** Merge `feat/extending-claude-code` into `main` via GitHub MCP,
then sync local `main`.

**Context:**
- The agent's review was acceptable — no changes requested.
- Use GitHub MCP for the merge, not `gh pr merge` or the web UI.
- After merging, pull locally so `main` reflects the merge commit.

**Execution:**
1. Using GitHub MCP, merge the PR into `main`.
2. Checkout `main` locally and pull from `origin`.
3. Confirm `git status` is clean and show me the top few commits on `main`
   so I can verify the merge landed.
```

12.
```
**Input:** Address the issue raised by the agent, push the fix, re-run the
review, and merge once clean.

**Context:**
- The agent flagged a concrete issue in its PR review comment — **replace this
  bullet with a one-sentence summary of that finding** before executing (e.g.
  “missing error handling on MCP timeout” or “PAT scope insufficient for merge”).
  If you are recording this video live, paste the real reviewer text here for the
  audience. This prompt is optional unless prompt 10’s review reported problems.
- Fix the root cause — do not just silence the symptom.
- Use GitHub MCP for push, re-review, and merge. Raw git is still fine for
  local staging/committing.
- Do NOT merge until the re-review comes back clean.

**Execution:**
1. Fix the flagged issue in the relevant file(s).
2. Stage and commit the fix with a message describing the change (not
   "fix review" — describe *what* was fixed).
3. Using GitHub MCP, push the fix to `feat/extending-claude-code`.
4. Re-run the `pr-reviewer` agent on the PR and report back the new outcome.
5. Run **`log-claude-build`** for **`VIDEO_3`** again (per `.claude/skills/log-claude-build.md`) so harness notes reflect any fix that touched `CLAUDE.md`, `.claude/`, or harness **`.env.example`**. Stage and commit only if docs changed: `docs: refresh VIDEO_3 harness build notes`.
6. Once the re-review is clean, use GitHub MCP to merge into `main`,
   checkout `main` locally, pull, and confirm clean.
```


# Claude Code Fundamentals

This guide is ordered for learning: each section assumes you understand the ones before it. For authoritative, up-to-date detail on install paths, every `settings.json` key, and policy behavior, refer to the official documentation linked at the end.

---

## 1. What is Claude Code?

Claude Code is an **agentic coding tool** that reads your codebase, edits files, runs commands, and integrates with your development tools. It understands your entire codebase and can work across multiple files and tools to get things done — building features, fixing bugs, automating development tasks, and more.

You can run it in several **surfaces**: terminal CLI, VS Code extension, JetBrains plugin, desktop app, and browser (including the Claude iOS app). The same core concepts — permissions, `CLAUDE.md`, MCP, hooks — apply across surfaces because they share the same underlying engine.

### Installation (CLI)

The quickest way to get started:

```bash
# macOS, Linux, or WSL
curl -fsSL https://claude.ai/install.sh | bash

# Windows PowerShell
irm https://claude.ai/install.ps1 | iex
```

Then start Claude Code in any project:

```bash
cd your-project
claude
```

You'll be prompted to log in on first use. Native installs auto-update in the background. See the [official quickstart](https://code.claude.com/docs/en/quickstart) for Homebrew, WinGet, and other install options.

---

## 2. How Claude Code Differs from Claude.ai Chat

| Dimension | Claude.ai (browser chat) | Claude Code |
| --- | --- | --- |
| **Primary unit of work** | Conversation | Tasks in a codebase |
| **Repository access** | You paste or upload context; no automatic repo reading | Reads files from disk (within allowed permissions) |
| **Execution** | Suggests text; you copy changes manually | Can edit files, run tests, drive git, call MCP tools |
| **Persistence** | Thread history; you re-explain each new thread unless you paste again | `CLAUDE.md`, rules, auto memory, and project config reload each session |
| **Risk profile** | Lower direct impact on disk | Higher: treat it like a junior dev with shell access — review diffs and permissions carefully |

Use **chat** for open-ended questions, drafts, and learning. Use **Claude Code** when the outcome is **software change** verified in your project tree (build, test, PR).

---

## 3. Consumer Plans vs. API Billing

Anthropic offers **consumer Claude** as named plans (for example **Free**, **Pro**, and **Max**): you pay a predictable subscription per person, or start on the free tier. Claude.ai chat and Claude Code are both surfaces on that same subscription — not separately metered products. Moving to a higher tier generally means more headroom: higher usage limits, broader model access, and additional features.

**API access** (via Anthropic Console or an enterprise agreement) is billed **on demand**: cost tracks how much the system actually runs, typically token-shaped usage for model calls, often plus separate charges for platform capabilities (tools, batch, caching, and similar). There is no Free/Pro/Max label on an API invoice — you think in terms of projects, API keys, budgets, and spend that scales with traffic.

Claude Code can authenticate through **subscription** paths (sign in with your Claude.ai account) or **Console/API** paths depending on how you configure the tool. The economic model — flat subscription vs. metered — follows that choice.

> Current plan names, inclusions, and API meter details change over time. See [Claude pricing](https://www.claude.com/pricing) and [API pricing](https://platform.claude.com/docs/en/about-claude/pricing) for the latest.

---

## 4. Mental Model: One Session at a Time

Each Claude Code session starts with a **fresh context window**. Anything not loaded from disk — instructions, settings, retrieved files — is gone when the session ends.

This is why the product relies on **files on disk** for things you want every time: `CLAUDE.md`, `.claude/settings.json`, rules, skills, hooks, and MCP configuration. These reload automatically at the start of every session.

---

## 5. Two Kinds of Memory

Claude Code has two complementary memory systems. Both load at the start of every conversation:

| | CLAUDE.md files | Auto memory |
| --- | --- | --- |
| **Who writes it** | You | Claude |
| **What it contains** | Instructions and rules | Learnings and patterns |
| **Scope** | Project, user, or org | Per working tree |
| **Use for** | Coding standards, workflows, architecture | Build commands, debugging insights, preferences Claude discovers |

**`CLAUDE.md` (and rules):** You write stable instructions — stack conventions, build commands, architecture decisions, review checklists. Keep it under 200 lines per file; longer files consume more context and reduce how reliably Claude follows them.

**Auto memory:** Claude may write compact learnings across sessions (for example, commands that worked, debugging notes). It stores these in `~/.claude/projects/<project>/memory/`. You can toggle it on or off via `/memory` in a session, or by setting `autoMemoryEnabled` in your settings. Requires Claude Code v2.1.59 or later.

> **Important:** `CLAUDE.md` content is delivered as a user message, not as an enforced system prompt. Claude reads it and tries to follow it, but it is not a hard enforcement layer. For hard limits (deny reading secrets, block shell patterns), use **permissions in `settings.json`** — not prose alone.

---

## 6. `CLAUDE.md`: Where It Lives and How It Stacks

CLAUDE.md files can live in several locations, each with a different scope. All discovered files are **concatenated into context** — they don't override each other. More specific locations are appended later, so they read last at that level.

| Scope | Location | Purpose | Shared with |
| --- | --- | --- | --- |
| **Managed (enterprise)** | macOS: `/Library/Application Support/ClaudeCode/CLAUDE.md`<br>Linux/WSL: `/etc/claude-code/CLAUDE.md`<br>Windows: `C:\Program Files\ClaudeCode\CLAUDE.md` | Org-wide policy; cannot be excluded by individual settings | All users in the organization |
| **Project (team)** | `./CLAUDE.md` or `./.claude/CLAUDE.md` | Shared project norms (commit to git) | Team via source control |
| **User (personal, all repos)** | `~/.claude/CLAUDE.md` | Your personal defaults everywhere | Just you |
| **Local (personal, this repo only)** | `./CLAUDE.local.md` | Per-project personal preferences; add to `.gitignore` | Just you |

**Loading order:** Claude walks up the directory tree from your working directory, loading `CLAUDE.md` and `CLAUDE.local.md` from each level. Files in subdirectories load on demand when Claude reads files in those directories.

**Monorepos:** If other teams' `CLAUDE.md` files are getting picked up and creating noise, use the `claudeMdExcludes` setting to skip them by path or glob pattern. Add it to `.claude/settings.local.json` so the exclusion stays local to your machine:

```json
{
  "claudeMdExcludes": [
    "**/other-team/CLAUDE.md"
  ]
}
```

**Imports:** `CLAUDE.md` can pull in other files using `@path/to/file` syntax. Both relative and absolute paths are supported. Imports recurse up to a depth of five hops — avoid building deep chains. Example:

```
See @README for project overview and @package.json for available npm commands.
```

**`AGENTS.md`:** Claude Code reads `CLAUDE.md`, not `AGENTS.md`. If your repository already uses `AGENTS.md` for other coding agents, create a `CLAUDE.md` that imports it so both tools read the same instructions:

```markdown
@AGENTS.md

## Claude Code

Use plan mode for changes under `src/billing/`.
```

**Bootstrap:** Run `/init` to generate a starting `CLAUDE.md` from your repo. Claude analyzes your codebase and creates a file with build commands, test instructions, and discovered conventions. Refine it by hand afterward.

---

## 7. The `.claude/` Directory (Project Brain)

Think of **`.claude/`** as the **project-local control plane**: files your team commits so everyone gets consistent behavior.

| Path | Role |
| --- | --- |
| `.claude/settings.json` | Shared JSON settings: permissions, hooks, model defaults — team scope; commit to git |
| `.claude/settings.local.json` | Your personal overrides for this repo; Claude auto-configures git to ignore this file |
| `.claude/CLAUDE.md` | Alternative location for the main project instruction file (equivalent to root `CLAUDE.md`) |
| `.claude/rules/` | Modular instruction files; optional path scoping via YAML frontmatter |
| `.claude/agents/` | Project subagents: markdown files with YAML frontmatter (prompt + tool policy) |

**User-wide equivalents** live under `~/.claude/` — for example `~/.claude/settings.json`, `~/.claude/agents/`, `~/.claude/rules/`.

**MCP servers** for the project are defined in a separate `.mcp.json` file at the project root (not inside `.claude/`). User-level MCP configs and per-project state are stored in `~/.claude.json`.

---

## 8. Rules: `.claude/rules/`

When `CLAUDE.md` grows large, split topics into `.claude/rules/*.md`. Files are discovered recursively, so you can use subdirectories like `frontend/` or `backend/`.

- **Always-on rules:** Markdown files *without* path frontmatter load for the whole project at session start, same priority as `.claude/CLAUDE.md`.
- **Path-scoped rules:** YAML frontmatter with a `paths` glob list loads the rule only when Claude is working with matching files — useful for keeping API guidance near the API code, for example:

```yaml
---
paths:
  - "src/api/**/*.ts"
---

# API Development Rules

- All endpoints must include input validation
- Use the standard error response format
```

Path-scoped rules trigger when Claude reads matching files, not on every tool use. This saves context and keeps rules relevant.

**Sharing rules:** `.claude/rules/` supports symlinks, so you can maintain a shared set of rules and link them into multiple projects.

**User-level rules** in `~/.claude/rules/` apply to every project on your machine. Project rules take precedence over user rules when they conflict.

---

## 9. Settings Scopes and Permissions (Safety Layer)

`settings.json` files are the structured enforcement layer — complementing the prose in `CLAUDE.md`.

**Precedence (highest wins):**
1. **Managed settings** (deployed by IT; cannot be overridden)
2. **Command line arguments** (temporary session overrides)
3. **Local** `.claude/settings.local.json`
4. **Project** `.claude/settings.json`
5. **User** `~/.claude/settings.json`

Array-valued settings (like `permissions.allow`) are **concatenated and deduplicated** across scopes — not replaced. A lower-priority scope can safely add entries without overriding higher-priority ones.

**Permissions** let you control exactly which tools and shell patterns Claude can use:

```json
{
  "permissions": {
    "allow": [
      "Bash(npm run lint)",
      "Bash(npm run test *)"
    ],
    "deny": [
      "Bash(curl *)",
      "Read(./.env)",
      "Read(./.env.*)",
      "Read(./secrets/**)"
    ]
  }
}
```

Rules are evaluated in order: `deny` first, then `ask`, then `allow`. The first matching rule wins.

**Default permission modes** (configurable via `permissions.defaultMode`):

| Mode | Behavior |
| --- | --- |
| `default` | Standard permission checking with prompts |
| `acceptEdits` | Auto-accept file edits for paths in the working directory |
| `auto` | A background classifier reviews commands automatically |
| `bypassPermissions` | Skip permission prompts entirely (use with caution) |
| `plan` | Read-only exploration mode |

Interactive configuration is available via **`/config`** in the CLI. Run **`/status`** to see which settings sources are active and where they come from.

---

## 10. Skills and Custom Commands (Repeatable Workflows)

**Skills** package procedures your team repeats: release checklists, database migration policies, incident triage steps. They are stored as markdown files and can be invoked with a `/command`-style name, or loaded automatically by Claude when relevant to the prompt.

Skills differ from `CLAUDE.md` in an important way: they load *on demand* rather than into every session's context. Use skills for long playbooks; keep `CLAUDE.md` short and factual.

Skills can also be run inside a subagent's isolated context — useful when you want a procedure to execute without polluting your main conversation.

See the official [Skills documentation](https://code.claude.com/docs/en/skills) for file layout and invocation syntax.

---

## 11. Subagents

**Subagents** are specialized AI assistants that handle specific types of tasks in their own isolated context window. When a side task would flood your main conversation with search results, logs, or file contents you won't reference again, a subagent handles that work and returns only a summary.

Each subagent has:
- A custom system prompt
- Its own tool restrictions
- Independent permissions
- Optionally, a different model

### Built-in subagents

Claude Code ships with several built-in subagents that Claude uses automatically:

| Subagent | Model | Purpose |
| --- | --- | --- |
| **Explore** | Haiku (fast) | Read-only codebase searching and analysis |
| **Plan** | Inherits from session | Research during plan mode before presenting a plan |
| **General-purpose** | Inherits from session | Complex multi-step tasks requiring both exploration and action |

### Creating custom subagents

Subagents are markdown files with YAML frontmatter. Store them in:

- `.claude/agents/` — project scope (commit to git, shared with team)
- `~/.claude/agents/` — user scope (available across all your projects)

Example subagent file (`.claude/agents/code-reviewer.md`):

```markdown
---
name: code-reviewer
description: Reviews code for quality, security, and best practices. Use after writing or modifying code.
tools: Read, Grep, Glob, Bash
model: sonnet
---

You are a senior code reviewer. When invoked:
1. Run git diff to see recent changes
2. Focus on modified files
3. Report issues organized by priority: Critical / Warning / Suggestion
```

**Supported frontmatter fields** include: `name`, `description`, `tools`, `disallowedTools`, `model`, `permissionMode`, `maxTurns`, `skills`, `mcpServers`, `hooks`, `memory`, `background`, `isolation`, and `color`. Only `name` and `description` are required.

The `model` field accepts aliases (`sonnet`, `opus`, `haiku`), a full model ID (e.g. `claude-sonnet-4-6`), or `inherit` (uses the same model as the main session — the default).

### Invoking subagents

Claude delegates automatically based on the task and each subagent's `description` field. You can also invoke them explicitly:

- **Natural language:** `Use the code-reviewer subagent to check my changes`
- **@-mention:** Type `@` and pick from the typeahead to guarantee a specific subagent runs for that task
- **Session-wide:** `claude --agent code-reviewer` makes the whole session run as that subagent

### Subagents vs. main conversation

Use the **main conversation** for iterative back-and-forth, quick targeted changes, or tasks where multiple phases share significant context.

Use **subagents** when a task produces verbose output, requires specific tool restrictions, or is self-contained enough to return a summary.

Subagents **cannot spawn other subagents**. If you need nested or parallel delegation, use [agent teams](https://code.claude.com/docs/en/agent-teams) or chain subagents from the main conversation.

---

## 12. Output Styles

**Output styles** adjust how Claude answers — more explanatory versus more terse, or a house tone your organization prefers. Configure them via the `outputStyle` key in `settings.json` or through `/config` in the CLI.

Use them for **communication defaults**, not for security rules (use permissions for that).

See the [output styles documentation](https://code.claude.com/docs/en/output-styles) for available styles and how to configure them.

---

## 13. MCP Servers (Connect to the Outside World)

**Model Context Protocol (MCP)** is an open standard for connecting Claude Code to external systems: issue trackers, databases, docs, internal HTTP APIs, Slack, and custom tools.

**Project MCP servers** are declared in **`.mcp.json`** at the project root — team-shared and committed to git.

**User-level** MCP server entries are stored in `~/.claude.json` alongside per-project state and OAuth sessions.

To enable a project's MCP servers automatically for all collaborators, set `enableAllProjectMcpServers: true` in `.claude/settings.json`. Individual servers can be approved or rejected with `enabledMcpjsonServers` and `disabledMcpjsonServers`.

Enterprise deployments can allowlist or denylist MCP servers via managed settings using `allowedMcpServers` and `deniedMcpServers`.

See the [MCP documentation](https://code.claude.com/docs/en/mcp) for server configuration format and advanced options.

---

## 14. Hooks (Automate Around Events)

**Hooks** run external commands when something happens in the Claude Code lifecycle. Common uses include auto-formatting after file edits, logging, validating operations before they execute, or posting to internal systems.

Hook events include:

| Event | When it fires |
| --- | --- |
| `PreToolUse` | Before Claude uses a tool |
| `PostToolUse` | After Claude uses a tool |
| `Stop` | When Claude finishes a response |
| `SubagentStart` | When a subagent begins |
| `SubagentStop` | When a subagent completes |

Hooks are configured in `settings.json` under the `hooks` key. Example:

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          { "type": "command", "command": "./scripts/run-linter.sh" }
        ]
      }
    ]
  }
}
```

Hook commands receive JSON via stdin describing the event. For `PreToolUse` hooks, exit code `2` blocks the operation and feeds stderr back to Claude as an error message.

Managed environments can restrict which hooks run using `allowManagedHooksOnly`.

See the [hooks documentation](https://code.claude.com/docs/en/hooks-guide) for the complete event list, input schema, and exit code behavior.

---

## 15. Plugins and Marketplaces (Composition)

**Plugins** bundle extensions — skills, agents, hooks, MCP server definitions, and other assets — distributed through marketplaces. Project settings can specify which plugins a repo expects; managed policy can constrain which marketplaces or plugins are permitted.

Use the **`/plugin`** command to browse available plugins, install or uninstall them, and add or remove marketplaces. Plugin settings live in `settings.json` under `enabledPlugins` and `extraKnownMarketplaces`.

Learn plugins *after* you understand settings, permissions, skills, agents, hooks, and MCP — otherwise debugging "who added this behavior?" becomes much harder.

---

## 16. Advanced: Scheduling, CI/CD, and Programmatic Use

Claude Code goes beyond interactive sessions:

- **Routines:** Schedule recurring tasks (morning PR reviews, overnight CI analysis, weekly dependency audits) that run on Anthropic-managed infrastructure via `/schedule` in the CLI or from the desktop app.
- **GitHub Actions / GitLab CI/CD:** Automate code review and issue triage in your CI pipeline.
- **Headless / programmatic use:** Run Claude Code non-interactively with `claude -p "your prompt"` or via the Agent SDK for fully custom orchestration.
- **Piping:** Claude Code follows Unix conventions and composes with other tools:

```bash
# Analyze recent logs
tail -200 app.log | claude -p "Slack me if you see any anomalies"

# Bulk review of changed files
git diff main --name-only | claude -p "review these changed files for security issues"
```

See the [CLI reference](https://code.claude.com/docs/en/cli-reference) and [programmatic usage](https://code.claude.com/docs/en/headless) docs for details.

---

## 17. Official Documentation

The official docs live at **`code.claude.com`**. All links below are verified against the live documentation.

| Topic | Link |
| --- | --- |
| Overview and install | [Claude Code overview](https://code.claude.com/docs/en/overview) |
| Quickstart | [Quickstart](https://code.claude.com/docs/en/quickstart) |
| `CLAUDE.md`, rules, imports, auto memory | [Store instructions and memories](https://code.claude.com/docs/en/memory) |
| `.claude/` directory | [Explore the .claude directory](https://code.claude.com/docs/en/claude-directory) |
| Settings, permissions, hooks keys | [Settings](https://code.claude.com/docs/en/settings) |
| Permission system and rule syntax | [Permissions](https://code.claude.com/docs/en/permissions) |
| Skills | [Extend Claude with skills](https://code.claude.com/docs/en/skills) |
| Subagents | [Create custom subagents](https://code.claude.com/docs/en/sub-agents) |
| Agent teams | [Run agent teams](https://code.claude.com/docs/en/agent-teams) |
| MCP | [Model Context Protocol](https://code.claude.com/docs/en/mcp) |
| Hooks | [Automate with hooks](https://code.claude.com/docs/en/hooks-guide) |
| Output styles | [Output styles](https://code.claude.com/docs/en/output-styles) |
| Scheduling | [Run prompts on a schedule](https://code.claude.com/docs/en/scheduled-tasks) |
| CI/CD integration | [GitHub Actions](https://code.claude.com/docs/en/github-actions) |
| Programmatic use | [Headless usage](https://code.claude.com/docs/en/headless) |
| CLI reference | [CLI reference](https://code.claude.com/docs/en/cli-reference) |
| Consumer pricing | [Claude pricing](https://www.claude.com/pricing) |
| API pricing | [API pricing](https://platform.claude.com/docs/en/about-claude/pricing) |

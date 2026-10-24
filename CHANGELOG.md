# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [3.0.0] - 2026-03-18

### Changed (BREAKING)

- **Split architecture** — `~/.claude/` now contains only minimal global config (rules, hooks, guard). Everything else lives in a bootstrapped workspace (default: `~/claude-assistant/`). This keeps `~/.claude/` lean and puts assistant data in a proper version-controlled workspace.
- **`setup.sh` — two-phase install.** Phase 1 installs global config to `~/.claude/`. Phase 2 bootstraps the workspace directory. Users choose the workspace name (default: `claude-assistant`).
- **Skills moved to workspace** — All 6 skills now live in `~/claude-assistant/.claude/skills/` instead of `~/.claude/skills/`. They activate when Claude runs from the workspace.
- **Agents moved to workspace** — Agent definitions now in `~/claude-assistant/agents/`.
- **Task database moved to workspace** — `tasks.db` and `scripts/db.py` now in `~/claude-assistant/`.
- **Knowledge moved to workspace** — `knowledge/` now in `~/claude-assistant/knowledge/`.
- **State moved to workspace** — `state/sessions/`, `state/backlog.md`, `state/rule-feedback.json` now in workspace. Guard audit log stays at `~/.claude/state/guard-log.jsonl` (global security).
- **Hook scripts workspace-aware** — `pre-compact.sh`, `post-compact-reinject.sh`, `session-save-reminder.sh` read workspace path from `~/.claude/workspace.conf`.
- **All path references updated** — Rules, skills, and scripts reference `~/claude-assistant/` instead of `~/.claude/` for workspace data.
- **CLAUDE.md split** — Global `~/.claude/CLAUDE.md` is minimal (~25 lines, points to workspace). Workspace `.claude/CLAUDE.md` has detailed instructions.

### Added

- `~/.claude/workspace.conf` — stores workspace path, read by hook scripts
- `templates/global-CLAUDE.md` — minimal global instructions template
- `templates/workspace-CLAUDE.md` — detailed workspace instructions template
- `templates/workspace-gitignore` — gitignore for the workspace directory

### Removed

- `templates/CLAUDE.md` — replaced by `global-CLAUDE.md` + `workspace-CLAUDE.md`

### Migration from v2.x

If upgrading from v2.x, you'll need to:
1. Re-run `setup.sh` (backs up nothing — save your knowledge/ and tasks.db first)
2. Copy `~/.claude/knowledge/` to `~/claude-assistant/knowledge/`
3. Copy `~/.claude/tasks.db` to `~/claude-assistant/tasks.db`
4. Copy `~/.claude/state/sessions/` to `~/claude-assistant/state/sessions/`
5. Copy `~/.claude/MEMORY.md` to `~/claude-assistant/MEMORY.md`

### Files

- 3 new templates: `global-CLAUDE.md`, `workspace-CLAUDE.md`, `workspace-gitignore`
- 1 removed template: `CLAUDE.md`
- Modified: all rules, all skills, all hook scripts, `setup.sh`, `README.md`, `CHANGELOG.md`

## [2.1.0] - 2026-03-18

### Added

- **Guard audit logging** — Every blocked tool call is now logged to `state/guard-log.jsonl` with timestamp, tool name, reason, and context (first 200 chars). Community request: "audit trail of blocked tool calls — that's intelligence lost." Review with `cat ~/.claude/state/guard-log.jsonl | python3 -m json.tool`.
- **Post-compaction rule re-injection** — New `post-compact-reinject.sh` script fires on `SessionStart:compact` and re-outputs critical rules (security, git, tasks, communication, sessions) as system-reminder content. Addresses the CLAUDE.md fading problem documented in GitHub issues #22309, #21119, #7777. A prompt hook also tells Claude to continue the in-progress task.

### Changed

- `global-guard.py` — `block()` now calls `log_block()` before exiting. Context parameter added to all block calls for richer audit trail.
- `settings.json` — `SessionStart:compact` hook now runs `post-compact-reinject.sh` instead of plain `cat`, plus adds a prompt hook for task continuity.
- `setup.sh` — Copies `post-compact-reinject.sh` to `~/.claude/scripts/`.

### Files

- 1 new: `scripts/post-compact-reinject.sh`
- Modified: `scripts/global-guard.py`, `templates/settings.json`, `setup.sh`, `README.md`, `CHANGELOG.md`

## [2.0.0] - 2026-03-18

### Added

- **`/bootstrap` skill** — Sets up any project's `.claude/` for agentic development. Creates CLAUDE.md, CODEBASE.md, module docs, knowledge files, and optional hooks. Includes LEARNINGS.md with battle-tested patterns.
- **`/create-skill` skill** — Scaffolds new skills with `init_skill.py` (directory + template) and `validate_skill.py` (convention checker). Full workflow: understand, scaffold, write, validate.
- **`communication.md` rule** — Radical honesty (no hype, no flattery, specific praise only), verify-before-assuming, review=revise (don't just critique, produce alternatives), audit=fix (fix issues immediately on review requests), verify before external communication.
- **`security.md` rule** — Hard blocks enforced by global-guard.py, git discipline, secrets management, security-first building, project isolation patterns.
- **`research.md` rule** — Source priority hierarchy, API/endpoint verification (always test before documenting), synthesis rules, output format conventions.

### Changed

- **`tasks.md` rule** — Expanded from 34 to 65 lines. Added: research request flagging, detailed task completion checklist, session-end task updates, effort tiers (S/M/L), operational guidelines (bias toward action, finish the job, priority drift guard).
- **`sessions.md` rule** — Expanded from 28 to 40 lines. Added: mandatory session start protocol (read yesterday's notes, check tasks, verify MEMORY.md), content routing table (what goes where), context management guidelines.
- **`/tasks` skill** — Added: LEARNINGS.md read instruction, blocked tasks query, next_id from config table, counts summary.
- **`/reflect` skill** — Improved contradiction scanning (wiki-linked files, shared tags), better rejection tracking (skip notes, promotion on 2nd contradiction), updated routing table for new rules (communication.md, security.md, research.md).
- **CLAUDE.md template** — Added `/bootstrap` and `/create-skill` to Available Skills section.
- **README** — Updated directory structure, added Rules System section, added `/bootstrap` and `/create-skill` to features table, updated customization section.
- **setup.sh** — Copies new skills (bootstrap, create-skill with scripts), new rules (communication, security, research). Updated output listing.

### Removed

- **`workflow.md` rule** — Replaced by `security.md` (git discipline) and `communication.md` (verification rules).
- **`handoff.md` rule** — Replaced by delegation.md patterns and agent definitions. The structured handoff format was rarely used in practice.

### Files

- 3 new rules: `rules/communication.md`, `rules/security.md`, `rules/research.md`
- 1 new skill: `skills/bootstrap/` (SKILL.md, LEARNINGS.md)
- 1 new skill: `skills/create-skill/` (SKILL.md, LEARNINGS.md, scripts/init_skill.py, scripts/validate_skill.py)
- 2 removed rules: `rules/workflow.md`, `rules/handoff.md`
- Modified: `rules/tasks.md`, `rules/sessions.md`, `skills/tasks/SKILL.md`, `skills/reflect/SKILL.md`, `templates/CLAUDE.md`, `setup.sh`, `README.md`, `CHANGELOG.md`

## [1.1.1] - 2026-03-13

### Fixed

- **macOS `/tmp` symlink bug** — `global-guard.py` now resolves `/tmp`, `/var/tmp`, `/usr/local`, `/opt/homebrew` at load time. On macOS these are symlinks to `/private/...`; previously, resolved paths didn't match the unresolved roots, blocking all `/tmp` operations.
- **`setup.sh` name validation** — now requires at least 2 characters (previously accepted empty-ish single-char input)
- **`setup.sh` git staging** — replaced `git add -A` with explicit file list to avoid accidentally committing pre-existing files in `~/.claude/`
- **`state/backlog.md` committed on setup** — DB export now runs before git init, so the backlog file is included in the initial commit
- **Starter `MEMORY.md`** — setup now creates a minimal MEMORY.md with placeholder sections and file map. Previously, users who skipped `/onboard` had no MEMORY.md despite CLAUDE.md referencing it.

### Files

- Modified: `scripts/global-guard.py`, `setup.sh`, `CHANGELOG.md`

## [1.1.0] - 2026-03-13

### Added

- **Agent definitions** — 4 pre-built agents for delegating work via the Agent tool:
  - `code-reviewer` — reviews diffs for bugs, security issues, style violations, test gaps (read-only, Sonnet)
  - `bug-fixer` — investigates, reproduces, fixes bugs + writes regression tests (Opus)
  - `implementer` — implements features from a plan/spec in dependency order (Opus)
  - `researcher` — explores codebases, reads docs, searches web for technical answers (read-only, Sonnet)
- Agent definitions referenced in CLAUDE.md template and copied by setup.sh

### Changed

- README rewritten for clarity — opens with one-line description, ASCII flow diagram, addresses context bloat concern upfront, removed duplicate security section

### Files

- 4 new: `agents/code-reviewer.md`, `agents/bug-fixer.md`, `agents/implementer.md`, `agents/researcher.md`
- Modified: `README.md`, `setup.sh`, `templates/CLAUDE.md`, `CHANGELOG.md`

## [1.0.0] - 2026-03-12

First stable release.

### Features

- **Guided onboarding** (`/onboard`) — 5-step interview: profile, 12 problems, goals, tasks, AI identity. Survives disconnects via YAML checkpoint.
- **Session persistence** — pre-compact hook saves state before context compression. Custom compaction prompt. Session save reminder after 10 minutes.
- **Security guard** (`global-guard.py`) — blocks secrets access, force-push, writes outside `$HOME`, `rm -rf`. Runs on every tool call via PreToolUse hook.
- **Task system** (`/tasks`) — SQLite-backed task management. Priority scoring against 12 problems. Auto-export to markdown backlog.
- **Knowledge system** — structured `knowledge/` directory. Claude reads files on demand, not all at startup. CLAUDE.md acts as an index.
- **Plan and implement** (`/plan`) — 6-phase gated workflow: explore, tool discovery, design, approve, implement, verify.
- **Reflection loop** (`/reflect`) — extracts corrections and preferences from session JSONL. Routes to correct files. Tracks rule health via feedback counters.
- **Delegation rules** — subagent orchestration with authority boundaries, dual-write knowledge flow, quality control.
- **Development standards** — code quality limits (100 lines/fn, complexity 8), testing philosophy, commit conventions.
- **Agent handoff protocol** — structured format for chaining subagents.
- **Status line** — two-line display: model, folder, branch, context usage bar, cost, duration, cache %.
- **Setup script** — detects OS, checks dependencies, copies files, personalizes CLAUDE.md.

### Files

- 4 skills: `/onboard`, `/tasks`, `/plan`, `/reflect`
- 6 rules: sessions, workflow, tasks, delegation, development, handoff
- 5 scripts: global-guard.py, db.py, extract-learnings.py, pre-compact.sh, session-save-reminder.sh
- 3 templates: CLAUDE.md, settings.json, gitignore

[3.0.0]: https://github.com/mp-web3/claude-starter-kit/compare/v2.1.0...v3.0.0
[2.1.0]: https://github.com/mp-web3/claude-starter-kit/compare/v2.0.0...v2.1.0
[2.0.0]: https://github.com/mp-web3/claude-starter-kit/compare/v1.1.1...v2.0.0
[1.1.1]: https://github.com/mp-web3/claude-starter-kit/releases/tag/v1.1.1
[1.1.0]: https://github.com/mp-web3/claude-starter-kit/releases/tag/v1.1.0
[1.0.0]: https://github.com/mp-web3/claude-starter-kit/releases/tag/v1.0.0

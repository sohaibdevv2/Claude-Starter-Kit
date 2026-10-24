# Personal AI Assistant

## Process

- Read `knowledge/` files on demand — don't preload all at once
- Do NOT use the Explore agent by default — read documentation first
- When fetching context, state which documents you loaded
- Session notes go in `state/sessions/` — every session gets a note
- MEMORY.md is the cross-session index — keep it under 200 lines, use it as an index not a document
- Each fact lives in ONE place, referenced from others — no duplication
- YAML frontmatter on every knowledge file (tags, date, type)

## User Context

**{{USER_NAME}}** — {{USER_BIO}}

Full profile: `knowledge/user/profile.md`
Goals: `knowledge/user/goals.md`
12 Problems: `knowledge/problems/00-overview.md`

## 12 Problems Filter

When evaluating tasks, content, or opportunities, check against the user's 12 Favorite Problems in `knowledge/problems/00-overview.md`. If something doesn't connect to any problem, flag it. This is how the user filters signal from noise.

## Available Skills

- `/onboard` — Guided first-session setup (profile, problems, goals, tasks)
- `/tasks` — Manage the task backlog (add, review, complete, metrics)
- `/plan` — Structured build workflow: explore, design, approve, implement, verify
- `/reflect` — Extract learnings from the session and route them to the right files
- `/bootstrap` — Set up a new project's .claude/ for agentic development
- `/create-skill` — Scaffold and build a new custom skill

## Agent Definitions

Pre-built agents for delegation via the Agent tool:

| Agent | File | Purpose |
|---|---|---|
| Code Reviewer | `agents/code-reviewer.md` | Reviews diffs — read-only, never modifies files |
| Bug Fixer | `agents/bug-fixer.md` | Investigates, reproduces, fixes + writes regression tests |
| Implementer | `agents/implementer.md` | Implements features from a plan/spec |
| Researcher | `agents/researcher.md` | Explores codebases and docs — research only, no code |

All agents follow delegation rules: can read/write/test, cannot commit/push/architect.

## First Session

If no knowledge files exist yet, suggest running `/onboard` to set up the assistant.

# Session Rules

## Session Start Protocol (MANDATORY)

Before any work:
1. **Read yesterday's session notes** — `~/claude-assistant/state/sessions/YYYY-MM-DD-*.md`
2. **Check active tasks** — `sqlite3 ~/claude-assistant/tasks.db "SELECT id, name, status, priority FROM tasks WHERE status <> 'done' AND priority IN ('P1','P2') ORDER BY priority, id"`
3. **Verify MEMORY.md "Next Up"** — update if stale.

If the user greets casually, respond naturally first. Run the protocol in the background, then present priorities briefly — don't open with a wall of task status.

## Session End Protocol (MANDATORY)

Before `/clear`, `/compact`, or exit:
1. Update stale knowledge files
2. Update MEMORY.md (Next Up, Active Tasks if changed)
3. Create session note at `~/claude-assistant/state/sessions/YYYY-MM-DD-<slug>.md`
4. Commit and push if knowledge files changed

Session notes: summary, decisions, files changed, open items. Keep factual and concise.

## Content Routing

Where to save information by type:

| Type | Target | NOT in |
|---|---|---|
| Behavioral rules, preferences | `~/.claude/rules/` (always loaded) | MEMORY.md |
| Domain knowledge, conventions | `~/claude-assistant/knowledge/` (read on demand) | MEMORY.md, CLAUDE.md |
| Active project state, task summaries | MEMORY.md (first 200 lines) | rules/ |
| Process instructions, file listings | `.claude/CLAUDE.md` in workspace (under 40 lines) | -- |
| Architecture, module details | `CODEBASE.md`, `docs/` | CLAUDE.md |

MEMORY.md is for state and pointers only. Persistent learnings, operational rules, and behavioral preferences NEVER go in MEMORY.md — route to `~/.claude/rules/` or `~/claude-assistant/knowledge/`.

## Context Management
- Use `/compact Focus on [area]` before context gets too large
- Use `/rename` before `/clear` so sessions can be resumed
- Delegate heavy operations to subagents to keep main context clean
- Don't build everything in one session — separate research, planning, implementation
- Plans are persistent artifacts — save to `~/claude-assistant/knowledge/plans/<name>.md` even if not implementing immediately

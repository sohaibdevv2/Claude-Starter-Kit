---
name: tasks
description: Manage the task backlog — add, review, complete, and measure tasks against the 12 Favorite Problems. Run /tasks to see current status.
allowed-tools: Read, Grep, Glob, Write, Edit, Bash, AskUserQuestion
argument-hint: "[status | add <description> | review | done T### | metrics]"
---

# /tasks — Task Management (SQLite-backed)

**First:** Read `LEARNINGS.md` (in this skill's directory) before proceeding.

Primary store: `tasks.db` (in workspace root). Markdown export at `state/backlog.md` (read-only, regenerated on changes).

**Arguments:** `$ARGUMENTS`

---

## Routing

| Input | Action |
|---|---|
| (empty) or `status` | Show Status |
| `add <description>` | Add Task |
| `review` | Review & Reprioritize |
| `done T###` | Complete Task |
| `metrics` | Show Metrics |

---

## Show Status

```bash
# Active tasks sorted by priority
sqlite3 ~/claude-assistant/tasks.db -header -column \
  "SELECT id, name, priority, status, effort, problems FROM tasks WHERE status != 'done' ORDER BY CASE priority WHEN 'P1' THEN 1 WHEN 'P2' THEN 2 WHEN 'P3' THEN 3 ELSE 4 END, id"

# Blocked tasks
sqlite3 ~/claude-assistant/tasks.db -header -column \
  "SELECT id, name, blocked_by, blocked_reason FROM tasks WHERE blocked_by IS NOT NULL AND status != 'done'"

# Counts
sqlite3 ~/claude-assistant/tasks.db \
  "SELECT (SELECT COUNT(*) FROM tasks WHERE status NOT IN ('done')) AS active, (SELECT COUNT(*) FROM tasks WHERE status='done') AS completed, (SELECT COUNT(*) FROM tasks WHERE blocked_by IS NOT NULL AND status != 'done') AS blocked"
```

Flag:
- Any P1 task not `in_progress` -- prompt to start it
- Any task `in_progress` for 7+ days (check updated_at) -- suggest reviewing

---

## Add Task

1. Parse `<description>` from arguments
2. Get next ID: `sqlite3 ~/claude-assistant/tasks.db "SELECT value FROM config WHERE key='next_id'"`
3. Read `knowledge/problems/00-overview.md` to know the user's problems
4. Ask: which problems (by number) does this relate to? Effort (S/M/L)? Which subgoal?
5. Evaluate priority:
   - Problems >= 3 -- strong P1 candidate
   - Problems >= 2 + urgency -- P2
   - Problems == 1 or no urgency -- P3
   - Problems == 0 -- flag: "Is this drift?"
6. On approval, insert via sqlite3:

```bash
sqlite3 ~/claude-assistant/tasks.db "INSERT INTO tasks (id, name, priority, problems, effort, status, subgoal, created_at, updated_at) VALUES ('T###', 'Name', 'P2', '1,4', 'M', 'pending', 'S1', '$(date +%Y-%m-%d)', '$(date -u +%Y-%m-%dT%H:%M:%SZ)')"
```

7. Increment next_id: `sqlite3 ~/claude-assistant/tasks.db "UPDATE config SET value='T###' WHERE key='next_id'"`
8. Re-export: `python3 ~/claude-assistant/scripts/db.py export`

---

## Review & Reprioritize

1. Show all active tasks
2. Read `knowledge/problems/00-overview.md` and `knowledge/user/goals.md`
3. For each task: priority still correct? Stale? Blocking others? Connected to active subgoal?
4. Present proposed changes: `| ID | Current P | Proposed P | Reason |`
5. On approval, update and re-export

---

## Complete Task

1. Parse task ID
2. Update:

```bash
sqlite3 ~/claude-assistant/tasks.db "UPDATE tasks SET status='done', completed_at='$(date +%Y-%m-%d)', updated_at='$(date -u +%Y-%m-%dT%H:%M:%SZ)' WHERE id='T###'"
```

3. Re-export: `python3 ~/claude-assistant/scripts/db.py export`
4. Show: task name, problems addressed, days from created to done
5. Suggest next task based on priority

---

## Show Metrics

```bash
# Completed this week
sqlite3 ~/claude-assistant/tasks.db "SELECT COUNT(*) as done_this_week FROM tasks WHERE status='done' AND completed_at >= date('now', '-7 days')"

# Active count by priority
sqlite3 ~/claude-assistant/tasks.db "SELECT priority, COUNT(*) as count FROM tasks WHERE status != 'done' GROUP BY priority ORDER BY priority"

# Average days to complete
sqlite3 ~/claude-assistant/tasks.db "SELECT ROUND(AVG(julianday(completed_at) - julianday(created_at)), 1) as avg_days FROM tasks WHERE status='done' AND completed_at IS NOT NULL"
```

---

## Task Conventions

- **IDs:** `T` + 3-digit counter (T001, T002, ...), monotonic, never reused
- **Priority:** P1 (now), P2 (this week), P3 (this month), BL (backlog)
- **Effort:** S (< 1 session), M (2-3 sessions), L (4+ sessions)
- **Status:** pending, in_progress, done, blocked
- **Problems:** comma-separated numbers referencing the user's 12 problems
- **Subgoal:** S1, S2, etc. from goals.md

## Before Substantive Work

When the user requests work that will take more than ~5 minutes:
1. Check active tasks -- does this map to one?
2. If NO -- flag: "This doesn't map to an active task. Want to add it, or continue anyway?"
3. If the work touches zero problems -- flag: "This isn't connected to any of your problems. Proceed?"

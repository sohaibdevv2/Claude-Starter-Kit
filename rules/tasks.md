# Task Alignment Rules

## Source of Truth
- **SQLite** (`~/claude-assistant/tasks.db`) is the primary task store. ALL writes go through SQLite.
- **backlog.md** (`~/claude-assistant/state/backlog.md`) is a read-only export. NEVER edit it directly.
- After any SQLite write, re-export: `python3 ~/claude-assistant/scripts/db.py export`
- Use `/tasks` skill for all task operations (add, complete, review, metrics).

## Before Substantive Work
When the user requests work that will take more than ~5 minutes:

1. Check active tasks: `sqlite3 ~/claude-assistant/tasks.db "SELECT id, name, priority FROM tasks WHERE status <> 'done' ORDER BY priority, id"`
2. Does this work map to an active P1 or P2 task?
   - **YES** — proceed, reference the task ID in session notes
   - **NO** — flag: "This doesn't map to an active task. Want to add it to the backlog, or continue anyway?"
3. If the work touches **zero** problems (1-12) — explicit flag: "This isn't connected to any of your 12 problems. Proceed?"

## Research Requests
Research that seems like a "quick question" can become substantive (web searches, paper reading, note writing). If the topic doesn't connect to any of the 12 problems or active goals, flag it BEFORE starting: "This isn't connected to your active goals. How does it relate, or should I proceed anyway?"

## When NOT to Check
- Quick questions, lookups, debugging
- Tasks under ~5 minutes
- User says "just do it" or explicitly overrides
- System maintenance (git, cleanup, updates)

## Task Completion
- Never claim a task is done without verifying the output. "It's running" is not "it's done."
- If a task fails or blocks, fix it or provide an alternative immediately. Don't defer to a follow-up.
- For async/background tasks: either wait for completion or explicitly tell the user it's running and what to expect.
- Don't stop a session while background agents are running. Wait for results, synthesize, then save state.
- When building automation, include retry logic in the script itself. Never tell the user to manually retry a failed automated step.
- Verify means reading source or testing, not guessing. Deploy, test, confirm before reporting done.

## After Completing a Task
When substantive work on a task is finished:
1. Update SQLite: `sqlite3 ~/claude-assistant/tasks.db "UPDATE tasks SET status='done', completed_at='YYYY-MM-DD', updated_at=datetime('now') WHERE id='T###'"`
2. Re-export: `python3 ~/claude-assistant/scripts/db.py export`
3. Stage `backlog.md` in the next git commit — don't leave the export uncommitted
4. Update MEMORY.md Active Tasks table
5. Suggest the next task based on priority — don't wait for the user to ask

## Session End — Task Updates
Before session end, update tasks via SQLite:
- Change status of tasks worked on (`pending` to `in_progress`, or to `done`)
- Add completion date for finished tasks
- Add new tasks that emerged during the session
- Re-export: `python3 ~/claude-assistant/scripts/db.py export`

## Task Conventions
- **IDs:** `T` + 3-digit counter, monotonic, never reused
- **Priority:** `P1` (now), `P2` (this week), `P3` (this month), `BL` (backlog)
- **Effort:** `S` (<1 session), `M` (2-3 sessions), `L` (4+ sessions)
- **Status:** `pending`, `in_progress`, `done`, `blocked`
- **Problems:** comma-separated numbers 1-12 referencing the 12 Favorite Problems

## Operational
- **Bias toward action** — deliver outcomes, not explanations. Use tools, install missing ones, build what doesn't exist.
- **Finish the job** — handle visible edge cases, clean up what you touched, don't invent new scope.
- **Research before retrying** — after 2-3 failures, research properly before next attempt.
- **Research then implement** — on own code, implement after identifying the approach. Don't ask permission.
- **Priority drift guard** — flag P2/P3 exploration when P1 is unfinished.
- **When blocked** — try all tools first, then ask for the specific thing needed.

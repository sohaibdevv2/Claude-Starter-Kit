"""SQLite task and goal store for the personal AI assistant.

Schema: tasks, goals, config.
Primary store — backlog.md is a read-only markdown export for human reading.

Usage:
  python3 db.py init      — create tables (idempotent)
  python3 db.py export    — regenerate state/backlog.md from SQLite
"""

import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

DB_PATH = Path(__file__).resolve().parent.parent / "tasks.db"
BACKLOG_PATH = Path(__file__).resolve().parent.parent / "state" / "backlog.md"


def _get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def init_db() -> None:
    """Create tables if they don't exist. Idempotent."""
    conn = _get_conn()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS tasks (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            priority TEXT NOT NULL,
            problems TEXT,
            effort TEXT,
            status TEXT NOT NULL DEFAULT 'pending',
            context TEXT,
            created_at TEXT NOT NULL,
            completed_at TEXT,
            blocked_by TEXT,
            blocked_reason TEXT,
            notes TEXT,
            updated_at TEXT NOT NULL,
            subgoal TEXT,
            parent_id TEXT REFERENCES tasks(id)
        );

        CREATE TABLE IF NOT EXISTS goals (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            type TEXT NOT NULL CHECK(type IN ('end_goal', 'subgoal')),
            parent_id TEXT REFERENCES goals(id),
            description TEXT,
            done_when TEXT,
            status TEXT NOT NULL DEFAULT 'active',
            problems TEXT,
            order_num INTEGER,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS config (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        );

        CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
        CREATE INDEX IF NOT EXISTS idx_tasks_priority ON tasks(priority);
        CREATE INDEX IF NOT EXISTS idx_goals_type ON goals(type);
        CREATE INDEX IF NOT EXISTS idx_goals_parent ON goals(parent_id);
    """)
    # Initialize counter if not set
    existing = conn.execute("SELECT value FROM config WHERE key='next_id'").fetchone()
    if not existing:
        conn.execute("INSERT INTO config (key, value) VALUES ('next_id', 'T001')")
    conn.commit()
    conn.close()


# --- Config ---

def get_config(key: str, default: Optional[str] = None) -> Optional[str]:
    conn = _get_conn()
    row = conn.execute("SELECT value FROM config WHERE key=?", (key,)).fetchone()
    conn.close()
    return row["value"] if row else default


def set_config(key: str, value: str) -> None:
    conn = _get_conn()
    conn.execute(
        "INSERT INTO config (key, value) VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET value=?",
        (key, value, value),
    )
    conn.commit()
    conn.close()


# --- Tasks CRUD ---

def get_task(task_id: str) -> Optional[dict]:
    conn = _get_conn()
    row = conn.execute("SELECT * FROM tasks WHERE id=?", (task_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def list_tasks(status: Optional[str] = None, priority: Optional[str] = None) -> list[dict]:
    conn = _get_conn()
    query = "SELECT * FROM tasks WHERE 1=1"
    params: list = []
    if status:
        query += " AND status=?"
        params.append(status)
    if priority:
        query += " AND priority=?"
        params.append(priority)
    query += " ORDER BY CASE priority WHEN 'P1' THEN 1 WHEN 'P2' THEN 2 WHEN 'P3' THEN 3 ELSE 4 END, id"
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def active_tasks() -> list[dict]:
    conn = _get_conn()
    rows = conn.execute(
        "SELECT * FROM tasks WHERE status NOT IN ('done') "
        "ORDER BY CASE priority WHEN 'P1' THEN 1 WHEN 'P2' THEN 2 WHEN 'P3' THEN 3 ELSE 4 END, id"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def completed_tasks() -> list[dict]:
    conn = _get_conn()
    rows = conn.execute(
        "SELECT * FROM tasks WHERE status='done' ORDER BY completed_at DESC"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def add_task(
    task_id: str,
    name: str,
    priority: str,
    problems: str = "",
    effort: str = "",
    status: str = "pending",
    context: str = "",
    created_at: Optional[str] = None,
    notes: str = "",
    blocked_by: Optional[str] = None,
    blocked_reason: Optional[str] = None,
    subgoal: Optional[str] = None,
    parent_id: Optional[str] = None,
) -> None:
    now = _now()
    conn = _get_conn()
    conn.execute(
        """INSERT INTO tasks (id, name, priority, problems, effort, status, context,
           created_at, blocked_by, blocked_reason, notes, updated_at, subgoal, parent_id)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (task_id, name, priority, problems, effort, status, context,
         created_at or now, blocked_by, blocked_reason, notes, now, subgoal, parent_id),
    )
    conn.commit()
    conn.close()


def update_task(task_id: str, **kwargs) -> None:
    if not kwargs:
        return
    kwargs["updated_at"] = _now()
    sets = ", ".join(f"{k}=?" for k in kwargs)
    vals = list(kwargs.values()) + [task_id]
    conn = _get_conn()
    conn.execute(f"UPDATE tasks SET {sets} WHERE id=?", vals)
    conn.commit()
    conn.close()


def complete_task(task_id: str, completed_at: Optional[str] = None) -> None:
    update_task(task_id, status="done", completed_at=completed_at or datetime.now().strftime("%Y-%m-%d"))


def next_task_id() -> str:
    """Get and increment the task counter."""
    conn = _get_conn()
    row = conn.execute("SELECT value FROM config WHERE key='next_id'").fetchone()
    current = row["value"] if row else "T001"
    num = int(current[1:])
    next_val = f"T{num + 1:03d}"
    conn.execute(
        "INSERT INTO config (key, value) VALUES ('next_id', ?) ON CONFLICT(key) DO UPDATE SET value=?",
        (next_val, next_val),
    )
    conn.commit()
    conn.close()
    return current


# --- Goals ---

def list_goals(goal_type: Optional[str] = None) -> list[dict]:
    conn = _get_conn()
    query = "SELECT * FROM goals WHERE 1=1"
    params: list = []
    if goal_type:
        query += " AND type=?"
        params.append(goal_type)
    query += " ORDER BY order_num"
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def add_goal(
    goal_id: str,
    name: str,
    goal_type: str,
    parent_id: Optional[str] = None,
    description: str = "",
    done_when: str = "",
    problems: str = "",
    order_num: int = 0,
) -> None:
    now = _now()
    conn = _get_conn()
    conn.execute(
        """INSERT INTO goals (id, name, type, parent_id, description, done_when,
           status, problems, order_num, created_at, updated_at)
           VALUES (?, ?, ?, ?, ?, ?, 'active', ?, ?, ?, ?)""",
        (goal_id, name, goal_type, parent_id, description, done_when,
         problems, order_num, now, now),
    )
    conn.commit()
    conn.close()


def update_goal(goal_id: str, **kwargs) -> None:
    if not kwargs:
        return
    kwargs["updated_at"] = _now()
    sets = ", ".join(f"{k}=?" for k in kwargs)
    vals = list(kwargs.values()) + [goal_id]
    conn = _get_conn()
    conn.execute(f"UPDATE goals SET {sets} WHERE id=?", vals)
    conn.commit()
    conn.close()


# --- Markdown Export ---

def export_markdown(output_path: Optional[Path] = None) -> str:
    """Generate backlog.md from SQLite."""
    path = output_path or BACKLOG_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    next_id = get_config("next_id", "T001")

    active = active_tasks()
    completed = completed_tasks()

    goals = list_goals()
    end_goals = [g for g in goals if g["type"] == "end_goal"]
    subgoals = [g for g in goals if g["type"] == "subgoal"]

    lines = [
        "---",
        "tags: [tasks, backlog]",
        f"last_reviewed: {datetime.now().strftime('%Y-%m-%d')}",
        f"next_id: {next_id}",
        "---",
        "",
        "# Task Backlog",
        "",
    ]

    # Goal hierarchy
    if end_goals:
        eg = end_goals[0]
        lines += [
            f"## End Goal: {eg['name']}",
            f"{eg['description'] or ''}",
            "",
        ]
        if subgoals:
            lines += [
                "### Subgoals",
                "",
                "| ID | Subgoal | Done When | Problems | Status |",
                "|----|---------|-----------|----------|--------|",
            ]
            for sg in subgoals:
                lines.append(
                    f"| {sg['id']} | {sg['name']} | {sg['done_when'] or ''} "
                    f"| {sg['problems'] or ''} | {sg['status']} |"
                )
            lines.append("")

    # Group active tasks by subgoal
    subgoal_ids = {sg["id"]: sg["name"] for sg in subgoals}
    grouped: dict[Optional[str], list[dict]] = {}
    for t in active:
        sg = t.get("subgoal")
        grouped.setdefault(sg, []).append(t)

    # Show subgoal groups first, then ungrouped
    for sg_id in list(subgoal_ids.keys()) + [None]:
        group = grouped.get(sg_id, [])
        if not group:
            continue

        if sg_id and sg_id in subgoal_ids:
            label = f"{sg_id} — {subgoal_ids[sg_id]}"
        elif sg_id:
            label = sg_id
        else:
            label = "Other"

        lines += [
            f"## {label}",
            "",
            "| ID | Task | P | Problems | Effort | Status | Created |",
            "|----|------|---|----------|--------|--------|---------|",
        ]

        for t in group:
            name = f"~~{t['name']}~~" if t["status"] == "done" else t["name"]
            lines.append(
                f"| {t['id']} | {name} | {t['priority']} | {t['problems'] or ''} "
                f"| {t['effort'] or ''} | {t['status']} | {t['created_at'][:10]} |"
            )
        lines.append("")

    if completed:
        lines += [
            "## Completed",
            "",
            "| ID | Task | Completed | Problems |",
            "|----|------|-----------|----------|",
        ]
        for t in completed[:20]:
            lines.append(
                f"| {t['id']} | {t['name']} | {t['completed_at'] or '?'} | {t['problems'] or ''} |"
            )
        lines.append("")

    content = "\n".join(lines)
    path.write_text(content)
    return content


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "init":
        init_db()
        print(f"Database initialized at {DB_PATH}")
    elif len(sys.argv) > 1 and sys.argv[1] == "export":
        export_markdown()
        print(f"Exported to {BACKLOG_PATH}")
    else:
        print("Usage: python3 db.py [init|export]")

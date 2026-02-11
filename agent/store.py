import sqlite3
from contextlib import contextmanager
from pathlib import Path

from agent.models import TaskRecord, TaskRequest, TaskStatus, TaskType

DB_PATH = Path("agent.db")


def init_db() -> None:
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_type TEXT NOT NULL,
                objective TEXT NOT NULL,
                risk_tags TEXT NOT NULL,
                requires_approval INTEGER NOT NULL,
                status TEXT NOT NULL,
                result TEXT
            )
            """
        )
        conn.commit()


@contextmanager
def _conn():
    conn = sqlite3.connect(DB_PATH)
    try:
        yield conn
    finally:
        conn.close()


def create_task(task: TaskRequest) -> TaskRecord:
    with _conn() as conn:
        cursor = conn.execute(
            "INSERT INTO tasks(task_type, objective, risk_tags, requires_approval, status, result) VALUES (?, ?, ?, ?, ?, ?)",
            (
                task.task_type.value,
                task.objective,
                ",".join(task.risk_tags),
                1 if task.requires_approval else 0,
                TaskStatus.queued.value,
                None,
            ),
        )
        conn.commit()
        task_id = cursor.lastrowid
    return get_task(task_id)


def get_task(task_id: int) -> TaskRecord:
    with _conn() as conn:
        row = conn.execute(
            "SELECT id, task_type, objective, risk_tags, requires_approval, status, result FROM tasks WHERE id = ?",
            (task_id,),
        ).fetchone()
    if not row:
        raise ValueError(f"Task {task_id} not found")
    return _to_record(row)


def list_tasks() -> list[TaskRecord]:
    with _conn() as conn:
        rows = conn.execute(
            "SELECT id, task_type, objective, risk_tags, requires_approval, status, result FROM tasks ORDER BY id DESC"
        ).fetchall()
    return [_to_record(row) for row in rows]


def next_queued_task() -> TaskRecord | None:
    with _conn() as conn:
        row = conn.execute(
            "SELECT id, task_type, objective, risk_tags, requires_approval, status, result FROM tasks WHERE status = ? ORDER BY id ASC LIMIT 1",
            (TaskStatus.queued.value,),
        ).fetchone()
    return _to_record(row) if row else None


def update_task(task_id: int, *, status: TaskStatus, result: str | None = None) -> TaskRecord:
    with _conn() as conn:
        conn.execute(
            "UPDATE tasks SET status = ?, result = ? WHERE id = ?",
            (status.value, result, task_id),
        )
        conn.commit()
    return get_task(task_id)


def _to_record(row: tuple) -> TaskRecord:
    risk = row[3].split(",") if row[3] else []
    return TaskRecord(
        id=row[0],
        task_type=TaskType(row[1]),
        objective=row[2],
        risk_tags=risk,
        requires_approval=bool(row[4]),
        status=TaskStatus(row[5]),
        result=row[6],
    )

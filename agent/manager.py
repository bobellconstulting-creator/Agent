from agent.models import TaskStatus
from agent.store import next_queued_task, update_task
from agent.workers import run_task


def run_once() -> dict:
    task = next_queued_task()
    if not task:
        return {"processed": False, "reason": "queue_empty"}

    if task.requires_approval:
        return {
            "processed": False,
            "reason": "approval_required",
            "task_id": task.id,
        }

    update_task(task.id, status=TaskStatus.running)
    try:
        result = run_task(task)
        update_task(task.id, status=TaskStatus.done, result=result)
        return {"processed": True, "task_id": task.id, "status": "done"}
    except Exception as exc:  # pragma: no cover
        update_task(task.id, status=TaskStatus.failed, result=str(exc))
        return {"processed": True, "task_id": task.id, "status": "failed"}

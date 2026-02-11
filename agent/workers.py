from agent.models import TaskRecord, TaskType


def run_task(task: TaskRecord) -> str:
    if task.task_type == TaskType.code:
        return f"Code worker analyzed objective: {task.objective}. Opened PR draft plan."
    if task.task_type == TaskType.research:
        return f"Research worker summarized objective: {task.objective}. Added source checklist."
    if task.task_type == TaskType.email:
        return f"Email worker drafted low-risk response for: {task.objective}."
    return f"Data worker organized records for: {task.objective}."

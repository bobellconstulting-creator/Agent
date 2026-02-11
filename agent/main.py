from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse

from agent.manager import run_once
from agent.models import TaskRequest, TelegramUpdate
from agent.policy import should_require_approval
from agent.store import create_task, get_task, init_db, list_tasks

app = FastAPI(title="BuckGrid Agent")


@app.on_event("startup")
def startup_event() -> None:
    init_db()


@app.get("/", response_class=HTMLResponse)
def root() -> str:
    return """
    <html>
      <head>
        <title>BuckGrid Agent</title>
        <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
        <style>
          body { font-family: Arial, sans-serif; max-width: 760px; margin: 40px auto; padding: 0 16px; }
          h1 { margin-bottom: 0.4rem; }
          code { background: #f3f3f3; padding: 2px 6px; border-radius: 6px; }
          .ok { color: #0a7a2f; font-weight: 600; }
        </style>
      </head>
      <body>
        <h1>BuckGrid Agent</h1>
        <p class=\"ok\">Service online.</p>
        <p>Use <code>/health</code> for checks, <code>/docs</code> for API docs, and <code>/webhook/telegram</code> for Telegram webhooks.</p>
      </body>
    </html>
    """


@app.get("/health")
def health() -> dict:
    return {"ok": True}


@app.post("/webhook/telegram")
def telegram_webhook(update: TelegramUpdate) -> dict:
    text = ""
    if update.message:
        text = str(update.message.get("text", "")).strip()

    if not text:
        return {"ok": True, "message": "no-op"}

    task = TaskRequest(task_type="research", objective=f"Telegram request: {text}", risk_tags=[])
    record = create_task(task)
    return {"ok": True, "queued_task_id": record.id}


@app.post("/tasks")
def create_task_endpoint(request: TaskRequest) -> dict:
    needs_approval = request.requires_approval or should_require_approval(request.risk_tags)
    normalized = request.model_copy(update={"requires_approval": needs_approval})
    record = create_task(normalized)
    return {"task": record.model_dump()}


@app.get("/tasks")
def list_tasks_endpoint() -> dict:
    return {"tasks": [task.model_dump() for task in list_tasks()]}


@app.get("/tasks/{task_id}")
def get_task_endpoint(task_id: int) -> dict:
    try:
        task = get_task(task_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {"task": task.model_dump()}


@app.post("/manager/run-once")
def manager_run_once_endpoint() -> dict:
    return run_once()

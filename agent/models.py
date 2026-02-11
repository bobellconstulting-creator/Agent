from enum import Enum
from pydantic import BaseModel, Field


class TaskType(str, Enum):
    code = "code"
    research = "research"
    email = "email"
    data = "data"


class TaskStatus(str, Enum):
    queued = "queued"
    running = "running"
    done = "done"
    failed = "failed"


class TaskRequest(BaseModel):
    task_type: TaskType
    objective: str = Field(min_length=3)
    risk_tags: list[str] = Field(default_factory=list)
    requires_approval: bool = False


class TaskRecord(TaskRequest):
    id: int
    status: TaskStatus
    result: str | None = None


class TelegramUpdate(BaseModel):
    update_id: int | None = None
    message: dict | None = None

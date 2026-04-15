from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class TaskCreateResponse(BaseModel):
    task_id: str
    status: str


class TaskRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    task_id: str
    file_id: int
    query: str
    status: str
    progress: int
    result: dict[str, Any] | None = None
    error: str | None = None
    created_at: datetime
    updated_at: datetime


class TaskProgressEvent(BaseModel):
    task_id: str
    status: str
    progress: int
    message: str | None = None

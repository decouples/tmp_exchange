"""Task orchestration: create OCR tasks, enqueue, publish progress."""
from __future__ import annotations

import json

import redis.asyncio as aioredis
from arq import ArqRedis
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.file import file_crud
from app.crud.ocr_record import ocr_crud
from app.models.ocr_record import OCRRecord
from app.schemas.task import TaskProgressEvent
from app.services.file_service import new_task_id

PROGRESS_CHANNEL = "task-progress"


async def create_ocr_task(
    db: AsyncSession,
    *,
    arq: ArqRedis,
    owner_id: int,
    file_id: int,
    query: str,
    priority: str = "default",
) -> OCRRecord:
    file = await file_crud.get(db, file_id)
    if not file or file.owner_id != owner_id:
        raise ValueError("File not found")

    task_id = new_task_id()
    record = await ocr_crud.create(
        db,
        obj_in={
            "task_id": task_id,
            "owner_id": owner_id,
            "file_id": file_id,
            "query": query,
            "status": "QUEUED",
            "progress": 0,
        },
    )
    queue_name = {"high": "arq:high", "batch": "arq:batch"}.get(priority, "arq:queue")
    await arq.enqueue_job(
        "run_ocr", task_id=task_id, _queue_name=queue_name,
    )
    return record


async def publish_progress(
    redis: aioredis.Redis, event: TaskProgressEvent
) -> None:
    await redis.publish(
        f"{PROGRESS_CHANNEL}:{event.task_id}",
        event.model_dump_json(),
    )


async def subscribe_progress(redis: aioredis.Redis, task_id: str):
    pubsub = redis.pubsub()
    await pubsub.subscribe(f"{PROGRESS_CHANNEL}:{task_id}")
    try:
        async for msg in pubsub.listen():
            if msg.get("type") != "message":
                continue
            yield json.loads(msg["data"])
    finally:
        await pubsub.unsubscribe(f"{PROGRESS_CHANNEL}:{task_id}")
        await pubsub.close()

"""WebSocket endpoint for real-time task progress.

Clients connect to `/ws/tasks/{task_id}?token=<jwt>` and receive JSON progress
events published by workers on the Redis pub/sub channel.
"""
from __future__ import annotations

import asyncio
import json

from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect, status

from app.core.security import decode_token
from app.crud.ocr_record import ocr_crud
from app.db.session import SessionLocal
from app.services.task_service import PROGRESS_CHANNEL

router = APIRouter()


@router.websocket("/ws/tasks/{task_id}")
async def ws_task(
    websocket: WebSocket,
    task_id: str,
    token: str | None = Query(None),
) -> None:
    if not token:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return
    try:
        payload = decode_token(token)
        user_id = int(payload["sub"])
    except Exception:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    async with SessionLocal() as db:
        rec = await ocr_crud.get_by_task_id(db, task_id=task_id)
        if rec is None or rec.owner_id != user_id:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return
        snapshot = {
            "task_id": rec.task_id,
            "status": rec.status,
            "progress": rec.progress,
            "message": "snapshot",
        }

    await websocket.accept()
    await websocket.send_json(snapshot)

    redis = websocket.app.state.redis
    pubsub = redis.pubsub()
    await pubsub.subscribe(f"{PROGRESS_CHANNEL}:{task_id}")

    async def pump() -> None:
        async for msg in pubsub.listen():
            if msg.get("type") != "message":
                continue
            try:
                data = json.loads(msg["data"])
            except json.JSONDecodeError:
                continue
            await websocket.send_json(data)
            if data.get("status") in ("SUCCESS", "FAILED", "CANCELLED"):
                return

    try:
        await asyncio.wait_for(pump(), timeout=60 * 30)
    except (WebSocketDisconnect, asyncio.TimeoutError):
        pass
    finally:
        try:
            await pubsub.unsubscribe(f"{PROGRESS_CHANNEL}:{task_id}")
            await pubsub.close()
        except Exception:
            pass
        try:
            await websocket.close()
        except Exception:
            pass

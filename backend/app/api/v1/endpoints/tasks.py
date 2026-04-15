from fastapi import APIRouter, HTTPException, Query

from app.api.deps import DB, CurrentUser
from app.crud.ocr_record import ocr_crud
from app.schemas.task import TaskRead

router = APIRouter()


@router.get("", response_model=list[TaskRead])
async def list_tasks(
    db: DB,
    user: CurrentUser,
    status: str | None = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
) -> list[TaskRead]:
    recs = await ocr_crud.list_for_owner(
        db, owner_id=user.id, status=status, limit=limit, offset=offset,
    )
    return [TaskRead.model_validate(r) for r in recs]


@router.get("/{task_id}", response_model=TaskRead)
async def get_task(task_id: str, db: DB, user: CurrentUser) -> TaskRead:
    rec = await ocr_crud.get_by_task_id(db, task_id=task_id)
    if rec is None or rec.owner_id != user.id:
        raise HTTPException(status_code=404, detail="Task not found")
    return TaskRead.model_validate(rec)


@router.post("/{task_id}/cancel", response_model=TaskRead)
async def cancel_task(task_id: str, db: DB, user: CurrentUser) -> TaskRead:
    rec = await ocr_crud.get_by_task_id(db, task_id=task_id)
    if rec is None or rec.owner_id != user.id:
        raise HTTPException(status_code=404, detail="Task not found")
    if rec.status in ("SUCCESS", "FAILED", "CANCELLED"):
        return TaskRead.model_validate(rec)
    updated = await ocr_crud.update_status(
        db, task_id=task_id, status="CANCELLED", progress=100,
    )
    return TaskRead.model_validate(updated)

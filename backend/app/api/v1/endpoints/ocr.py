from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.api.deps import DB, Arq, CurrentUser, Quota
from app.schemas.ocr import OCRRequest
from app.schemas.task import TaskCreateResponse
from app.services.file_service import FileValidationError, save_upload
from app.services.task_service import create_ocr_task

router = APIRouter()


@router.post("", response_model=TaskCreateResponse)
async def submit_ocr(
    db: DB,
    arq: Arq,
    quota: Quota,
    user: CurrentUser,
    payload: OCRRequest,
) -> TaskCreateResponse:
    await quota.check_and_incr(user.id)
    try:
        rec = await create_ocr_task(
            db, arq=arq, owner_id=user.id,
            file_id=payload.file_id, query=payload.query, priority=payload.priority,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return TaskCreateResponse(task_id=rec.task_id, status=rec.status)


@router.post("/upload", response_model=TaskCreateResponse)
async def upload_and_submit(
    db: DB,
    arq: Arq,
    quota: Quota,
    user: CurrentUser,
    query: str = Form(...),
    priority: str = Form("default"),
    file: UploadFile = File(...),
) -> TaskCreateResponse:
    """Combined upload + enqueue in one multipart call."""
    await quota.check_and_incr(user.id)
    data = await file.read()
    try:
        saved = await save_upload(
            db,
            owner_id=user.id,
            filename=file.filename or "upload.bin",
            content_type=file.content_type or "application/octet-stream",
            data=data,
        )
    except FileValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))

    rec = await create_ocr_task(
        db, arq=arq, owner_id=user.id,
        file_id=saved.id, query=query, priority=priority,
    )
    return TaskCreateResponse(task_id=rec.task_id, status=rec.status)

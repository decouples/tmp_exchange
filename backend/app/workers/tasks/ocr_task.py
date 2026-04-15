"""Arq task: run OCR for a single OCRRecord."""
from __future__ import annotations

from app.core.logging import get_logger
from app.crud.file import file_crud
from app.crud.ocr_record import ocr_crud
from app.db.session import SessionLocal
from app.schemas.task import TaskProgressEvent
from app.services.file_service import read_file_bytes
from app.services.ocr_service import run_pdf, run_single_image
from app.services.task_service import publish_progress

log = get_logger(__name__)


async def run_ocr(ctx: dict, *, task_id: str) -> dict:
    redis = ctx["redis"]

    async def notify(status: str, progress: int, message: str | None = None):
        await publish_progress(
            redis,
            TaskProgressEvent(
                task_id=task_id, status=status, progress=progress, message=message
            ),
        )

    async with SessionLocal() as db:
        rec = await ocr_crud.get_by_task_id(db, task_id=task_id)
        if rec is None:
            log.warning("OCR task %s not found", task_id)
            return {"ok": False, "error": "not_found"}

        await ocr_crud.update_status(db, task_id=task_id, status="PROCESSING", progress=5)
        await notify("PROCESSING", 5, "Loading file")

        file = await file_crud.get(db, rec.file_id)
        if file is None:
            await ocr_crud.update_status(
                db, task_id=task_id, status="FAILED", error="File missing"
            )
            await notify("FAILED", 100, "File missing")
            return {"ok": False}

        try:
            data = await read_file_bytes(file)
            await notify("PROCESSING", 25, "Running VLM")

            if file.content_type == "application/pdf":
                result = run_pdf(pdf_bytes=data, query=rec.query)
            else:
                result = run_single_image(image_png=data, query=rec.query)

            await ocr_crud.update_status(
                db,
                task_id=task_id,
                status="SUCCESS",
                progress=100,
                result=result.model_dump(mode="json"),
            )
            await notify("SUCCESS", 100, f"{len(result.matches)} matches")
            return {"ok": True, "matches": len(result.matches)}
        except Exception as e:
            log.exception("OCR task %s failed", task_id)
            await ocr_crud.update_status(
                db, task_id=task_id, status="FAILED", progress=100, error=str(e)
            )
            await notify("FAILED", 100, str(e))
            return {"ok": False, "error": str(e)}

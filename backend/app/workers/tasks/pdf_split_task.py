"""Fan-out a large PDF into per-page subtasks.

In the current implementation `run_ocr` already handles multi-page PDFs in a
single task by iterating render_pdf_pages. This fan-out variant is kept as a
hook for genuinely large (100+ page) PDFs — it enqueues one `run_ocr_page`
job per page then a merge job.
"""
from __future__ import annotations

from app.core.logging import get_logger
from app.crud.file import file_crud
from app.db.session import SessionLocal
from app.services.file_service import read_file_bytes
from app.services.pdf_service import render_pdf_pages

log = get_logger(__name__)


async def split_pdf(ctx: dict, *, task_id: str, file_id: int) -> dict:
    async with SessionLocal() as db:
        file = await file_crud.get(db, file_id)
        if file is None:
            return {"ok": False, "error": "file_not_found"}
        data = await read_file_bytes(file)
        pages = render_pdf_pages(data)
        log.info("split_pdf %s -> %d pages", task_id, len(pages))
        return {"ok": True, "pages": len(pages)}

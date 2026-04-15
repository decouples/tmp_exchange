"""Merge per-page OCR subtask results."""
from __future__ import annotations

from app.crud.ocr_record import ocr_crud
from app.db.session import SessionLocal


async def merge_results(ctx: dict, *, task_id: str, partials: list[dict]) -> dict:
    merged: list[dict] = []
    for p in partials:
        merged.extend(p.get("matches", []))
    async with SessionLocal() as db:
        await ocr_crud.update_status(
            db, task_id=task_id, status="SUCCESS", progress=100,
            result={"matches": merged, "engine": "merged"},
        )
    return {"ok": True, "merged": len(merged)}

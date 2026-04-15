from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.ocr_record import OCRRecord


class CRUDOCRRecord(CRUDBase[OCRRecord]):
    async def get_by_task_id(self, db: AsyncSession, *, task_id: str) -> OCRRecord | None:
        stmt = select(OCRRecord).where(OCRRecord.task_id == task_id)
        return (await db.execute(stmt)).scalar_one_or_none()

    async def list_for_owner(
        self, db: AsyncSession, *, owner_id: int, status: str | None = None,
        limit: int = 50, offset: int = 0,
    ) -> list[OCRRecord]:
        stmt = select(OCRRecord).where(OCRRecord.owner_id == owner_id)
        if status:
            stmt = stmt.where(OCRRecord.status == status)
        stmt = stmt.order_by(OCRRecord.id.desc()).limit(limit).offset(offset)
        return list((await db.execute(stmt)).scalars().all())

    async def update_status(
        self, db: AsyncSession, *, task_id: str, status: str,
        progress: int | None = None, result: dict | None = None, error: str | None = None,
    ) -> OCRRecord | None:
        rec = await self.get_by_task_id(db, task_id=task_id)
        if not rec:
            return None
        rec.status = status
        if progress is not None:
            rec.progress = progress
        if result is not None:
            rec.result = result
        if error is not None:
            rec.error = error
        await db.commit()
        await db.refresh(rec)
        return rec


ocr_crud = CRUDOCRRecord(OCRRecord)

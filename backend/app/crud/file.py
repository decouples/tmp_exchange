from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.file import File


class CRUDFile(CRUDBase[File]):
    async def get_by_md5(self, db: AsyncSession, *, owner_id: int, md5: str) -> File | None:
        stmt = select(File).where(File.owner_id == owner_id, File.md5 == md5)
        return (await db.execute(stmt)).scalar_one_or_none()

    async def list_for_owner(self, db: AsyncSession, *, owner_id: int) -> list[File]:
        stmt = select(File).where(File.owner_id == owner_id).order_by(File.id.desc())
        return list((await db.execute(stmt)).scalars().all())


file_crud = CRUDFile(File)

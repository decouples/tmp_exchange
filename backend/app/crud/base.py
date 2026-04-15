from typing import Any, Generic, TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.base import Base

ModelT = TypeVar("ModelT", bound=Base)


class CRUDBase(Generic[ModelT]):
    def __init__(self, model: type[ModelT]):
        self.model = model

    async def get(self, db: AsyncSession, id: Any) -> ModelT | None:
        return await db.get(self.model, id)

    async def list(self, db: AsyncSession, *, limit: int = 50, offset: int = 0) -> list[ModelT]:
        stmt = select(self.model).limit(limit).offset(offset).order_by(self.model.id.desc())
        return list((await db.execute(stmt)).scalars().all())

    async def create(self, db: AsyncSession, *, obj_in: dict[str, Any]) -> ModelT:
        obj = self.model(**obj_in)
        db.add(obj)
        await db.commit()
        await db.refresh(obj)
        return obj

    async def delete(self, db: AsyncSession, *, id: Any) -> None:
        obj = await self.get(db, id)
        if obj is not None:
            await db.delete(obj)
            await db.commit()

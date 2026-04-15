from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.logging import get_logger
from app.core.security import hash_password
from app.db.base import Base  # noqa: F401 — ensures models registered
from app.db.session import engine
from app.models.user import User

log = get_logger(__name__)


async def create_all() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def seed_demo_user(session: AsyncSession) -> User:
    stmt = select(User).where(User.email == settings.demo_user_email)
    existing = (await session.execute(stmt)).scalar_one_or_none()
    if existing:
        return existing
    user = User(
        email=settings.demo_user_email,
        name=settings.demo_user_name,
        hashed_password=hash_password(settings.demo_user_password),
        is_active=True,
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    log.info("Seeded demo user: %s", user.email)
    return user

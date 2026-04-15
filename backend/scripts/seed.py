"""Manual DB bootstrap: create tables + seed demo user."""
import asyncio

from app.db.init_db import create_all, seed_demo_user
from app.db.session import SessionLocal


async def main() -> None:
    await create_all()
    async with SessionLocal() as db:
        user = await seed_demo_user(db)
        print(f"Demo user: {user.email} (id={user.id})")


if __name__ == "__main__":
    asyncio.run(main())

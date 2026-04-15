from __future__ import annotations

from typing import Annotated

import redis.asyncio as aioredis
from arq import ArqRedis, create_pool
from arq.connections import RedisSettings
from fastapi import Depends, Header, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import UnauthorizedError
from app.core.quota import QuotaManager
from app.core.security import decode_token
from app.db.session import get_db
from app.models.user import User


async def get_redis(request: Request) -> aioredis.Redis:
    return request.app.state.redis


async def get_arq(request: Request) -> ArqRedis:
    return request.app.state.arq


async def get_current_user(
    authorization: Annotated[str | None, Header()] = None,
    db: AsyncSession = Depends(get_db),
) -> User:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise UnauthorizedError("Missing bearer token")
    token = authorization.split(" ", 1)[1].strip()
    payload = decode_token(token)
    try:
        user_id = int(payload["sub"])
    except (KeyError, ValueError) as e:
        raise UnauthorizedError("Invalid token subject") from e
    user = await db.get(User, user_id)
    if user is None or not user.is_active:
        raise UnauthorizedError("User not found or inactive")
    return user


async def get_quota(
    redis: aioredis.Redis = Depends(get_redis),
) -> QuotaManager:
    return QuotaManager(redis)


CurrentUser = Annotated[User, Depends(get_current_user)]
DB = Annotated[AsyncSession, Depends(get_db)]
Redis = Annotated[aioredis.Redis, Depends(get_redis)]
Arq = Annotated[ArqRedis, Depends(get_arq)]
Quota = Annotated[QuotaManager, Depends(get_quota)]


async def create_arq_pool() -> ArqRedis:
    return await create_pool(RedisSettings.from_dsn(settings.redis_url))

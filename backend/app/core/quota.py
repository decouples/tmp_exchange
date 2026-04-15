from datetime import datetime, timezone

import redis.asyncio as aioredis

from app.core.config import settings
from app.core.exceptions import QuotaExceededError


class QuotaManager:
    def __init__(self, redis: aioredis.Redis):
        self.redis = redis

    @staticmethod
    def _key(user_id: int) -> str:
        today = datetime.now(timezone.utc).strftime("%Y%m%d")
        return f"quota:ocr:{user_id}:{today}"

    async def check_and_incr(self, user_id: int, cost: int = 1) -> int:
        key = self._key(user_id)
        pipe = self.redis.pipeline()
        pipe.incrby(key, cost)
        pipe.expire(key, 86400 * 2)
        used, _ = await pipe.execute()
        if used > settings.daily_ocr_quota:
            raise QuotaExceededError(
                f"Daily OCR quota ({settings.daily_ocr_quota}) exceeded"
            )
        return int(used)

    async def remaining(self, user_id: int) -> int:
        key = self._key(user_id)
        used = int(await self.redis.get(key) or 0)
        return max(0, settings.daily_ocr_quota - used)

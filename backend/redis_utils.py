"""Redis utility for caching and rate limiting."""

import redis.asyncio as redis
from config import settings

class RedisClient:
    def __init__(self):
        self.client = None

    def connect(self):
        self.client = redis.from_url(settings.redis_url, decode_responses=True)
        return self.client

    async def get_cache(self, key: str):
        if not self.client:
            self.connect()
        return await self.client.get(key)

    async def set_cache(self, key: str, value: str, expire: int = 3600):
        if not self.client:
            self.connect()
        await self.client.set(key, value, ex=expire)

    async def check_rate_limit(self, user_id: str, limit: int = 60, window: int = 60) -> bool:
        """Simple token bucket / counter based rate limit."""
        if not self.client:
            self.connect()
        key = f"rate_limit:{user_id}"
        count = await self.client.incr(key)
        if count == 1:
            await self.client.expire(key, window)
        
        return count <= limit

redis_client = RedisClient()

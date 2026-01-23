import redis.asyncio as redis
from settings import settings
import datetime as dt
from contextlib import asynccontextmanager

class RedisService:
    def __init__(self):
        self.redis = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            username=settings.REDIS_USER,
            password=settings.REDIS_PASSWORD,
            db=settings.REDIS_DATABASE,
            decode_responses=False,
        )
    
    @asynccontextmanager
    async def get_redis(self):
        try:
            yield self.redis
        finally:
            pass

    async def set_cache(self, key: str, value: str | int, ttl: int = 60):
        async with self.get_redis() as _redis:
            await _redis.setex(key, dt.timedelta(seconds=ttl), value)

    async def get_cache(self, key: str):
        async with self.get_redis() as _redis:
            return await _redis.get(key)

    async def delete_cache(self, key: str):
        async with self.get_redis() as _redis:
            await _redis.delete(key)


redis_service = RedisService()

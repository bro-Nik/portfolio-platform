from collections.abc import AsyncIterator

from redis.asyncio import Redis

from app.core.database import redis_client


async def get_redis() -> AsyncIterator[Redis]:
    async with redis_client.get_redis_session() as client:
        yield client

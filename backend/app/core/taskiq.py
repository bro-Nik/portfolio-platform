from taskiq_redis import RedisAsyncResultBackend, RedisStreamBroker

from app.core import settings

result_backend = RedisAsyncResultBackend(redis_url=settings.redis_url)
broker = RedisStreamBroker(url=settings.redis_url).with_result_backend(result_backend)

from dishka import make_async_container
from dishka.integrations.taskiq import setup_dishka
from taskiq import TaskiqScheduler
from taskiq_redis import RedisAsyncResultBackend, RedisStreamBroker

from app.core import settings
from app.modules.market.dependencies import AppProvider, TaskProvider
from app.modules.market.scheduler import DBScheduleSource

result_backend = RedisAsyncResultBackend(redis_url=settings.redis_url)
broker = RedisStreamBroker(url=settings.redis_url).with_result_backend(result_backend)

container = make_async_container(AppProvider(), TaskProvider())
setup_dishka(container=container, broker=broker)

db_source = DBScheduleSource()

scheduler = TaskiqScheduler(
    broker=broker,
    sources=[db_source],
)

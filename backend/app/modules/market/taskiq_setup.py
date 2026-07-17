from dishka import make_async_container
from dishka.integrations.taskiq import setup_dishka
from taskiq import TaskiqScheduler

from app.core.taskiq import broker
from app.modules.market.dependencies import AppProvider, TaskProvider
from app.modules.market.scheduler import DBScheduleSource

container = make_async_container(AppProvider(), TaskProvider())
setup_dishka(container=container, broker=broker)

db_source = DBScheduleSource()

scheduler = TaskiqScheduler(
    broker=broker,
    sources=[db_source],
)

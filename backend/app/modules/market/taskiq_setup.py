from dishka.integrations.taskiq import setup_dishka
from taskiq import TaskiqScheduler

from app.core.taskiq import broker
from app.di import build_worker_container
from app.modules.market.scheduler import DBScheduleSource
from app.modules.market.scheduler_system import SystemScheduleSource

container = build_worker_container()
setup_dishka(container=container, broker=broker)

db_source = DBScheduleSource()
system_source = SystemScheduleSource()

scheduler = TaskiqScheduler(
    broker=broker,
    sources=[db_source, system_source],
)

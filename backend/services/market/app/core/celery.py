from celery import Celery
from celery.schedules import crontab

from app.core.config import settings

celery = Celery(
    'portfolio_platform_market',
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=['app.tasks', 'app.tasks_sync'],
)

# Настройки Celery
celery.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,

    # RedBeat
    beat_scheduler='redbeat.RedBeatScheduler',
    beat_max_loop_interval=300,
    beat_schedule={},
    redbeat_redis_url=settings.redis_url,
    redbeat_key_prefix='redbeat:',

    # Logs
    worker_hijack_root_logger=False,
    beat_log_level='INFO',
    beat_dblog_interval=60,  # Логировать состояние каждые 60 секунд
)

# Задача для периодической синхронизации задач из БД
celery.conf.beat_schedule = {
    'sync-tasks-from-db': {
        'task': 'app.tasks_sync.sync_db_tasks',
        'schedule': crontab(minute='*/1'),  # Каждые 1 мин
        # 'schedule': crontab(minute='*/5'),  # Каждые 5 мин
    },
}

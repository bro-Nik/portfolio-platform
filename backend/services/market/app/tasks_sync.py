import logging

from app.dependencies import get_sync_db
from app.core.celery import celery
from app.repositories.sync_repo.api_task import ApiTaskRepository
from .services import task_sync as sync


logger = logging.getLogger(__name__)


@celery.task()
def sync_db_tasks():
    """Периодическая задача для синхронизации задач из БД"""
    try:
        with get_sync_db() as db:
            count = sync.sync_tasks_from_db(db)
            logger.info('Синхронизированно %s задач из БД', count)
            return {'status': 'success', 'tasks_synced': count}
    except Exception as e:
        logger.error('Ошибка в sync_db_tasks: %s', e)
        return {'status': 'error', 'message': str(e)}


@celery.task()
def activate_task(task_id: int):
    """Активирует задачу (добавляет в расписание)"""
    with get_sync_db() as db:
        success = sync.schedule_task_from_db(db, task_id)
    success = sync.remove_task_from_schedule(task_id)
    return {'status': 'success' if success else 'error', 'task_id': task_id}


@celery.task()
def deactivate_task(task_id: int):
    """Деактивирует задачу (удаляет из расписания)"""
    success = sync.remove_task_from_schedule(task_id)
    return {'status': 'success' if success else 'error', 'task_id': task_id}


@celery.task()
def update_task_schedule(task_id: int, new_schedule: str):
    """Обновляет расписание задачи"""
    with get_sync_db() as db:
        # Удаляем старую задачу из расписания
        sync.remove_task_from_schedule(task_id)

        # Обновляем в БД
        task_repo = ApiTaskRepository(db)
        task = task_repo.get_with_provider(task_id)
        if task:
            task.schedule = new_schedule
            task.next_run = sync.get_next_run_time(new_schedule)
            db.commit()

        # Добавляем с новым расписанием
        if task.is_active:
            sync.schedule_task_from_db(db, task_id)

        return {'status': 'success', 'task_id': task_id}

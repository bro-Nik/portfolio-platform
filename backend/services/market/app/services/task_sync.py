from datetime import datetime
import json
import logging

from celery import current_app
from celery.schedules import crontab
from redbeat.schedulers import RedBeatSchedulerEntry, get_redis
from shared.dependencies.db import sync_session
from sqlalchemy.orm import Session

from app.core.database import SyncSessionLocal
from app.repositories.sync_repo.api_task import ApiTaskRepository

logger = logging.getLogger(__name__)


def get_active_task(task_id):
    with sync_session(SyncSessionLocal) as db:
        task_repo = ApiTaskRepository(db)
        task = task_repo.get_with_provider(task_id)

        if not task:
            logger.debug('Задача не найдена в БД, id: %s', task_id)
            raise ValueError(f'Задача не найдена в БД, id: {task_id}')
        if not task.is_active:
            logger.debug('Задача не активна, id: %s', task_id)
            raise ValueError(f'Задача не активна в БД, id: {task_id}')

        return task


def get_task_key(id: str | int = ''):
    return f'db-task-{id}'


def get_redbeat_key(id: str = ''):
    return f'{current_app.conf.redbeat_key_prefix}{id}'


def parce_task_params(task):
    """Парсинг параметров задачи"""
    args = []
    kwargs = {}

    if task.parameters:
        try:
            params = json.loads(task.parameters) if isinstance(task.parameters, str) else task.parameters
            if isinstance(params, dict):
                kwargs = params
            elif isinstance(params, list):
                args = params
        except json.JSONDecodeError:
            logger.error('Неверный формат JSON в параметрах задачи %s', task.id)
        except Exception as e:
            logger.error('Ошибка парсинга параметров для задачи %s: %s', task.id, e)

    # Добавляем обязательные параметры
    kwargs['db_task_id'] = task.id
    kwargs['api_provider'] = task.api_provider.name
    kwargs['method'] = task.task_type

    return args, kwargs


def get_all_redbeat_entries():
    """Получает все записи RedBeat из Redis"""
    try:
        redis_client = get_redis(current_app)
        key_prefix = current_app.conf.redbeat_key_prefix

        # Получаем все ключи с префиксом
        pattern = f"{key_prefix}*"
        keys = redis_client.keys(pattern)

        entries = []
        for key in keys:
            # Ключи могут быть bytes или str
            if isinstance(key, bytes):
                key_str = key.decode('utf-8')
            else:
                key_str = str(key)

            # Пропускаем системные ключи
            if key_str.endswith(':schedule') or key_str.endswith(':index'):
                continue

            try:
                entry = RedBeatSchedulerEntry.from_key(key_str, app=current_app)
                entries.append(entry)
            except Exception as e:
                logger.debug(f'Не удалось загрузить запись {key_str}: {e}')

        return entries

    except Exception as e:
        logger.error('Ошибка при получении записей RedBeat: %s', e)
        return []


def parse_cron_schedule(schedule_str: str) -> crontab:
    """Парсим cron строку в объект crontab"""
    try:
        # Формат: minute hour day_of_month month day_of_week
        parts = schedule_str.strip().split()
        if len(parts) != 5:
            raise ValueError(f'Неверный формат cron: {schedule_str}')

        minute, hour, day_of_month, month, day_of_week = parts

        return crontab(
            minute=minute,
            hour=hour,
            day_of_month=day_of_month,
            month_of_year=month,
            day_of_week=day_of_week
        )
    except Exception as e:
        logger.error(f'Ошибка при разборе расписания cron {schedule_str}: {e}')
        # По умолчанию каждый час
        return crontab(minute='0', hour='*')


def sync_task(task, current_keys):
    task_key = get_task_key(task.id)
    redbeat_key = get_redbeat_key(task_key)

    task_func = "app.tasks.update_market_data"

    # Парсим параметры
    args, kwargs = parce_task_params(task)

    # Проверяем, существует ли уже такая задача
    if redbeat_key in current_keys:
        # Обновляем существующую
        entry = current_keys[redbeat_key]
        entry.schedule = parse_cron_schedule(task.schedule)
        entry.args = args
        entry.kwargs = kwargs
        entry.save()
        logger.debug('Обновлена задача %s в RedBeat', task.id)
    else:
        # Создаем новую
        entry = RedBeatSchedulerEntry(
            name=task_key,
            task=task_func,
            schedule=parse_cron_schedule(task.schedule),
            args=args,
            kwargs=kwargs,
            app=current_app,
        )
        entry.save()
        logger.debug('Создана задача %s в RedBeat', task.id)


def sync_tasks_from_db(db: Session):
    """Синхронизирует задачи из БД с Celery beat"""
    try:
        task_repo = ApiTaskRepository(db)
        tasks = task_repo.get_all_with_providers(only_active=True)

        # Получаем все текущие задачи из RedBeat
        current_entries = get_all_redbeat_entries()
        current_keys = {entry.key: entry for entry in current_entries}

        synced_count = 0

        for task in tasks:
            # Синхронизируем задачу
            sync_task(task, current_keys)

            synced_count += 1

        # Удаляем задачи, которых нет в БД
        task_redbeat_key_prefix = get_redbeat_key(get_task_key())
        for key, entry in current_keys.items():
            if task_redbeat_key_prefix in key:
                # Извлекаем ID задачи из ключа
                try:
                    task_id = int(key.split(task_redbeat_key_prefix)[1])
                    # Проверяем, существует ли задача в БД
                    task_exists = any(t.id == task_id for t in tasks)
                    if not task_exists:
                        entry.delete()
                        logger.debug('Удалена задача %s из RedBeat', task_id)
                except (ValueError, IndexError):
                    continue

        logger.info('Синхронизировано %s задач с RedBeat', synced_count)
        return synced_count

    except Exception as e:
        logger.error('Ошибка синхронизации задач из БД: %s', e)
        return 0


def schedule_task_from_db(task_id: int):
    """Добавляет конкретную задачу из БД в Celery beat"""
    try:
        task = get_active_task(task_id)

        # Получаем все текущие задачи из RedBeat
        current_entries = get_all_redbeat_entries()
        current_keys = {entry.key: entry for entry in current_entries}

        # Синхронизируем задачу
        sync_task(task, current_keys)

        logger.info('Запланирована задача %s из БД', task_id)

    except Exception as e:
        logger.error('Ошибка планирования задачи %s: %s', task_id, e)
        raise


def remove_task_from_schedule(task_id: int):
    """Удаляет задачу из расписания Celery beat"""
    try:
        task_key = get_task_key(task_id)

        if task_key in current_app.conf.beat_schedule:
            del current_app.conf.beat_schedule[task_key]
            logger.info('Задача %s удалена из расписания Celery beat', task_id)
            return True
        return False
    except Exception as e:
        logger.error('Ошибка удаления задачи %s: %s', task_id, e)
        return False


def run_task_now(task_id: int):
    """Немедленно запускает задачу из БД"""
    try:
        task = get_active_task(task_id)

        # Определяем функцию задачи
        from .. import tasks
        # task_func = getattr(tasks, task.task_type)
        task_func = tasks.update_market_data
        if not task_func:
            logger.info('Модуль задачи %s не найден', task.task_type)
            return

        # Парсим параметры
        args, kwargs = parce_task_params(task)

        # Запускаем задачу
        result = task_func.delay(*args, **kwargs)

        logger.info('Запущена задача %s', task_id)
        return result.id

    except Exception as e:
        logger.error('Ошибка запуска задачи %s: %s', task_id, e)
        return None


def get_next_run_time(schedule_str: str) -> datetime:
    """Вычисляет следующее время запуска по cron расписанию"""
    try:
        from celery.schedules import crontab
        import croniter
        from datetime import datetime

        cron = parse_cron_schedule(schedule_str)

        # Получаем cron строку из объекта
        cron_parts = [
            cron._orig_minute,
            cron._orig_hour,
            cron._orig_day_of_month,
            cron._orig_month_of_year,
            cron._orig_day_of_week
        ]
        cron_str = ' '.join(str(p) for p in cron_parts)

        # Используем croniter для вычисления следующего времени
        now = datetime.now()
        iter = croniter.croniter(cron_str, now)
        next_run = iter.get_next(datetime)

        return next_run
    except Exception as e:
        logger.error('Ошибка при вычислении времени следующего запуска: %s', e)
        return None

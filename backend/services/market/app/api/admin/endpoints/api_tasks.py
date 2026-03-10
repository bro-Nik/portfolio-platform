from fastapi import APIRouter
from shared.api import responses
from shared.exceptions import handle_errors

from app.dependencies import ApiTaskServiceDep
from app.schemas import (
    ApiTaskCreate,
    ApiTaskResponse,
    ApiTaskUpdate,
    TaskRunRequest,
    TaskScheduleRequest,
)
from app.services import task_sync

router = APIRouter(prefix='/tasks', tags=['Admin | ApiTasks'], responses=responses(401, 429, 500))


@router.get('/')
@handle_errors('Ошибка при получении задач')
async def get_tasks(
    task_service: ApiTaskServiceDep,
    skip: int = 0,
    limit: int | None = None,
) -> list[ApiTaskResponse]:
    """Получить список задач."""
    return await task_service.get_tasks(skip=skip, limit=limit)


@router.post('/', status_code=201, responses=responses(400, 409))
@handle_errors('Ошибка при создании задачи')
async def create_task(
    task_data: ApiTaskCreate,
    task_service: ApiTaskServiceDep,
) -> ApiTaskResponse:
    """Создать новую задачу."""
    return await task_service.create_task(task_data)


@router.put('/{task_id}', responses=responses(400, 404, 409))
@handle_errors('Ошибка при обновлении задачи')
async def update_task(
    task_id: int,
    task_data: ApiTaskUpdate,
    task_service: ApiTaskServiceDep,
) -> ApiTaskResponse:
    """Обновить задачу."""
    return await task_service.update_task(task_id, task_data)


@router.delete('/{task_id}', status_code=204, responses=responses(400, 404))
@handle_errors('Ошибка при удалении задачи')
async def delete_task(
    task_id: int,
    task_service: ApiTaskServiceDep,
) -> None:
    """Удалить задачу."""
    await task_service.delete_task(task_id)


@router.post('/run/')
def run_task(data: TaskRunRequest):
    """Запустить задачу вручную."""
    celery_task_id = task_sync.run_task_now(data.task_id)
    return {'task_id': celery_task_id, 'status': 'started'}


@router.post('/schedule/')
@handle_errors('Ошибка при попытке запланировать задачу')
def schedule_periodic_task(data: TaskScheduleRequest):
    """Запланировать периодическую задачу."""
    task_sync.schedule_task_from_db(data.task_id)
    return {'message': 'Задача запланирована'}

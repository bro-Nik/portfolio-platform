"""Управление задачами внешних API.

Все эндпоинты требуют валидный access token с ролью ADMIN
"""

from app.api.router import AppRouter
from app.dependencies import TaskServiceDep
from app.schemas import TaskCreateRequest, TaskResponse, TaskUpdateRequest
from shared.api import responses
from shared.exceptions import handle_errors

router = AppRouter(prefix='/tasks', tags=['Admin | ApiTasks'])


@router.get('/')
@handle_errors('Ошибка при получении задач')
async def get_tasks(
    task_service: TaskServiceDep,
) -> list[TaskResponse]:
    """Получить список задач."""
    return await task_service.get_all_with_providers()


@router.post('/', status_code=201, responses=responses(400, 409))
@handle_errors('Ошибка при создании задачи')
async def create_task(
    data: TaskCreateRequest,
    task_service: TaskServiceDep,
) -> TaskResponse:
    """Создать новую задачу."""
    task = await task_service.create(data)
    return await task_service.get_with_provider(task.id)


@router.put('/{task_id}', responses=responses(400, 404, 409))
@handle_errors('Ошибка при обновлении задачи')
async def update_task(
    task_id: int,
    data: TaskUpdateRequest,
    task_service: TaskServiceDep,
) -> TaskResponse:
    """Обновить задачу."""
    task = await task_service.update(task_id, data)
    return await task_service.get_with_provider(task.id)


@router.delete('/{task_id}', status_code=204, responses=responses(400, 404))
@handle_errors('Ошибка при удалении задачи')
async def delete_task(
    task_id: int,
    task_service: TaskServiceDep,
) -> None:
    """Удалить задачу."""
    await task_service.delete(task_id)

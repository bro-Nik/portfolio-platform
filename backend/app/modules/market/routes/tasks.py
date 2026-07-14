from app.common.exceptions import handle_errors

from app.modules.market.dependencies import TaskServiceDep
from app.modules.market.schemas import (
    TaskCreateRequest, TaskResponse, TaskUpdateRequest,
)
from app.modules.market.routes.app_router import AppRouter


tasks_router = AppRouter(prefix='/tasks', tags=['Admin | ApiTasks'])


@tasks_router.get('')
@handle_errors('Ошибка получения задач')
async def get_tasks(task_service: TaskServiceDep) -> list[TaskResponse]:
    return await task_service.get_all_with_providers()


@tasks_router.post('', status_code=201)
@handle_errors('Ошибка создания задачи')
async def create_task(data: TaskCreateRequest, task_service: TaskServiceDep) -> TaskResponse:
    task = await task_service.create(data)
    return await task_service.get_with_provider(task.id)


@tasks_router.put('/{task_id}')
@handle_errors('Ошибка обновления задачи')
async def update_task(task_id: int, data: TaskUpdateRequest, task_service: TaskServiceDep) -> TaskResponse:
    task = await task_service.update(task_id, data)
    return await task_service.get_with_provider(task.id)


@tasks_router.delete('/{task_id}', status_code=204)
@handle_errors('Ошибка удаления задачи')
async def delete_task(task_id: int, task_service: TaskServiceDep) -> None:
    await task_service.delete(task_id)

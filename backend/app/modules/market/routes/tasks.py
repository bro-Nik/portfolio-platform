from app.common.exceptions import handle_errors

from app.core.taskiq import broker
from app.modules.market.dependencies import TaskServiceDep
from app.modules.market.schemas import (
    TaskCreateRequest, TaskResponse, TaskUpdateRequest,
)
from app.modules.market.routes.app_router import AppRouter


tasks_router = AppRouter(prefix='/tasks', tags=['Admin | ApiTasks'])


@tasks_router.get('')
@handle_errors('Ошибка получения задач')
async def get_tasks(task_service: TaskServiceDep) -> list[TaskResponse]:
    return await task_service.get_all()


@tasks_router.post('', status_code=201)
@handle_errors('Ошибка создания задачи')
async def create_task(data: TaskCreateRequest, task_service: TaskServiceDep) -> TaskResponse:
    task = await task_service.create(data)
    return await task_service.get(task.id)


@tasks_router.put('/{task_id}')
@handle_errors('Ошибка обновления задачи')
async def update_task(task_id: int, data: TaskUpdateRequest, task_service: TaskServiceDep) -> TaskResponse:
    task = await task_service.update(task_id, data)
    return await task_service.get(task.id)


@tasks_router.delete('/{task_id}', status_code=204)
@handle_errors('Ошибка удаления задачи')
async def delete_task(task_id: int, task_service: TaskServiceDep) -> None:
    await task_service.delete(task_id)


@tasks_router.post('/{task_id}/run', status_code=202)
@handle_errors('Ошибка запуска задачи')
async def run_task(task_id: int, task_service: TaskServiceDep) -> dict:
    task = await task_service.get(task_id)
    await broker.kick(
        task_name='update_market_data',
        kwargs={
            'provider_name': task.provider_name,
            'method': task.task_type,
            'db_task_id': task.id,
            **task.parameters,
        },
    )
    return {'message': 'Задача отправлена в очередь', 'task_id': task_id}

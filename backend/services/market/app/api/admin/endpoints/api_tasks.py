from typing import List, Optional

from fastapi import APIRouter
from shared.exceptions import handle_errors

from app import schemas
from app.dependencies import ApiTaskServiceDep
from app.services import task_sync

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("/", response_model=List[schemas.ApiTaskResponse])
@handle_errors('Ошибка при получении задач')
async def get_tasks(
    ts: ApiTaskServiceDep,
    skip: int = 0,
    limit: Optional[int] = None,
) -> List[schemas.ApiTaskResponse]:
    """Получить список задач"""
    return await ts.get_tasks(skip=skip, limit=limit)


@router.post("/", response_model=schemas.ApiTaskResponse)
@handle_errors('Ошибка при создании задачи')
async def create_task(
    task_data: schemas.ApiTaskCreate,
    ts: ApiTaskServiceDep,
) -> schemas.ApiTaskResponse:
    """Создать новую задачу"""
    return await ts.create_task(task_data)


@router.put("/{task_id}", response_model=schemas.ApiTaskResponse)
@handle_errors('Ошибка при обновлении задачи')
async def update_task(
    task_id: int,
    task_data: schemas.ApiTaskUpdate,
    ts: ApiTaskServiceDep,
) -> schemas.ApiTaskResponse:
    """Обновить задачу"""
    return await ts.update_task(task_id, task_data)


@router.delete("/{task_id}")
@handle_errors('Ошибка при удалении задачи')
async def delete_task(
    task_id: int,
    ts: ApiTaskServiceDep,
) -> dict:
    """Удалить задачу"""
    await ts.delete_task(task_id)
    return {"message": "Задача удалена"}


@router.post("/run/")
def run_task(data: schemas.TaskRunRequest):
    """Запустить задачу вручную"""
    celery_task_id = task_sync.run_task_now(data.task_id)
    return {"task_id": celery_task_id, "status": "started"}


@router.post("/schedule/")
@handle_errors('Ошибка при попытке запланировать задачу')
def schedule_periodic_task(data: schemas.TaskScheduleRequest):
    """Запланировать периодическую задачу"""
    task_sync.schedule_task_from_db(data.task_id)
    return {"message": "Задача запланирована"}

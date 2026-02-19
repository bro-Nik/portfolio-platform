from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException

from app import schemas
from app.services.api_task import ApiTaskService
from app.api.admin.dependencies import get_api_task_service
from app.services import task_sync


router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("/", response_model=List[schemas.ApiTaskResponse])
async def get_tasks(
    skip: int = 0,
    limit: Optional[int] = None,
    ts: ApiTaskService = Depends(get_api_task_service)
) -> List[schemas.ApiTaskResponse]:
    """Получить список задач"""
    try:
        tasks = await ts.get_tasks(skip=skip, limit=limit)
        return tasks
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/", response_model=schemas.ApiTaskResponse)
async def create_task(
    task_data: schemas.ApiTaskCreate,
    ts: ApiTaskService = Depends(get_api_task_service)
) -> schemas.ApiTaskResponse:
    """Создать новую задачу"""
    try:
        task = await ts.create_task(task_data)
        return task
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{task_id}", response_model=schemas.ApiTaskResponse)
async def update_task(
    task_id: int,
    task_data: schemas.ApiTaskUpdate,
    ts: ApiTaskService = Depends(get_api_task_service)
) -> schemas.ApiTaskResponse:
    """Обновить задачу"""
    try:
        task = await ts.update_task(task_id, task_data)
        if not task:
            raise HTTPException(status_code=404, detail="Задача не найдена")
        return task
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{task_id}")
async def delete_task(
    task_id: int,
    ts: ApiTaskService = Depends(get_api_task_service)
) -> dict:
    """Удалить задачу"""
    try:
        await ts.delete_task(task_id)
        return {"message": "Задача удалена"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/run/")
def run_task(data: schemas.TaskRunRequest):
    """Запустить задачу вручную"""
    celery_task_id = task_sync.run_task_now(data.task_id)
    return {"task_id": celery_task_id, "status": "started"}


@router.post("/schedule/")
def schedule_periodic_task(data: schemas.TaskScheduleRequest):
    """Запланировать периодическую задачу"""
    try:
        task_sync.schedule_task_from_db(data.task_id)
        return {"message": "Задача запланирована"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

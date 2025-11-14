from fastapi import APIRouter, Depends, HTTPException
from typing import List
import uuid


from backend.core.database import get_async_session
from sqlalchemy.ext.asyncio import AsyncSession

from repositories.tasks_repository import TaskRepository
from schemas.tasks_schema import TaskResponse, TaskCreate, TaskUpdate, TaskListResponse

tasks_router = APIRouter(prefix="/api/tasks", tags=["Задания ямоборцев"])

@tasks_router.post("/", response_model=TaskResponse, summary="Создать задание")
async def create_task(
    payload: TaskCreate,
    session: AsyncSession = Depends(get_async_session)
):
    repo = TaskRepository(session)
    task = await repo.create_task(payload)
    return task

@tasks_router.get("/{task_uuid}", response_model=TaskResponse, summary="Получить задание по UUID")
async def get_task(
    task_uuid: uuid.UUID,
    session: AsyncSession = Depends(get_async_session)
):
    repo = TaskRepository(session)
    task = await repo.get_task_by_uuid(task_uuid)
    if not task:
        raise HTTPException(status_code=404, detail="Задание не найдено")
    return task

@tasks_router.patch("/{task_uuid}", response_model=TaskResponse, summary="Обновить задание")
async def update_task(
    task_uuid: uuid.UUID,
    payload: TaskUpdate,
    session: AsyncSession = Depends(get_async_session)
):
    repo = TaskRepository(session)
    task = await repo.update_task(task_uuid, payload)
    if not task:
        raise HTTPException(status_code=404, detail="Задание не найдено")
    return task

@tasks_router.delete("/{task_uuid}", summary="Удалить задание")
async def delete_task(
    task_uuid: uuid.UUID,
    session: AsyncSession = Depends(get_async_session)
):
    repo = TaskRepository(session)
    await repo.delete_task(task_uuid)
    return {"detail": "Задание удалено"}

@tasks_router.get("/", response_model=TaskListResponse, summary="Список заданий")
async def list_tasks(
    skip: int = 0,
    limit: int = 100,
    session: AsyncSession = Depends(get_async_session)
):
    repo = TaskRepository(session)
    tasks = await repo.list_tasks(skip=skip, limit=limit)
    return {"total": len(tasks), "items": tasks}

from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, delete
import uuid

from models.tasks_model import Task
from schemas.tasks_schema import TaskCreate, TaskUpdate


class TaskRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_task(self, task_create: TaskCreate) -> Task:
        task = Task(**task_create.dict())
        self.session.add(task)
        await self.session.commit()
        await self.session.refresh(task)
        return task

    async def get_task_by_uuid(self, task_uuid: uuid.UUID) -> Optional[Task]:
        query = select(Task).where(Task.uuid == task_uuid)
        result = await self.session.execute(query)
        return result.scalars().first()

    async def update_task(self, task_uuid: uuid.UUID, task_update: TaskUpdate) -> Optional[Task]:
        query = (
            update(Task).
            where(Task.uuid == task_uuid).
            values(**task_update.dict(exclude_unset=True)).
            execution_options(synchronize_session="fetch")
        )
        await self.session.execute(query)
        await self.session.commit()
        return await self.get_task_by_uuid(task_uuid)

    async def delete_task(self, task_uuid: uuid.UUID) -> None:
        query = delete(Task).where(Task.uuid == task_uuid)
        await self.session.execute(query)
        await self.session.commit()

    async def list_tasks(self, skip: int = 0, limit: int = 100) -> List[Task]:
        query = select(Task).offset(skip).limit(limit)
        result = await self.session.execute(query)
        return result.scalars().all()

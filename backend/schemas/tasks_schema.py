from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import uuid
from enum import Enum



class TaskStatusEnum(str, Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"

class TaskCreate(BaseModel):
    user_id: Optional[int]
    description: str

class TaskUpdate(BaseModel):
    description: Optional[str]
    status: Optional[TaskStatusEnum]

class TaskResponse(BaseModel):
    uuid: uuid.UUID
    user_id: Optional[int]
    description: str
    status: TaskStatusEnum
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class TaskListResponse(BaseModel):
    total: int
    items: List[TaskResponse]

# backend/schemas/users_schema.py
from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID
from typing import Optional


class UserCreate(BaseModel):
    """Схема для создания пользователя"""
    max_user_id: int = Field(..., gt=0)
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    username: str = Field(..., min_length=1, max_length=50)


class UserUpdate(BaseModel):
    """Схема для обновления пользователя"""
    first_name: Optional[str] = Field(None, max_length=50)
    last_name: Optional[str] = Field(None, max_length=50)
    username: Optional[str] = Field(None, max_length=50)


class UserResponse(BaseModel):
    """Схема для ответа"""
    uuid: UUID
    max_user_id: int
    first_name: str
    last_name: str
    username: str
    registration_at: datetime

    class Config:
        from_attributes = True

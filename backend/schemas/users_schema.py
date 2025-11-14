# backend/schemas/users_schema.py
from pydantic import BaseModel, Field, ConfigDict
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
    user_level: Optional[int] = Field(None, ge=1, le=6)
    current_status: Optional[str] = Field(None)  # Строка, не dict
    total_points: Optional[int] = Field(None, ge=0)
    sent_reports_count: Optional[int] = Field(None, ge=0)

    model_config = ConfigDict(from_attributes=True, extra='ignore')


class UserResponse(BaseModel):
    """Схема для ответа"""
    uuid: UUID
    max_user_id: int
    first_name: str
    last_name: str
    username: str
    registration_at: datetime
    sent_reports_count: int = Field(default=0, ge=0)
    user_level: int = Field(default=1, ge=1, le=6)
    current_status: Optional[str] = Field(default=None)
    total_points: int = Field(default=0, ge=0)

    model_config = ConfigDict(from_attributes=True)

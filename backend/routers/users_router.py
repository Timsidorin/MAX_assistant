# backend/routers/users_router.py
from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from uuid import UUID
import uuid  # Для совместимости с вашим стилем

from backend.core.database import get_async_session
from backend.services.users_service import UserService
from backend.schemas.users_schema import UserResponse, UserCreate  # UserUpdate не нужен для GET

users_router = APIRouter(
    prefix="/api/users",
    tags=["Пользователи"]
)


@users_router.get(
    "/{max_user_id}",
    response_model=UserResponse,
    summary="Получить пользователя по max_user_id"
)
async def get_user_by_max_id(
        max_user_id: int = Path(..., gt=0, description="Внешний ID пользователя"),
        db: AsyncSession = Depends(get_async_session)
):
    """
    Получить полную информацию о пользователе по max_user_id.

    Возвращает: имя, username, дату регистрации, количество отправленных заявок,
    уровень пользователя и текущий статус (начинающий ямоборец, etc.).
    """
    service = UserService(db)
    user = await service.get_user_by_max_user_id(max_user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return user


@users_router.get(
    "/",
    response_model=List[UserResponse],
    summary="Получить список всех пользователей"
)
async def list_users(
        username_filter: Optional[str] = Query(None, max_length=50, description="Фильтр по username"),
        min_level: Optional[int] = Query(None, ge=1, le=6, description="Минимальный уровень"),
        skip: int = Query(0, ge=0, description="Пропустить записей"),
        limit: int = Query(50, ge=1, le=100, description="Лимит записей"),
        db: AsyncSession = Depends(get_async_session)
):
    """
    Получить список пользователей с фильтрацией и пагинацией.

    Полезно для админов или дашборда.
    """
    service = UserService(db)
    return await service.get_all_users(
        username_filter=username_filter,
        min_level=min_level,
        skip=skip,
        limit=limit
    )


@users_router.get(
    "/username/{username}",
    response_model=UserResponse,
    summary="Получить пользователя по username"
)
async def get_user_by_username(
        username: str = Path(..., min_length=1, max_length=50, description="Username пользователя"),
        db: AsyncSession = Depends(get_async_session)
):
    """Получение пользователя по логину (username)"""
    service = UserService(db)
    user = await service.get_user_by_username(username)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return user


@users_router.get(
    "/uuid/{user_uuid}",
    response_model=UserResponse,
    summary="Получить пользователя по UUID"
)
async def get_user_by_uuid(
        user_uuid: UUID = Path(..., description="UUID пользователя"),
        db: AsyncSession = Depends(get_async_session)
):
    """Получение пользователя по внутреннему UUID"""
    service = UserService(db)
    user = await service.get_user_by_uuid(user_uuid)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return user

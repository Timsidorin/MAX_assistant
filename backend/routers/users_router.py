# backend/routers/users_router.py

from fastapi import APIRouter, Depends, HTTPException, Path, Query
from typing import Optional, List, Annotated
from uuid import UUID

from backend.depends import UserServiceDep, AsyncSessionDep
from backend.schemas.users_schema import UserResponse

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
    user_service: UserServiceDep = None
):
    """
    Получить полную информацию о пользователе по max_user_id.
    Возвращает: имя, username, дату регистрации, количество отправленных заявок,
    уровень пользователя и текущий статус (начинающий ямоборец, etc.).
    """
    user = await user_service.get_user_by_max_user_id(max_user_id)
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
    user_service: UserServiceDep = None
):
    """
    Получить список пользователей с фильтрацией и пагинацией.
    Полезно для админов или дашборда.
    """
    return await user_service.get_all_users(
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
    user_service: UserServiceDep = None
):
    """Получение пользователя по логину (username)"""
    user = await user_service.get_user_by_username(username)
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
    user_service: UserServiceDep = None
):
    """Получение пользователя по внутреннему UUID"""
    user = await user_service.get_user_by_uuid(user_uuid)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return user

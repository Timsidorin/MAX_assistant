from typing import Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from backend.repositories.user_repository import UserRepository
from backend.schemas.users_schema import UserResponse, UserCreate, UserUpdate


class UserService:
    def __init__(self, session: AsyncSession):
        self.repository = UserRepository(session)

    async def register_user(self, user_data: UserCreate) -> UserResponse:
        """Регистрация нового пользователя с проверкой существования"""
        if await self.repository.user_exists(user_data.username):
            raise ValueError(f"Username '{user_data.username}' already exists")
        if await self.repository.user_exists_by_max_user_id(user_data.max_user_id):
            raise ValueError(f"Max user ID '{user_data.max_user_id}' already exists")
        user = await self.repository.create_user(user_data)

        if not user:
            raise Exception("Failed to create user")

        return UserResponse.model_validate(user)

    async def get_user_by_username(self, username: str) -> Optional[UserResponse]:
        """Получение пользователя по username"""
        user = await self.repository.get_user_by_username(username)

        if not user:
            return None

        return UserResponse.model_validate(user)

    async def get_user_by_uuid(self, user_uuid: UUID) -> Optional[UserResponse]:
        """Получение пользователя по UUID"""
        user = await self.repository.get_user_by_uuid(user_uuid)

        if not user:
            return None
        return UserResponse.model_validate(user)

    async def get_user_by_max_user_id(self, max_user_id: str) -> Optional[UserResponse]:
        """Получение пользователя по max_user_id"""
        user = await self.repository.get_user_by_max_user_id(max_user_id)
        if not user:
            return None

        return UserResponse.model_validate(user)


        if not user:
            raise Exception("Failed to update user")
        return UserResponse.model_validate(user)

    async def get_all_users(self) -> list[UserResponse]:
        """Получение всех пользователей"""
        users = await self.repository.get_all_users()
        return [UserResponse.model_validate(user) for user in users]

    async def user_exists(self, username: str) -> bool:
        """Проверка существования пользователя"""
        return await self.repository.user_exists(username)

from typing import Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from backend.models.users_model import User
from backend.schemas.users_schema import UserCreate, UserUpdate


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_user(self, user_data: UserCreate) -> Optional[User]:
        """Создание нового пользователя"""
        try:
            new_user = User(
                max_user_id=user_data.max_user_id,
                first_name=user_data.first_name,
                last_name=user_data.last_name,
                username=user_data.username,
            )

            self.session.add(new_user)
            await self.session.commit()
            await self.session.refresh(new_user)
            return new_user
        except IntegrityError:
            await self.session.rollback()
            return None
        except Exception as e:
            await self.session.rollback()
            raise e

    async def get_user_by_username(self, username: str) -> Optional[User]:
        """Получение пользователя по логину"""
        try:
            query = select(User).where(User.username == username)
            result = await self.session.execute(query)
            return result.scalar_one_or_none()
        except Exception as e:
            await self.session.rollback()
            raise e

    async def get_user_by_max_user_id(self, max_user_id: int) -> Optional[User]:
        """Получение пользователя по max_user_id"""
        try:
            query = select(User).where(User.max_user_id == max_user_id)
            result = await self.session.execute(query)
            return result.scalar_one_or_none()
        except Exception as e:
            await self.session.rollback()
            raise e

    async def get_user_by_uuid(self, user_uuid: UUID) -> Optional[User]:
        """Получение пользователя по UUID"""
        try:
            query = select(User).where(User.uuid == user_uuid)
            result = await self.session.execute(query)
            return result.scalar_one_or_none()
        except Exception as e:
            await self.session.rollback()
            raise e

    async def user_exists(self, username: str) -> bool:
        """Проверка существования пользователя по логину"""
        try:
            user = await self.get_user_by_username(username)
            return user is not None
        except Exception as e:
            await self.session.rollback()
            raise e

    async def user_exists_by_max_user_id(self, max_user_id: int) -> bool:
        """Проверка существования пользователя по max_user_id"""
        try:
            user = await self.get_user_by_max_user_id(max_user_id)
            return user is not None
        except Exception as e:
            await self.session.rollback()
            raise e

    async def user_exists_by_uuid(self, user_uuid: UUID) -> bool:
        """Проверка существования пользователя по UUID"""
        try:
            user = await self.get_user_by_uuid(user_uuid)
            return user is not None
        except Exception as e:
            await self.session.rollback()
            raise e

    async def update_user(self, user_uuid: UUID, update_data: dict) -> Optional[User]:
        """
        Обновление данных пользователя
        """
        try:
            user = await self.get_user_by_uuid(user_uuid)
            if not user:
                return None
            for field, value in update_data.items():
                if hasattr(user, field) and value is not None:
                    setattr(user, field, value)
            self.session.add(user)
            await self.session.commit()
            await self.session.refresh(user)
            return user

        except IntegrityError:
            await self.session.rollback()
            return None
        except Exception as e:
            await self.session.rollback()
            raise e

    async def update(self, user: User) -> User:
        try:
            self.session.add(user)
            await self.session.commit()
            await self.session.refresh(user)
            return user
        except Exception as e:
            await self.session.rollback()
            raise e

    async def delete_user(self, user_uuid: UUID) -> bool:
        """Удаление пользователя"""
        try:
            user = await self.get_user_by_uuid(user_uuid)
            if not user:
                return False

            await self.session.delete(user)
            await self.session.commit()
            return True
        except Exception as e:
            await self.session.rollback()
            raise e

    async def get_all_users(self) -> list[User]:
        """Получение всех пользователей"""
        try:
            query = select(User)
            result = await self.session.execute(query)
            return list(result.scalars().all())
        except Exception as e:
            await self.session.rollback()
            raise e

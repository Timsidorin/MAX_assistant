from typing import Optional, List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from backend.core.config import configs
from backend.models.report_model import ReportStatus, ReportPriority
from backend.models.users_model import User
from backend.repositories.ReportRepository import ReportRepository
from backend.repositories.user_repository import UserRepository
from backend.schemas.users_schema import UserResponse, UserCreate, UserUpdate

logger = logging.getLogger(__name__)


class UserService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repository = UserRepository(session)

    async def register_user(self, user_data: UserCreate) -> UserResponse:
        """Регистрация нового пользователя с проверкой существования"""
        if await self.repository.user_exists(user_data.username):
            logger.warning(f"Username '{user_data.username}' already exists")
            raise ValueError(f"Username '{user_data.username}' already exists")

        if await self.repository.user_exists_by_max_user_id(user_data.max_user_id):
            logger.warning(f"Max user ID '{user_data.max_user_id}' already exists")
            raise ValueError(f"Max user ID '{user_data.max_user_id}' already exists")

        user = await self.repository.create_user(user_data)
        if not user:
            logger.error("Failed to create user")
            raise Exception("Failed to create user")

        logger.info(f"User '{user_data.username}' registered successfully")
        return UserResponse.model_validate(user)

    async def get_user_by_username(self, username: str) -> Optional[UserResponse]:
        """Получение пользователя по username"""
        user = await self.repository.get_user_by_username(username)
        if not user:
            logger.debug(f"User with username '{username}' not found")
            return None
        return UserResponse.model_validate(user)

    async def get_user_by_uuid(self, user_uuid: UUID) -> Optional[UserResponse]:
        """Получение пользователя по UUID"""
        user = await self.repository.get_user_by_uuid(user_uuid)
        if not user:
            logger.debug(f"User with UUID {user_uuid} not found")
            return None
        return UserResponse.model_validate(user)

    async def get_user_by_max_user_id(self, max_user_id: str) -> Optional[UserResponse]:
        """Получение пользователя по max_user_id"""
        user = await self.repository.get_user_by_max_user_id(max_user_id)
        if not user:
            logger.debug(f"User with max_user_id '{max_user_id}' not found")
            return None
        return UserResponse.model_validate(user)

    async def get_user_by_max_user_id_orm(self, max_user_id: str) -> Optional[User]:
        """
        Получение ORM пользователя по max_user_id (для внутренних операций)
        Используйте этот метод, когда нужна модификация данных
        """
        user = await self.repository.get_user_by_max_user_id(max_user_id)
        if not user:
            logger.debug(f"User with max_user_id '{max_user_id}' not found")
            return None
        return user

    async def get_all_users(self) -> List[UserResponse]:
        """Получение всех пользователей"""
        users = await self.repository.get_all_users()
        logger.debug(f"Retrieved {len(users)} users")
        return [UserResponse.model_validate(user) for user in users]

    async def user_exists(self, username: str) -> bool:
        """Проверка существования пользователя"""
        return await self.repository.user_exists(username)

    async def get_user_level(self, max_user_id: str, USER_LEVELS=None) -> dict:
        """Расчёт уровня пользователя на основе очков от отчётов"""
        if USER_LEVELS is None:
            USER_LEVELS = configs.USER_LEVELS

        user = await self.get_user_by_max_user_id_orm(max_user_id)
        if not user:
            logger.info(f"User with max_user_id '{max_user_id}' not found, returning default level")
            return {
                "level": 1,
                "name": USER_LEVELS[1]["name"],
                "points": 0,
                "sent_reports": 0
            }

        reports_repo = ReportRepository(self.session)
        user_reports, _ = await reports_repo.get_list(userid=user.max_user_id, limit=1000)

        points_map = {
            ReportPriority.LOW: 10,
            ReportPriority.MEDIUM: 20,
            ReportPriority.HIGH: 50,
            ReportPriority.CRITICAL: 100
        }

        total_points = sum(
            points_map.get(r.priority, 10)
            for r in user_reports
            if r.status in [
                ReportStatus.SUBMITTED,
                ReportStatus.IN_REVIEW,
                ReportStatus.IN_PROGRESS,
                ReportStatus.COMPLETED
            ]
        )

        level = 1
        for lvl_id, data in sorted(USER_LEVELS.items(), key=lambda x: x[1]['points']):
            if total_points >= data['points']:
                level = lvl_id
            else:
                break

        if hasattr(user, 'total_points'):
            user.total_points = total_points
            await self.repository.update(user)

        result = {
            "level": level,
            "name": USER_LEVELS[level]["name"],
            "points": total_points,
            "sent_reports": getattr(user, 'sent_reports_count', 0)
        }

        logger.info(f"User '{max_user_id}' level calculated: level={level}, points={total_points}")
        return result

    async def update_user(self, user_uuid: UUID, update_data: UserUpdate) -> Optional[UserResponse]:
        """
        Обновление данных пользователя.
        Принимает UserUpdate для partial обновлений.
        """
        current_user = await self.repository.get_user_by_uuid(user_uuid)
        if not current_user:
            logger.warning(f"User {user_uuid} not found for update")
            return None

        update_dict = update_data.model_dump(exclude_none=True, exclude_unset=True)
        if not update_dict:
            logger.debug(f"No updates provided for user {user_uuid}")
            return UserResponse.model_validate(current_user)

        try:
            updated_user = await self.repository.update_user(user_uuid, update_dict)
            if not updated_user:
                logger.error(f"Failed to update user {user_uuid}")
                return None

            logger.info(f"User {user_uuid} updated successfully with: {update_dict}")
            return UserResponse.model_validate(updated_user)

        except Exception as e:
            logger.error(f"Error updating user {user_uuid}: {e}", exc_info=True)
            await self.session.rollback()
            return None

    async def update_user_points(self, max_user_id: str, points_awarded: int) -> Optional[UserResponse]:
        """
        Специальный метод для обновления очков пользователя (для report_service)
        Возвращает обновлённого пользователя
        """
        try:
            user = await self.get_user_by_max_user_id_orm(max_user_id)
            if not user:
                logger.warning(f"User '{max_user_id}' not found for points update")
                return None

            current_points = getattr(user, 'total_points', 0)
            user.total_points = current_points + points_awarded
            user.sent_reports_count = getattr(user, 'sent_reports_count', 0) + 1

            total_points = user.total_points
            new_level = 1
            USER_LEVELS = configs.USER_LEVELS

            for level_id, level_data in sorted(USER_LEVELS.items(), key=lambda x: x[1]['points']):
                if total_points >= level_data['points']:
                    new_level = level_id
                else:
                    break

            user.user_level = new_level
            user.current_status = USER_LEVELS[new_level]['name']

            self.session.add(user)
            await self.session.refresh(user)

            logger.info(
                f"User '{max_user_id}' points updated: +{points_awarded}, "
                f"total={user.total_points}, level={new_level} ({user.current_status})"
            )
            return UserResponse.model_validate(user)

        except Exception as e:
            logger.error(f"Error updating user points for '{max_user_id}': {e}", exc_info=True)
            await self.session.rollback()
            return None

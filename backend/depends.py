from backend.core.database import get_async_session
from backend.services.users_service import UserService


async def get_user_service() -> UserService:
    """Получение сервиса пользователя с сессией"""
    session = await get_async_session()
    return UserService(session)

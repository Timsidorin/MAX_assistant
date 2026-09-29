import logging

logger = logging.getLogger(__name__)


async def notify_user(max_user_id: int, text: str) -> bool:
    """Отправить уведомление пользователю в MAX-бота.

    Безопасно вызывать из фоновых задач: любые ошибки
    (бот недоступен, пользователь заблокировал) логируются и глушатся.
    """
    if not max_user_id:
        return False
    try:
        from max_bot.main import bot
        await bot.send_message(user_id=max_user_id, text=text)
        logger.info(f"Notification sent to user {max_user_id}")
        return True
    except Exception as e:
        logger.warning(f"Failed to notify user {max_user_id}: {e}")
        return False

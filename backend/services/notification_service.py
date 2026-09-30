import logging

logger = logging.getLogger(__name__)


async def notify_user(max_user_id: int, text: str, links: list[tuple[str, str]] | None = None) -> bool:
    """Отправить уведомление пользователю в MAX-бота.

    Безопасно вызывать из фоновых задач: любые ошибки
    (бот недоступен, пользователь заблокировал) логируются и глушатся.
    """
    if not max_user_id:
        return False
    try:
        from max_bot.main import bot
        attachments = None
        if links:
            from maxapi.types import LinkButton
            from maxapi.utils.inline_keyboard import InlineKeyboardBuilder

            builder = InlineKeyboardBuilder()
            for label, url in links:
                builder.row(LinkButton(text=label, url=url))
            attachments = [builder.as_markup()]
        await bot.send_message(user_id=max_user_id, text=text, attachments=attachments)
        logger.info(f"Notification sent to user {max_user_id}")
        return True
    except Exception as e:
        logger.warning(f"Failed to notify user {max_user_id}: {e}")
        return False

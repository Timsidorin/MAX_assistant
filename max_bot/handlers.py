import logging
from typing import Optional
from maxapi.enums import TextFormat
from maxapi.types import BotStarted, MessageCreated, MessageCallback, Attachment

from backend.core.database import async_session_maker
from backend.services.users_service import UserService
from backend.schemas.users_schema import UserCreate
from max_bot.keyboards import get_main_keyboard, InstructionPayload
from max_bot.instruction import instruction_text

logger = logging.getLogger(__name__)


async def register_or_get_user(
        max_user_id: str,
        first_name: str,
        last_name: Optional[str] = None
) -> bool:
    """Регистрация или получение существующего пользователя"""
    async with async_session_maker() as session:
        try:
            service = UserService(session)
            existing_user = await service.get_user_by_max_user_id(max_user_id)

            if existing_user:
                logger.info(f"User {max_user_id} already exists")
                return False

            username = f"user_{max_user_id}"
            user_data = UserCreate(
                max_user_id=max_user_id,
                first_name=first_name,
                last_name=last_name or "Unknown",
                username=username
            )

            await service.register_user(user_data)
            await session.commit()
            logger.info(f"User {max_user_id} ({first_name}) registered successfully")
            return True
        except Exception as e:
            await session.rollback()
            logger.error(f"Error registering user: {e}", exc_info=True)
            return False
        finally:
            await session.close()


async def send_welcome(
        bot,
        user_id: int,
        first_name: str,
        last_name: Optional[str] = None,
        chat_id: Optional[int] = None
):
    is_new_user = await register_or_get_user(
        max_user_id=user_id,
        first_name=first_name,
        last_name=last_name or "Unknown"
    )

    target = {"chat_id": chat_id} if chat_id else {"user_id": user_id}
    photo_attachment = Attachment(
        type='image',
        payload={
            'url': 'https://fiesta-2000.com/image/catalog/znakiK/76%20%D0%97%D0%BD%D0%B0%D0%BA%20%D0%9E%D1%81%D1%82%D0%BE%D1%80%D0%BE%D0%B6%D0%BD%D0%BE%20%D1%8F%D0%BC%D0%B0%20.jpg'
        }
    )
    try:
        await bot.send_message(**target, attachments=[photo_attachment])
    except Exception as error:
        logger.warning(f"Failed to send welcome image to user {user_id}: {error}")

    welcome_text = (
        f"Привет, {first_name}!\n"
        "Я чат-бот, который помогает зафиксировать дорожный дефект и отправить "
        "официальное обращение в ответственную организацию.\n"
        "Нажми кнопку ниже, чтобы открыть Ямоборца."
    )
    if is_new_user:
        welcome_text += "\n\nВаш аккаунт успешно создан."

    await bot.send_message(
        **target,
        text=welcome_text,
        attachments=[get_main_keyboard()]
    )


async def start_handler(event: MessageCreated, bot):
    """Обработчик команды /start"""
    await send_welcome(
        bot=bot,
        user_id=event.from_user.user_id,
        first_name=event.from_user.first_name,
        last_name=event.from_user.last_name
    )


async def bot_started_handler(event: BotStarted, bot):
    """Обработчик нативной кнопки MAX «Начать»."""
    await send_welcome(
        bot=bot,
        user_id=event.user.user_id,
        first_name=event.user.first_name,
        last_name=event.user.last_name,
        chat_id=event.chat_id
    )


async def instruction_callback_handler(event: MessageCallback, payload: InstructionPayload):
    """Обработчик callback для показа инструкции"""
    await event.message.answer(instruction_text, format=TextFormat.MARKDOWN)

import asyncio
import logging
import os
from dotenv import load_dotenv
from pathlib import Path
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from maxapi import Bot, Dispatcher
from maxapi.filters.callback_payload import CallbackPayload
from maxapi.utils.inline_keyboard import InlineKeyboardBuilder
from maxapi.types import (
    CommandStart,
    MessageCreated,
    MessageCallback,
    Attachment,
    LinkButton,
    CallbackButton,
)

from backend.depends import get_user_service
from backend.instructions import instruction
from backend.schemas.users_schema import UserCreate
from backend.services.users_service import UserService

load_dotenv(dotenv_path="../.env", verbose=True)
logging.basicConfig(level=logging.INFO)

TOKEN = os.getenv("TOKEN_BOT")

bot = Bot(TOKEN)
dp = Dispatcher()

WEBAPP_URL = "https://orderly-familiar-bushbuck.cloudpub.ru/"


class InstructionPayload(CallbackPayload, prefix='instruction'):
    action: str = "show"

async def register_or_get_user(
        max_user_id: str,
        first_name: str,
        last_name: Optional[str] = None
) -> bool:
    service = await get_user_service()

    try:
        existing_user = await service.get_user_by_max_user_id(max_user_id)

        if existing_user:
            logging.info(f"User {max_user_id} already exists")
            return False

        username = f"user_{max_user_id}"
        user_data = UserCreate(
            max_user_id=max_user_id,
            first_name=first_name,
            last_name=last_name or "Unknown",
            username=username
        )

        await service.register_user(user_data)
        logging.info(f"User {max_user_id} ({first_name}) registered successfully")
        return True
    except Exception as e:
        logging.error(f"Error registering user: {e}")
        return False


@dp.message_created(CommandStart())
async def start_command(event: MessageCreated):
    user_id = event.from_user.user_id
    first_name = event.from_user.first_name
    last_name = event.from_user.last_name or "Unknown"

    is_new_user = await register_or_get_user(
        max_user_id=user_id,
        first_name=first_name,
        last_name=last_name
    )

    photo_attachment = Attachment(
        type='image',
        payload={
            'url': 'https://fiesta-2000.com/image/catalog/znakiK/76%20%D0%97%D0%BD%D0%B0%D0%BA%20%D0%9E%D1%81%D1%82%D0%BE%D1%80%D0%BE%D0%B6%D0%BD%D0%BE%20%D1%8F%D0%BC%D0%B0%20.jpg'
        }
    )

    await bot.send_message(
        user_id=event.from_user.user_id,
        attachments=[photo_attachment]
    )

    builder = InlineKeyboardBuilder()
    builder.row(
        LinkButton(
            text="Открыть сканер",
            url=f"https://creakily-patient-eland.cloudpub.ru/?user_id={user_id}",
        )
    )
    builder.row(
        CallbackButton(
            text="Инструкция",
            payload=InstructionPayload().pack(),
        )
    )

    welcome_text = f"Привет, {first_name}!\nЯ чат-бот, который позволяет отправлять обращения по состоянию дороги в различные инстанции твоего региона.\nДля того, чтобы отправить обращение, нажми кнопку ниже 👇"

    if is_new_user:
        welcome_text += "\n\n✅ Ваш аккаунт успешно создан!"

    await event.message.answer(
        text=welcome_text,
        attachments=[builder.as_markup()]
    )


@dp.message_callback(InstructionPayload.filter())
async def handle_instruction_callback(event: MessageCallback, payload: InstructionPayload):
    instruction_text = instruction
    await event.message.answer(instruction_text)


async def main():
    logging.info("Bot started")
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())

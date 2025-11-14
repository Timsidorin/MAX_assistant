from maxapi.utils.inline_keyboard import InlineKeyboardBuilder
from maxapi.types import CallbackButton, OpenAppButton
from maxapi.filters.callback_payload import CallbackPayload


class InstructionPayload(CallbackPayload, prefix='instruction'):
    action: str = "show"


def get_main_keyboard():
    """Главная клавиатура с кнопками приложения и инструкции"""
    builder = InlineKeyboardBuilder()
    builder.row(
        OpenAppButton(
            text="Открыть приложение",
            web_app=f"https://max.ru/t86_hakaton_bot?startapp",
        )
    )
    builder.row(
        CallbackButton(
            text="Инструкция",
            payload=InstructionPayload().pack(),
        )
    )
    return builder.as_markup()

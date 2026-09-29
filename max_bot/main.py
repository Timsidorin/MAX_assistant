import asyncio
import logging
import os
from dotenv import load_dotenv
from maxapi import Bot, Dispatcher
from maxapi.types import BotStarted, CommandStart, MessageCreated, MessageCallback

from max_bot.handlers import bot_started_handler, start_handler, instruction_callback_handler
from max_bot.keyboards import InstructionPayload



load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"), verbose=True)
logging.basicConfig(level=logging.INFO)

TOKEN = os.getenv("TOKEN_BOT")
WEBAPP_URL = os.getenv("WEBAPP_URL")

bot = Bot(TOKEN)
dp = Dispatcher()


@dp.bot_started()
async def handle_bot_started(event: BotStarted):
    await bot_started_handler(event, bot)


@dp.message_created(CommandStart())
async def start_command(event: MessageCreated):
    await start_handler(event, bot)


@dp.message_callback(InstructionPayload.filter())
async def handle_instruction_callback(event: MessageCallback, payload: InstructionPayload):
    await instruction_callback_handler(event, payload)



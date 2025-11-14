from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from typing import AsyncGenerator
from contextlib import asynccontextmanager
from starlette.responses import HTMLResponse
import asyncio
import os

from max_bot.main import dp, bot


def create_base_app(configs):
    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncGenerator[dict, None]:
        """Управление жизненным циклом приложения."""
        logger.info("Инициализация приложения...")

        model_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'cv_models', 'best.pt'))
        if os.path.isfile(model_path):
            logger.info("Модель найдена")
        else:
            logger.error("Модель не найдена, скачайте с облака: https://disk.yandex.ru/d/BQkOm1xGN9l6hQ")

        bot_task = asyncio.create_task(dp.start_polling(bot))
        logger.info("Бот запущен в фоновом режиме")

        yield

        bot_task.cancel()
        try:
            await bot_task
        except asyncio.CancelledError:
            logger.info("Бот остановлен")

        logger.info("Завершение работы приложения...")

    app = FastAPI(
        title=configs.PROJECT_NAME,
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/", response_class=HTMLResponse)
    def root():
        return """
        <html>
            <head>
                <title>Добро пожаловать</title>
                <style>
                    button {
                        padding: 10px 20px;
                        background-color: #4CAF50;
                        color: white;
                        border: none;
                        border-radius: 5px;
                        cursor: pointer;
                    }
                    button:hover {
                        background-color: #45a049;
                    }
                </style>
            </head>
            <body>
                <h1>Запустилось и работает!</h1>
                <a href="/docs">
                    <button>Перейти к документации</button>
                </a>
            </body>
        </html>
        """

    return app

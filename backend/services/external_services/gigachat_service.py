# backend/services/gigachat_service.py

"""
GigaChat Service для генерации текста заявлений.
"""

import os
import time
from typing import Optional
from dotenv import load_dotenv
from gigachat import GigaChat
from gigachat.models import Chat, Messages, MessagesRole

load_dotenv()

GIGACHAT_CREDENTIALS = os.getenv('GIGACHAT_CREDENTIALS')
GIGACHAT_SCOPE = os.getenv('GIGACHAT_SCOPE', 'GIGACHAT_API_PERS')


class GigaChatService:
    """Сервис для работы с GigaChat API."""

    def __init__(self):
        self.credentials = GIGACHAT_CREDENTIALS
        self.scope = GIGACHAT_SCOPE
        self.client = None

    def _get_client(self) -> GigaChat:
        if self.client is None:
            self.client = GigaChat(
                credentials=self.credentials,
                scope=self.scope,
                verify_ssl_certs=False
            )
        return self.client

    def generate_complaint_text(
        self,
        city: str,
        address: str,
        description: str,
        total_potholes: int,
        max_risk: float,
        priority: str
    ) -> str:
        """Генерирует текст заявления о дорожной проблеме."""
        try:
            client = self._get_client()

            prompt = f"""Составь официальное заявление в управление дорожной деятельности города {city} о проблеме с дорожным покрытием.

Адрес: {address}
Описание: {description}
Обнаружено дефектов: {total_potholes}
Уровень опасности: {max_risk:.1f}%
Приоритет: {priority}

Требования:
- Официальный стиль
- Краткость (до 200 слов)
- Указать адрес и описание
- Просьба о ремонте
- Ссылка на приложенные материалы

Начинай сразу с текста заявления."""

            messages = [Messages(role=MessagesRole.USER, content=prompt)]

            response = client.chat(Chat(messages=messages, temperature=0.7, max_tokens=500))

            generated_text = response.choices[0].message.content
            return generated_text.strip()

        except Exception as e:
            return self._generate_fallback_text(city, address, description, total_potholes, max_risk)

    def _generate_fallback_text(self, city: str, address: str, description: str, total_potholes: int, max_risk: float) -> str:
        return f"""Заявление о дефектах дорожного покрытия

Адрес: {address}

По указанному адресу обнаружены дефекты дорожного покрытия: {description}

Количество дефектов: {total_potholes}
Уровень опасности: {max_risk:.1f}%

Прошу провести осмотр и ремонт дорожного покрытия в кратчайшие сроки.
К заявлению прилагаются фото и видеоматериалы.

Дата: {time.strftime('%d.%m.%Y')}"""



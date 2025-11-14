# backend/services/gigachat_service.py

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
        priority: str,
        person_name: str = "Заявитель"
    ) -> str:
        """Генерирует текст заявления о дорожной проблеме."""
        try:
            client = self._get_client()
            prompt = f"""Составь официальное заявление в управление дорожной деятельности города {city} о проблеме с дорожным покрытием.

Заявитель: {person_name}
Адрес проблемы: {address}
Описание: {description}
Обнаружено дефектов: {total_potholes}
Уровень опасности: {max_risk:.1f}%
Приоритет: {priority}

НАЧИНАЙ текст так:
Заявление
В [организация]
От: {person_name}

ОБЯЗАТЕЛЬНО:
- НЕ УКАЗЫВАЙ адрес проживания заявителя, телефон, email
- Укажи только ФИО: {person_name} в начале (От:) и в конце (Подпись)
- Опиши проблему с дорогой по адресу {address}
- Укажи уровень опасности {max_risk:.1f}% и количество дефектов {total_potholes}
- Упомяни приложенные фотографии
- Закончи просьбой о ремонте и ФИО

Кратко, официально, 150-200 слов. БЕЗ контактных данных заявителя!"""

            messages = [Messages(role=MessagesRole.USER, content=prompt)]
            response = client.chat(Chat(messages=messages, temperature=0.5, max_tokens=400))
            generated_text = response.choices[0].message.content
            return generated_text.strip()
        except Exception as e:
            print(f"[GigaChat Service] Error generating text: {e}")
            return self._generate_fallback_text(
                city=city,
                address=address,
                description=description,
                total_potholes=total_potholes,
                max_risk=max_risk,
                priority=priority,
                person_name=person_name
            )

    def _generate_fallback_text(
        self,
        city: str,
        address: str,
        description: str,
        total_potholes: int,
        max_risk: float,
        priority: str,
        person_name: str = "Заявитель"
    ) -> str:
        """Резервный текст на случай ошибки GigaChat."""
        current_date = time.strftime('%d.%m.%Y')
        organization_name = "Управление дорожной деятельности администрации города " + city

        return f"""Заявление

В {organization_name}

От: {person_name}

Обращаюсь с заявлением о неудовлетворительном состоянии дорожного покрытия по адресу: {address}.

Описание проблемы: {description}

На указанном участке обнаружены дефекты дорожного покрытия:
- Количество дефектов: {total_potholes}
- Уровень опасности: {max_risk:.1f}%
- Приоритет: {priority.upper()}

Данные дефекты представляют угрозу безопасности дорожного движения и требуют срочного устранения.

Прошу:
1. Провести осмотр указанного участка в кратчайшие сроки
2. Организовать ремонтные работы для устранения выявленных дефектов
3. При необходимости установить предупреждающие знаки

К заявлению прилагаются фотографии дефектов ({total_potholes} шт.).

Дата: {current_date}

{person_name}"""

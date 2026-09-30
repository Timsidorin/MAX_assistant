"""Поиск контактов дорожных служб: DaData -> GigaChat -> fallback."""

import json
import os
import re
import time
from typing import Optional, Dict, List

import httpx
from dotenv import load_dotenv
from loguru import logger

from backend.services.external_services.gigachat_service import GigaChatService

load_dotenv()

DADATA_API_KEY = os.getenv("DADATA_API_KEY")
DADATA_SUGGEST_URL = "https://suggestions.dadata.ru/suggestions/api/4_1/rs"
REQUEST_TIMEOUT = 10
CACHE_TTL = 24 * 60 * 60  # сутки

EMAIL_PATTERN = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
PHONE_PATTERN = r"\+7\s?\(?\d{3}\)?\s?\d{3}[-\s]?\d{2}[-\s]?\d{2}"

# Шаблоны поиска дорожной организации в DaData party
PARTY_QUERIES = [
    "управление дорожной деятельности {city}",
    "управление дорог {city}",
    "дорожное хозяйство {city}",
    "комитет дорожного хозяйства {city}",
    "администрация {city}",
]


class AIAgentService:
    """Поиск контактов управления дорожной деятельности по адресу."""

    def __init__(self):
        self._gigachat: Optional[GigaChatService] = None
        self._cache: Dict[str, dict] = {}  # city -> {ts, data}

    @property
    def gigachat(self) -> GigaChatService:
        if self._gigachat is None:
            self._gigachat = GigaChatService()
        return self._gigachat

    def _extract_city(self, address: str) -> Optional[str]:
        """Извлекает город из адреса через DaData, regex как fallback."""
        if DADATA_API_KEY:
            try:
                resp = httpx.post(
                    f"{DADATA_SUGGEST_URL}/suggest/address",
                    headers={
                        "Authorization": f"Token {DADATA_API_KEY}",
                        "Content-Type": "application/json",
                    },
                    json={"query": address, "count": 1},
                    timeout=REQUEST_TIMEOUT,
                )
                if resp.status_code == 200:
                    suggestions = resp.json().get("suggestions") or []
                    if suggestions:
                        data = suggestions[0].get("data") or {}
                        city = data.get("city") or data.get("settlement") or data.get("region")
                        if city:
                            logger.info(f"DaData resolved city: {city}")
                            return city
            except Exception as e:
                logger.warning(f"DaData address suggest failed: {e}")

        match = re.search(r"г\s+([А-Яа-яЁё\s\-]+?)(?=\s*,|\s+край|\s+область|$)", address, re.IGNORECASE)
        return match.group(1).strip() if match else None

    def _search_party_contacts(self, city: str) -> Optional[dict]:
        """Ищет дорожную организацию через DaData party suggestions."""
        if not DADATA_API_KEY:
            return None

        for template in PARTY_QUERIES:
            try:
                resp = httpx.post(
                    f"{DADATA_SUGGEST_URL}/suggest/party",
                    headers={
                        "Authorization": f"Token {DADATA_API_KEY}",
                        "Content-Type": "application/json",
                    },
                    json={"query": template.format(city=city), "count": 5},
                    timeout=REQUEST_TIMEOUT,
                )
                if resp.status_code != 200:
                    continue

                for sug in resp.json().get("suggestions") or []:
                    data = sug.get("data") or {}
                    # Берём только действующие госорганы/учреждения
                    state = (data.get("state") or {}).get("status")
                    if state and state not in ("ACTIVE",):
                        continue

                    emails = data.get("emails") or []
                    phones = data.get("phones") or []

                    result = {
                        "organization": sug.get("value") or data.get("name", {}).get("full_with_opf"),
                        "email": emails[0] if emails else None,
                        "phone": phones[0] if phones else None,
                        "website": None,
                        "source": "dadata",
                    }
                    if result["organization"]:
                        logger.info(f"DaData party: {result['organization']} (email={result['email']})")
                        return result
            except Exception as e:
                logger.warning(f"DaData party suggest failed for '{template}': {e}")

        return None

    def _search_gigachat(self, city: str, address: str) -> Optional[dict]:
        """Просит GigaChat вернуть контакты дорожной службы в JSON."""
        prompt = f"""Какая организация отвечает за состояние дорог в городе {city} (адрес обращения: {address})?

Верни ТОЛЬКО валидный JSON без пояснений и markdown:
{{"organization": "полное название ведомства", "email": "email для обращений или null", "phone": "телефон или null", "website": "сайт или null"}}

Если email не знаешь точно — поставь null, НЕ выдумывай."""

        try:
            client = self.gigachat._get_client()
            from gigachat.models import Chat, Messages, MessagesRole
            response = client.chat(
                Chat(messages=[Messages(role=MessagesRole.USER, content=prompt)],
                     temperature=0.2, max_tokens=300)
            )
            text = response.choices[0].message.content.strip()
            match = re.search(r"\{.*\}", text, re.DOTALL)
            if not match:
                return None

            data = json.loads(match.group(0))
            email = data.get("email")
            if email and not re.fullmatch(EMAIL_PATTERN, email):
                email = None

            return {
                "organization": data.get("organization"),
                "email": email,
                "phone": data.get("phone"),
                "website": data.get("website"),
                "source": "gigachat",
            }
        except Exception as e:
            logger.warning(f"GigaChat contact search failed: {e}")
            return None

    def find_road_agency_contacts(self, address: str, coordinates: Optional[dict] = None) -> dict:
        """Находит контакты дорожной службы: DaData -> GigaChat -> fallback."""
        city = self._extract_city(address)

        if not city:
            return {
                "success": False,
                "city": None,
                "organization": "Росавтодор",
                "email": "rad@rosavtodor.gov.ru",
                "website": "https://rosavtodor.gov.ru",
                "phone": None,
                "status": "city_not_found",
            }

        # Кэш по городу
        cached = self._cache.get(city)
        if cached and time.time() - cached["ts"] < CACHE_TTL:
            logger.info(f"Contacts for {city} from cache")
            result = dict(cached["data"])
            result["status"] = "cached"
            return result

        # DaData party
        result = self._search_party_contacts(city)

        # GigaChat fallback / дополнение email
        if not result or not result.get("email"):
            giga = self._search_gigachat(city, address)
            if giga:
                if result:
                    result["email"] = result["email"] or giga.get("email")
                    result["phone"] = result["phone"] or giga.get("phone")
                    result["website"] = result["website"] or giga.get("website")
                else:
                    result = giga

        if result and result.get("email"):
            data = {
                "success": True,
                "city": city,
                "organization": result.get("organization") or f"Управление дорожной деятельности {city}",
                "email": result["email"],
                "website": result.get("website"),
                "phone": result.get("phone"),
                "status": "found",
            }
            self._cache[city] = {"ts": time.time(), "data": data}
            return data

        # Финальный fallback: федеральный портал для дорожных обращений
        return {
            "success": False,
            "city": city,
            "organization": (result or {}).get("organization") or f"Администрация {city}",
            "email": (result or {}).get("email"),
            "website": "https://pos.gosuslugi.ru",
            "phone": (result or {}).get("phone"),
            "status": "email_not_found",
        }


_service_instance = None


def find_road_agency_contacts(address: str, coordinates: Optional[dict] = None) -> dict:
    """Публичная функция для использования в других модулях."""
    global _service_instance
    if _service_instance is None:
        _service_instance = AIAgentService()
    return _service_instance.find_road_agency_contacts(address, coordinates)


if __name__ == "__main__":
    result = find_road_agency_contacts("Приморский край, г Владивосток, ул Светланская, 1")
    print(json.dumps(result, ensure_ascii=False, indent=2))

import json
import os
import re
import time
from typing import Optional, Dict

import httpx
from dotenv import load_dotenv
from loguru import logger

from backend.services.external_services.gigachat_service import GigaChatService

load_dotenv()

DADATA_API_KEY = os.getenv("DADATA_API_KEY")
DADATA_SUGGEST_URL = "https://suggestions.dadata.ru/suggestions/api/4_1/rs"
REQUEST_TIMEOUT = 10
CACHE_TTL = 24 * 60 * 60

EMAIL_PATTERN = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
PHONE_PATTERN = r"\+7\s?\(?\d{3}\)?\s?\d{3}[-\s]?\d{2}[-\s]?\d{2}"

PARTY_QUERIES = [
    "управление дорожной деятельности {city}",
    "управление дорог {city}",
    "дорожное хозяйство {city}",
    "комитет дорожного хозяйства {city}",
    "министерство транспорта {region}",
    "министерство дорожного хозяйства {region}",
    "администрация {city}",
    "мэрия {city}",
    "благоустройство {city}",
    "ЖКХ {city}",
]


class AIAgentService:
    """Поиск контактов организации, ответственной за дороги."""

    def __init__(self):
        self._gigachat: Optional[GigaChatService] = None
        self._cache: Dict[str, dict] = {}

    @property
    def gigachat(self) -> GigaChatService:
        if self._gigachat is None:
            self._gigachat = GigaChatService()
        return self._gigachat

    def _extract_city_and_region(self, address: str) -> tuple[Optional[str], Optional[str]]:
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
                        city = data.get("city") or data.get("settlement") or data.get("region_with_type")
                        region = data.get("region_with_type")
                        if city:
                            logger.info(f"DaData resolved city={city}, region={region}")
                            return city, region
            except Exception as e:
                logger.warning(f"DaData address suggest failed: {e}")

        match = re.search(
            r"г\s+([А-Яа-яЁё\s\-]+?)(?=\s*,|\s+край|\s+область|\s+республика|\s+ао|$)",
            address,
            re.IGNORECASE,
        )
        city = match.group(1).strip() if match else None
        region = None
        return city, region

    def _search_party_contacts(self, city: Optional[str], region: Optional[str]) -> Optional[dict]:
        if not DADATA_API_KEY:
            return None

        for template in PARTY_QUERIES:
            query = template.format(city=city or "", region=region or city or "")
            if not query.strip():
                continue
            try:
                resp = httpx.post(
                    f"{DADATA_SUGGEST_URL}/suggest/party",
                    headers={
                        "Authorization": f"Token {DADATA_API_KEY}",
                        "Content-Type": "application/json",
                    },
                    json={"query": query, "count": 10},
                    timeout=REQUEST_TIMEOUT,
                )
                if resp.status_code != 200:
                    continue

                for sug in resp.json().get("suggestions") or []:
                    data = sug.get("data") or {}
                    state = (data.get("state") or {}).get("status")
                    if state and state not in ("ACTIVE", "LIQUIDATING"):
                        continue

                    emails = data.get("emails") or []
                    phones = data.get("phones") or []
                    organization = (
                        sug.get("value")
                        or (data.get("name", {}) or {}).get("full_with_opf")
                        or (data.get("name", {}) or {}).get("short")
                    )
                    if not organization:
                        continue

                    result = {
                        "organization": organization,
                        "email": emails[0] if emails else None,
                        "phone": phones[0] if phones else None,
                        "website": None,
                        "source": "dadata",
                    }
                    logger.info(
                        f"DaData party: {result['organization']} email={result['email']} "
                        f"phone={result['phone']}"
                    )
                    return result
            except Exception as e:
                logger.warning(f"DaData party suggest failed for '{query}': {e}")

        return None

    def _search_gigachat_contacts(self, city: Optional[str], region: Optional[str], address: str) -> Optional[dict]:
        location = city or region or "город неизвестен"
        prompt = f"""Какая организация отвечает за содержание дорог в населённом пункте {location} (адрес обращения: {address})?

Верни ТОЛЬКО валидный JSON без пояснений и markdown:
{{"organization": "полное название ведомства", "email": "email для обращений или null", "phone": "телефон или null", "website": "сайт или null"}}

Правила:
- email должен быть реальным рабочим адресом ведомства или null;
- если email неизвестен точно — поставь null, НЕ выдумывай;
- для маленьких городов обычно отвечает местная администрация или районное управление дорог.
"""
        return self._call_gigachat(prompt, source="gigachat")

    def _search_gigachat_email(self, organization: str, city: Optional[str]) -> Optional[str]:
        prompt = f"""Найди официальный email для обращений граждан в организацию "{organization}" в городе {city or 'Россия'}.

Верни ТОЛЬКО валидный JSON без пояснений:
{{"email": "email для обращений или null"}}

Правила:
- email должен быть реальным, опубликованным на официальном сайте;
- если не уверен — поставь null, НЕ выдумывай;
- приоритет: приёмная, канцелярия, обращения граждан.
"""
        result = self._call_gigachat(prompt, source="gigachat")
        if result:
            email = result.get("email")
            if email and re.fullmatch(EMAIL_PATTERN, email):
                logger.info(f"GigaChat email found for {organization}: {email}")
                return email
        return None

    def _call_gigachat(self, prompt: str, source: str = "gigachat") -> Optional[dict]:
        try:
            client = self.gigachat._get_client()
            from gigachat.models import Chat, Messages, MessagesRole
            response = client.chat(
                Chat(
                    messages=[Messages(role=MessagesRole.USER, content=prompt)],
                    temperature=0.2,
                    max_tokens=300,
                )
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
                "source": source,
            }
        except Exception as e:
            logger.warning(f"GigaChat contact search failed: {e}")
            return None

    def find_road_agency_contacts(self, address: str, coordinates: Optional[dict] = None) -> dict:
        city, region = self._extract_city_and_region(address)

        if not city and not region:
            return {
                "success": False,
                "city": None,
                "region": None,
                "organization": "Федеральное дорожное агентство (Росавтодор)",
                "email": None,
                "website": "https://rosavtodor.gov.ru",
                "phone": "+7 (495) 995-50-55",
                "status": "city_not_found",
                "source": "fallback",
            }

        cache_key = f"{city or ''}|{region or ''}"
        cached = self._cache.get(cache_key)
        if cached and time.time() - cached["ts"] < CACHE_TTL:
            logger.info(f"Contacts for {cache_key} from cache")
            result = dict(cached["data"])
            result["status"] = "cached"
            return result

        # 1. DaData party
        dadata_result = self._search_party_contacts(city, region)

        # 2. GigaChat: поиск организации + email
        giga = None
        if not dadata_result or not dadata_result.get("email"):
            giga = self._search_gigachat_contacts(city, region, address)

        # 3. Слияние результатов
        organization = None
        email = None
        phone = None
        website = None
        source = "fallback"

        if dadata_result:
            organization = dadata_result.get("organization")
            email = dadata_result.get("email")
            phone = dadata_result.get("phone")
            source = "dadata"

        if giga:
            organization = organization or giga.get("organization")
            email = email or giga.get("email")
            phone = phone or giga.get("phone")
            website = website or giga.get("website")
            source = "dadata+gigachat" if dadata_result else "gigachat"

        # 4. Если организация есть, но email нет — попробуем найти email через GigaChat по названию
        if organization and not email:
            email = self._search_gigachat_email(organization, city)
            if email:
                source = f"{source}+gigachat_email"

        if not organization:
            organization = f"Управление дорожной деятельности {city or region}"

        if email:
            data = {
                "success": True,
                "city": city,
                "region": region,
                "organization": organization,
                "email": email,
                "website": website,
                "phone": phone,
                "status": "found",
                "source": source,
            }
            self._cache[cache_key] = {"ts": time.time(), "data": data}
            return data

        # 6. Федеральный fallback
        return {
            "success": False,
            "city": city,
            "region": region,
            "organization": organization,
            "email": None,
            "website": website or "https://rosavtodor.gov.ru",
            "phone": phone or "+7 (495) 995-50-55",
            "status": "email_not_found",
            "source": source,
        }


_service_instance = None


def find_road_agency_contacts(address: str, coordinates: Optional[dict] = None) -> dict:
    global _service_instance
    if _service_instance is None:
        _service_instance = AIAgentService()
    return _service_instance.find_road_agency_contacts(address, coordinates)

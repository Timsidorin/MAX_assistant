import ipaddress
import json
import os
import re
import socket
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
        prompt = f"""Определи владельца дороги и официальный канал подачи обращения о дефекте по адресу: {address}. Населённый пункт: {location}, регион: {region or 'неизвестен'}.

Проверь последовательно муниципальный дорожный орган, региональное министерство или дорожное учреждение, а для федеральной дороги — территориальное ФКУ Упрдор Росавтодора. Не выбирай администрацию только потому, что найден её сайт.

Верни ТОЛЬКО валидный JSON без пояснений и markdown:
{{"organization": "полное название", "authority_level": "municipal|regional|federal|unknown", "channel_type": "email|web_form|public_portal|phone|manual", "email": "email или null", "phone": "телефон или null", "website": "официальная страница канала или null", "source_url": "официальная страница, подтверждающая контакт, или null", "reason": "краткое основание выбора"}}

Правила:
- email допустим только если он опубликован на указанной официальной странице source_url;
- для обращения через форму верни channel_type=web_form и прямую ссылку на форму;
- не придумывай email, домен, организацию или принадлежность дороги;
- Росавтодор или ФКУ Упрдор выбирай только при признаках федеральной дороги;
- если принадлежность дороги не установлена, выбери официальный региональный или федеральный портал обращений для маршрутизации, channel_type=public_portal;
- если достоверного канала нет, channel_type=manual.
"""
        result = self._call_gigachat(prompt, source="gigachat")
        if result and result.get("email"):
            source_url = result.get("source_url")
            if not source_url or not self._email_is_published(result["email"], source_url):
                logger.warning(f"Rejected unverified GigaChat email for {result.get('organization')}")
                result["email"] = None
                if result.get("website"):
                    result["channel_type"] = "web_form"
        return result

    def _search_gigachat_email(self, organization: str, city: Optional[str]) -> Optional[dict]:
        prompt = f"""Найди официальный канал обращений граждан организации "{organization}" в городе {city or 'Россия'}.

Верни ТОЛЬКО валидный JSON без пояснений:
{{"email": "email или null", "website": "прямая ссылка на форму или null", "source_url": "официальная страница с контактом или null", "channel_type": "email|web_form|public_portal|phone|manual"}}

Email указывай только вместе с официальной страницей source_url, на которой он опубликован. Если не уверен — null. Не генерируй адрес по домену.
"""
        result = self._call_gigachat(prompt, source="gigachat")
        if not result:
            return None
        email = result.get("email")
        source_url = result.get("source_url")
        if email and source_url and self._email_is_published(email, source_url):
            logger.info(f"Verified GigaChat email found for {organization}: {email}")
            return result
        result["email"] = None
        return result

    def _email_is_published(self, email: str, source_url: str) -> bool:
        try:
            if not re.fullmatch(EMAIL_PATTERN, email):
                return False
            url = httpx.URL(source_url)
            host = (url.host or "").lower()
            if (
                url.scheme not in {"http", "https"}
                or not host.endswith((".ru", ".рф"))
                or url.port not in {None, 80, 443}
                or url.userinfo
            ):
                return False
            addresses = {item[4][0] for item in socket.getaddrinfo(host, None)}
            if not addresses or any(not ipaddress.ip_address(address).is_global for address in addresses):
                return False
            response = httpx.get(source_url, timeout=REQUEST_TIMEOUT, follow_redirects=True)
            return response.status_code == 200 and email.lower() in response.text.lower()
        except Exception as e:
            logger.warning(f"Official contact verification failed for {source_url}: {e}")
            return False

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
                "source_url": data.get("source_url"),
                "authority_level": data.get("authority_level", "unknown"),
                "channel_type": data.get("channel_type", "manual"),
                "reason": data.get("reason"),
                "source": source,
            }
        except Exception as e:
            logger.warning(f"GigaChat contact search failed: {e}")
            return None

    def find_road_agency_contacts(self, address: str, coordinates: Optional[dict] = None) -> dict:
        city, region = self._extract_city_and_region(address)

        if not city and not region:
            return {
                "success": True,
                "city": None,
                "region": None,
                "organization": "Платформа обратной связи Госуслуг",
                "email": None,
                "website": "https://pos.gosuslugi.ru",
                "phone": None,
                "status": "public_portal",
                "source": "official_federal_fallback",
                "source_url": "https://pos.gosuslugi.ru",
                "authority_level": "unknown",
                "channel_type": "public_portal",
                "reason": "Местоположение не определено; обращение требует маршрутизации через официальный государственный портал.",
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
            if giga.get("email") or giga.get("website"):
                organization = giga.get("organization") or organization
            else:
                organization = organization or giga.get("organization")
            email = email or giga.get("email")
            phone = phone or giga.get("phone")
            website = website or giga.get("website")
            source = "dadata+gigachat" if dadata_result else "gigachat"

        # 4. Если организация есть, но email нет — попробуем найти официальный канал по названию
        channel_type = giga.get("channel_type") if giga else None
        authority_level = giga.get("authority_level") if giga else "unknown"
        source_url = giga.get("source_url") if giga else None
        reason = giga.get("reason") if giga else None
        if organization and not email:
            channel = self._search_gigachat_email(organization, city)
            if channel:
                email = channel.get("email")
                website = website or channel.get("website")
                source_url = source_url or channel.get("source_url")
                channel_type = channel.get("channel_type") or channel_type
                source = f"{source}+gigachat_channel"

        if not organization:
            organization = f"Дорожный орган по адресу: {city or region}"

        if email or website:
            data = {
                "success": True,
                "city": city,
                "region": region,
                "organization": organization,
                "email": email,
                "website": website,
                "phone": phone,
                "status": "email_found" if email else channel_type or "web_form",
                "source": source,
                "source_url": source_url,
                "authority_level": authority_level,
                "channel_type": "email" if email else channel_type or "web_form",
                "reason": reason,
            }
            self._cache[cache_key] = {"ts": time.time(), "data": data}
            return data

        return {
            "success": True,
            "city": city,
            "region": region,
            "organization": "Платформа обратной связи Госуслуг",
            "email": None,
            "website": "https://pos.gosuslugi.ru",
            "phone": None,
            "status": "public_portal",
            "source": "official_federal_fallback",
            "source_url": "https://pos.gosuslugi.ru",
            "authority_level": "unknown",
            "channel_type": "public_portal",
            "reason": "Владелец дороги достоверно не определён; обращение должно быть маршрутизировано компетентному ведомству через официальный государственный портал.",
        }


_service_instance = None


def find_road_agency_contacts(address: str, coordinates: Optional[dict] = None) -> dict:
    global _service_instance
    if _service_instance is None:
        _service_instance = AIAgentService()
    return _service_instance.find_road_agency_contacts(address, coordinates)

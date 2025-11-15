"""
AI Agent Service - интеллектуальный поиск email через Яндекс Алису.
"""

import re
import os
import time
import json
import random
from typing import Optional, Dict
from dotenv import load_dotenv
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from loguru import logger

load_dotenv()

SELENIUM_TIMEOUT = int(os.getenv('SELENIUM_TIMEOUT', '20'))
ALISA_RESPONSE_TIMEOUT = int(os.getenv('ALISA_RESPONSE_TIMEOUT', '60'))
REQUEST_DELAY_MIN = int(os.getenv('REQUEST_DELAY_MIN', '5'))
REQUEST_DELAY_MAX = int(os.getenv('REQUEST_DELAY_MAX', '15'))


class ContentLoadedCondition:
    """Кастомное условие: ждёт загрузки контента с email или достаточным количеством текста."""

    def __init__(self, class_name: str, email_pattern: str, min_length: int = 100):
        self.class_name = class_name
        self.email_pattern = email_pattern
        self.min_length = min_length

    def __call__(self, driver):
        try:
            blocks = driver.find_elements(By.CLASS_NAME, self.class_name)
            if not blocks:
                return False

            all_text = "\n".join([block.text for block in blocks if block.text])

            has_email = re.search(self.email_pattern, all_text)
            has_content = len(all_text) >= self.min_length

            if has_email or has_content:
                return all_text
            return False
        except Exception:
            return False


class AIAgentService:
    """Сервис для поиска контактов управлений дорожной деятельности через Алису."""

    def __init__(self):
        self.email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        self.phone_pattern = r'\+7\s?\(?\d{3}\)?\s?\d{3}[-\s]?\d{2}[-\s]?\d{2}'
        self.cache = {}
        self.last_request_time = 0

    def _setup_driver(self) -> uc.Chrome:
        """Настройка undetected Chrome WebDriver для обхода капчи."""
        options = uc.ChromeOptions()

        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-extensions')
        options.add_argument('disable-infobars')
        options.add_argument(
            '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

        try:
            driver = uc.Chrome(options=options, version_main=None)
            driver.set_page_load_timeout(30)
            return driver
        except Exception as e:
            logger.error(f"Chrome WebDriver initialization error: {e}")
            raise

    def _extract_city(self, address: str) -> Optional[str]:
        """Извлекает название города из адреса."""
        match = re.search(r'г\s+([А-Яа-яЁё\s\-]+?)(?=\s*,|\s+край|\s+область|$)', address, re.IGNORECASE)
        return match.group(1).strip() if match else None

    def _build_search_query(self, city: str) -> str:
        """Формирует оптимизированный поисковый запрос для Алисы."""
        queries = [
            f"email для обращений по дорогам в городе {city}",
            f"контакты управления дорожной деятельности {city}",
            f"куда писать о проблемах с дорогами в {city}",
            f"email уддивб {city}",
        ]
        return queries[0]

    def _wait_before_request(self):
        """Добавляет случайную задержку между запросами для обхода блокировок."""
        elapsed = time.time() - self.last_request_time
        min_delay = REQUEST_DELAY_MIN

        if elapsed < min_delay:
            delay = random.uniform(min_delay - elapsed, REQUEST_DELAY_MAX)
            logger.debug(f"Waiting {delay:.1f}s before request")
            time.sleep(delay)

        self.last_request_time = time.time()

    def _simulate_human_behavior(self, driver):
        """Имитирует человеческое поведение для обхода антибот-систем."""
        scroll_amount = random.randint(100, 500)
        driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
        time.sleep(random.uniform(0.5, 1.5))
        driver.execute_script("""
            document.dispatchEvent(new MouseEvent('mousemove', {
                bubbles: true,
                clientX: Math.random() * window.innerWidth,
                clientY: Math.random() * window.innerHeight
            }));
        """)

    def _parse_alisa_answer(self, query: str) -> Dict[str, Optional[str]]:
        """Парсит ответ Алисы и извлекает email и телефон."""
        driver = None
        result = {
            'email': None,
            'phone': None,
            'organization': None
        }

        try:
            self._wait_before_request()

            logger.info(f"Starting browser for query: '{query}'")
            driver = self._setup_driver()

            search_url = f"https://ya.ru/search/?text={query}"
            driver.get(search_url)

            self._simulate_human_behavior(driver)

            wait = WebDriverWait(driver, SELENIUM_TIMEOUT)

            try:
                close_button = wait.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[aria-label="Нет, спасибо"]'))
                )
                time.sleep(random.uniform(0.5, 1.5))
                close_button.click()
            except (TimeoutException, NoSuchElementException):
                pass

            try:
                wait.until(EC.invisibility_of_element_located((By.CLASS_NAME, "Distribution-SplashScreenModalScene")))
            except TimeoutException:
                pass

            if "captcha" in driver.current_url.lower() or "showcaptcha" in driver.current_url.lower():
                logger.warning("Captcha detected")
                return result

            try:
                alisa_links = driver.find_elements(By.PARTIAL_LINK_TEXT, "алиса")
                if not alisa_links:
                    alisa_links = driver.find_elements(By.PARTIAL_LINK_TEXT, "Алиса")

                if alisa_links:
                    logger.info("Clicking on Alisa tab")
                    time.sleep(random.uniform(1, 2))
                    driver.execute_script("arguments[0].click();", alisa_links[0])

                    extended_wait = WebDriverWait(driver, ALISA_RESPONSE_TIMEOUT)

                    logger.info(f"Waiting up to {ALISA_RESPONSE_TIMEOUT}s for Alisa response")

                    try:
                        all_text = extended_wait.until(
                            ContentLoadedCondition("FuturisMarkdown", self.email_pattern, 100)
                        )

                        if not all_text:
                            logger.debug("Initial wait completed, checking content")
                            max_retries = 10
                            retry_count = 0

                            while retry_count < max_retries:
                                answer_blocks = driver.find_elements(By.CLASS_NAME, "FuturisMarkdown")
                                all_text = "\n".join([block.text for block in answer_blocks if block.text])

                                if re.search(self.email_pattern, all_text) or len(all_text) > 100:
                                    logger.info(f"Content loaded successfully ({len(all_text)} chars)")
                                    break

                                logger.debug(f"Waiting for content, retry {retry_count + 1}/{max_retries}")
                                time.sleep(2)
                                retry_count += 1

                            if retry_count >= max_retries:
                                logger.warning("Max retries reached, content may be incomplete")
                        else:
                            logger.info(f"Content loaded successfully ({len(all_text)} chars)")

                        answer_blocks = driver.find_elements(By.CLASS_NAME, "FuturisMarkdown")
                        all_text = "\n".join([block.text for block in answer_blocks if block.text])

                        if len(all_text) == 0:
                            logger.warning("No text content found in answer blocks")
                            return result

                        logger.debug(f"Total text length: {len(all_text)}")

                        emails = re.findall(self.email_pattern, all_text)
                        unique_emails = list(set(emails))

                        phones = re.findall(self.phone_pattern, all_text)
                        unique_phones = list(set(phones))

                        org_patterns = [
                            r'(Управление дорожной деятельности[^.]*)',
                            r'(УДД[^.]*)',
                            r'(Администрация[^.]*)',
                        ]
                        for pattern in org_patterns:
                            org_match = re.search(pattern, all_text)
                            if org_match:
                                result['organization'] = org_match.group(1).strip()
                                break

                        if unique_emails:
                            result['email'] = unique_emails[0]
                            logger.info(f"Found email: {result['email']}")

                        if unique_phones:
                            result['phone'] = unique_phones[0]
                            logger.info(f"Found phone: {result['phone']}")

                        if not unique_emails and not unique_phones:
                            logger.warning("No contacts found in response")

                    except TimeoutException:
                        logger.error(f"Timeout: Alisa took longer than {ALISA_RESPONSE_TIMEOUT}s to respond")

                else:
                    logger.warning("Alisa tab not found")

            except Exception as e:
                logger.error(f"Error parsing Alisa: {e}")

        except Exception as e:
            logger.error(f"Browser error: {e}")

        finally:
            if driver:
                driver.quit()

        return result

    def find_road_agency_contacts(self, address: str, coordinates: Optional[dict] = None) -> dict:
        """
        Главная функция поиска контактов управления дорожной деятельности.
        С кешированием для избежания повторных запросов.
        """

        city = self._extract_city(address)

        if not city:
            return {
                "success": False,
                "city": None,
                "organization": "Росавтодор",
                "email": "rad@rosavtodor.gov.ru",
                "website": "https://rosavtodor.gov.ru",
                "phone": None,
                "status": "city_not_found"
            }

        if city in self.cache:
            logger.info(f"Using cached data for {city}")
            cached = self.cache[city]
            return {
                "success": cached['email'] is not None,
                "city": city,
                "organization": cached.get('organization') or f"Управление дорожной деятельности {city}",
                "email": cached['email'],
                "website": None,
                "phone": cached.get('phone'),
                "status": "cached"
            }

        query = self._build_search_query(city)

        alisa_result = self._parse_alisa_answer(query)
        self.cache[city] = alisa_result

        if alisa_result['email']:
            return {
                "success": True,
                "city": city,
                "organization": alisa_result.get('organization') or f"Управление дорожной деятельности {city}",
                "email": alisa_result['email'],
                "website": None,
                "phone": alisa_result.get('phone'),
                "status": "found"
            }
        else:
            return {
                "success": False,
                "city": city,
                "organization": f"Администрация {city}",
                "email": None,
                "website": None,
                "phone": alisa_result.get('phone'),
                "status": "email_not_found"
            }


_service_instance = None


def find_road_agency_contacts(address: str, coordinates: Optional[dict] = None) -> dict:
    """Публичная функция для использования в других модулях."""
    global _service_instance
    if _service_instance is None:
        _service_instance = AIAgentService()
    return _service_instance.find_road_agency_contacts(address, coordinates)


if __name__ == "__main__":
    test_addresses = {
        "Vladivostok": "Приморский край, г Владивосток, ул Светланская, 1",
    }
    for city_name, address in test_addresses.items():
        print(f"\n{'=' * 60}")
        print(f"Testing: {city_name}")
        print(f"{'=' * 60}")
        result = find_road_agency_contacts(address)
        print(json.dumps(result, ensure_ascii=False, indent=2))

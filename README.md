# Ямоборец

<div align="center">
  <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/7/75/Max_logo_2025.png/600px-Max_logo_2025.png" alt="MAX Logo" width="180"/>

  <p><strong>Сервис в MAX для обнаружения дорожных дефектов и автоматического формирования официальных обращений</strong></p>

  ![Python](https://img.shields.io/badge/Python-3.12-3776ab)
  ![FastAPI](https://img.shields.io/badge/FastAPI-0.120-009688)
  ![React](https://img.shields.io/badge/React-18-61dafb)
  ![Vue](https://img.shields.io/badge/Vue-3-4fc08d)
  ![YOLO](https://img.shields.io/badge/YOLO11-CV-orange)
  ![Docker](https://img.shields.io/badge/Docker_Compose-ready-2496ed)
</div>

---

## О проекте

**Ямоборец** помогает жителю за несколько минут превратить фотографию дорожной ямы в официальное обращение.

Пользователь открывает mini app в MAX, снимает дефект или загружает фотографии, после чего система:

1. обнаруживает ямы с помощью YOLO11;
2. рассчитывает уровень опасности;
3. определяет координаты и адрес;
4. находит ответственную дорожную организацию;
5. формирует заявление в DOCX/PDF;
6. отправляет заявление по электронной почте вместе с фотографиями;
7. уведомляет пользователя через MAX-бота;
8. отображает заявки на интерактивной карте и начисляет баллы.

Дополнительная документация: [DecodeMAX — Ямоборец](https://decodemax.yonote.ru/share/da62cda2-7468-4b95-8b6d-3d14f37f1852).

## Основные возможности

- CV-детекция дорожных ям на фото и видео;
- оценка риска и классификация `LOW / MEDIUM / HIGH / CRITICAL`;
- мобильный scanner с несколькими ракурсами;
- ручной ввод адреса, если iPhone или MAX WebView не предоставляет GPS;
- обратное геокодирование через DaData;
- поиск ответственной организации через DaData и GigaChat;
- автоматическое создание официального заявления;
- отправка через SMTP Яндекс Почты;
- локальное хранение обработанных фотографий и видео;
- карта дефектов, кластеры и тепловой слой;
- подтверждение дефекта другими жителями;
- профиль, уровни, очки и лидерборд;
- уведомления о ходе обработки в MAX;
- OpenAPI/Swagger для проверки backend API.

---

## Архитектура

```text
MAX Bot
   │
   ├── React Mini App ───── карта, профиль, заявки
   │
   └── Vue Web Scanner ─── камера, GPS, загрузка фото
              │
              ▼
        FastAPI Backend
       ├── YOLO11 / OpenCV
       ├── DaData
       ├── GigaChat
       ├── Яндекс SMTP
       ├── DOCX/PDF generator
       ├── Local media storage
       └── PostgreSQL
```

### Backend

- FastAPI и Uvicorn;
- SQLAlchemy Async + asyncpg;
- PostgreSQL 16;
- Alembic;
- Ultralytics YOLO11 и OpenCV;
- GigaChat API;
- DaData Suggestions API;
- MAX Bot API через `maxapi`;
- Яндекс SMTP;
- локальная раздача медиа через `/media`.

### Frontend

- `mini_app` — React 18, React Router, MaxUI, `mmr-gl`;
- `web_camera` — Vue 3, Element Plus, MediaDevices и Geolocation API;
- Vite для разработки и production-сборки.

### Хранение данных

- PostgreSQL хранит пользователей, заявки, статусы и статистику;
- обработанные файлы сохраняются в `backend/media`;
- Docker использует persistent volumes `pgdata` и `media_data`;
- S3 для текущей версии не требуется.

---

## Структура проекта

```text
MAX_assistant/
├── backend/
│   ├── alembic/                 # миграции БД
│   ├── core/                    # конфигурация, БД, FastAPI app
│   ├── cv_models/best.pt        # модель YOLO11
│   ├── media/                   # локальные фото и видео, не хранится в Git
│   ├── models/                  # SQLAlchemy-модели
│   ├── repositories/            # доступ к данным
│   ├── routers/                 # API endpoints
│   ├── schemas/                 # Pydantic-схемы
│   ├── services/                # CV, документы, почта, AI и уведомления
│   ├── Dockerfile
│   └── main.py
├── max_bot/                     # MAX-бот и клавиатуры
├── mini_app/                    # React mini app
├── web_camera/                  # Vue scanner
├── docker-compose.yaml
├── pyproject.toml
├── uv.lock
├── .env.example
└── Шаблон заявления.docx
```

---

## Предварительные требования

### Для Docker-запуска

- Docker Engine или Docker Desktop;
- Docker Compose v2;
- доступ в интернет для внешних API.

### Для локальной разработки

- Python 3.12;
- [uv](https://docs.astral.sh/uv/);
- Node.js 22+ и npm;
- PostgreSQL 16 или совместимая версия;
- HTTPS-туннель или домен для проверки внутри MAX.

### Внешние сервисы

Обязательны для полного сценария:

- токен MAX-бота;
- DaData API key;
- GigaChat credentials;
- аккаунт Яндекс Почты с паролем приложения.

Ключ VK Maps необязателен: без него карта использует резервный публичный стиль.

---

## Подготовка модели

Скачайте `best.pt` с [Яндекс Диска](https://disk.yandex.ru/d/BQkOm1xGN9l6hQ) и поместите файл строго по пути:

```text
backend/cv_models/best.pt
```

При запуске backend выводит `Модель найдена`. Если файла нет, CV endpoints не смогут обработать изображения.

---

## Переменные окружения

Создайте `.env` в корне репозитория:

```bash
cp .env.example .env
```

Не коммитьте `.env` и реальные ключи в Git.

### MAX и AI-интеграции

| Переменная | Назначение | Обязательность |
|---|---|---|
| `TOKEN_BOT` | токен MAX-бота | да |
| `DADATA_API_KEY` | геокодирование и поиск организаций | да |
| `GIGACHAT_CREDENTIALS` | Authorization data GigaChat в формате Base64 | да |
| `GIGACHAT_SCOPE` | scope GigaChat, обычно `GIGACHAT_API_PERS` | нет |

### Яндекс Почта

| Переменная | Значение |
|---|---|
| `YANDEX_SMTP_HOST` | `smtp.yandex.ru` |
| `YANDEX_SMTP_PORT` | `465` |
| `YANDEX_SMTP_USER` | полный адрес почты Яндекса |
| `YANDEX_SMTP_PASSWORD` | пароль приложения, не пароль аккаунта |
| `EMAIL_FROM_NAME` | отображаемое имя отправителя |

Для отправки используется SMTP over SSL. IMAP приложению не требуется.

### PostgreSQL

| Переменная | Локальный запуск | Docker Compose |
|---|---|---|
| `DB_HOST` | `localhost` | автоматически заменяется на `db` |
| `DB_PORT` | `5432` | `5432` |
| `DB_USER` | `postgres` | `postgres` |
| `DB_NAME` | `max_assistant` | `max_assistant` |
| `DB_PASS` | пароль PostgreSQL | пароль PostgreSQL |

Не используйте БД с чужой схемой. Проект ожидает таблицы, созданные его Alembic-миграциями.

### Backend

| Переменная | Значение по умолчанию |
|---|---|
| `HOST` | `localhost` |
| `PORT` | `8005` |
| `LOG_LEVEL` | `INFO` |

### Карта

Создайте `mini_app/.env` при наличии ключа VK Maps:

```env
VITE_VK_MAP_API=your_vk_maps_key
```

Не публикуйте настоящий ключ в README или репозитории.

---

## Быстрый запуск через Docker Compose

Docker Compose поднимает четыре сервиса:

- `db` — PostgreSQL, порт `5432`;
- `backend` — FastAPI и MAX-бот, порт `8005`;
- `web_camera` — scanner, порт `8006`;
- `mini_app` — React mini app, порт `8008`.

Запуск:

```bash
docker compose up --build -d
```

Backend ожидает готовности PostgreSQL, выполняет миграции и только затем запускает Uvicorn:

```text
alembic upgrade head → uvicorn backend.main:app
```

Проверка:

```bash
docker compose ps
docker compose logs -f backend
```

После запуска:

- API: `http://localhost:8005`;
- Swagger: `http://localhost:8005/docs`;
- OpenAPI: `http://localhost:8005/openapi.json`;
- scanner: `http://localhost:8006`;
- mini app: `http://localhost:8008`;
- локальные медиа: `http://localhost:8005/media/...`.

Данные сохраняются в Docker volumes и не пропадают после обычного перезапуска контейнеров.

> Для mini app и доступа к камере/GPS на телефоне необходим HTTPS. Локальные HTTP-адреса предназначены для разработки.

---

## Локальный запуск без Docker

Все Python-команды выполняются из корня репозитория.

### 1. Установка зависимостей

```bash
uv sync --frozen
```

Не используйте устаревший `backend/requirements.txt`: источником зависимостей являются `pyproject.toml` и `uv.lock`.

### 2. PostgreSQL

Создайте отдельную базу `max_assistant` и укажите её параметры в `.env`.

### 3. Миграции

```bash
uv run alembic -c backend/alembic/alembic.ini upgrade head
```

### 4. Backend и MAX-бот

```bash
uv run uvicorn backend.main:app --host localhost --port 8005
```

MAX-бот запускается внутри lifespan FastAPI. Отдельно запускать `max_bot/main.py` не требуется.

### 5. Scanner

```bash
cd web_camera
npm ci
npm run dev
```

Scanner будет доступен на `http://localhost:8006`.

### 6. Mini app

```bash
cd mini_app
npm ci
npm run dev
```

Mini app будет доступно на `http://localhost:8008`.

---

## Настройка публичных URL

Перед deployment замените адреса backend и scanner в:

- `mini_app/vite.config.js`;
- `web_camera/vite.config.js`.

Требования:

- `__BASE__PYTHON__URL__` и `__BASE__SCANNER__URL__` не должны заканчиваться `/`;
- `server.allowedHosts` содержит только hostname без `https://` и завершающего `/`;
- scanner и mini app должны открываться по HTTPS;
- ссылка `OpenAppButton` находится в `max_bot/keyboards.py` и должна соответствовать зарегистрированному mini app в MAX.

После изменения Vite-конфигурации требуется повторная сборка frontend.

---

## Основной сценарий проверки

1. Откройте бота `@t468_hakaton_max_bot` в MAX.
2. Нажмите нативную кнопку **«Начать»** или отправьте `/start`.
3. Нажмите **«Открыть приложение»**.
4. Выберите scanner или ручную загрузку.
5. Сделайте до 10 фотографий дорожного дефекта.
6. Разрешите камеру и геопозицию. Если GPS недоступен, укажите адрес вручную.
7. Запустите AI-анализ.
8. Проверьте найденные дефекты, уровни риска и адрес.
9. Создайте и отправьте заявление.
10. Проверьте уведомление в MAX, письмо с документом и фотографиями, профиль и карту.

---

## API

Основные группы endpoints:

- `/api/detect` — обработка фото и видео;
- `/api/reports` — черновики, отправка, карта, статистика и подтверждения;
- `/api/users` — регистрация, профиль, рейтинг и лидерборд;
- `/api/tasks` — задачи пользователя;
- `/media` — локально сохранённые обработанные файлы.

Полная актуальная схема доступна в Swagger и OpenAPI после запуска backend.

---

## Ограничения пилотной версии

- модель специализируется на дорожных ямах;
- качество CV зависит от освещения, ракурса и резкости снимка;
- контакты организаций зависят от полноты данных DaData и ответа GigaChat;
- фотографии хранятся локально; для промышленного масштабирования потребуются резервное копирование и распределённое хранилище;
- `docx2pdf` требует Microsoft Word, поэтому в Linux-контейнере заявление отправляется как DOCX;
- mini app, камера и GPS на мобильном устройстве требуют HTTPS;
- статус `отправлено` подтверждает передачу письма SMTP-серверу, но не гарантирует рассмотрение ведомством.

---

## Диагностика

### `uv.lock` не найден во время Docker build

Убедитесь, что сборка запускается из корня репозитория и `uv.lock` присутствует в Git:

```bash
ls -la uv.lock
docker compose build --no-cache backend
```

### `pywin32` не устанавливается на Linux

Используйте актуальные `pyproject.toml` и `uv.lock`. `pywin32` не является прямой зависимостью проекта и устанавливается `docx2pdf` только на Windows.

### Модель не найдена

Проверьте путь:

```text
backend/cv_models/best.pt
```

### Камера или GPS не работают

Проверьте HTTPS, разрешения браузера/iOS и откройте scanner во внешнем браузере. При отсутствии GPS можно продолжить с ручным адресом.

### Письмо не отправляется

Используйте пароль приложения Яндекса и проверьте переменные `YANDEX_SMTP_USER` и `YANDEX_SMTP_PASSWORD`.

---

## Безопасность

- не коммитьте `.env`, токены, SMTP-пароли и API-ключи;
- используйте отдельные test credentials для демонстрации;
- ограничьте доступ к серверу PostgreSQL в production;
- настройте HTTPS и reverse proxy;
- организуйте резервное копирование PostgreSQL и `backend/media`;
- перед публичным deployment ограничьте CORS доверенными доменами.

---

## Контакты

- GitHub: [Timsidorin/MAX_assistant](https://github.com/Timsidorin/MAX_assistant)
- Документация: [DecodeMAX — Ямоборец](https://decodemax.yonote.ru/share/da62cda2-7468-4b95-8b6d-3d14f37f1852)

<div align="center">
  <strong>Ямоборец — от фотографии дорожного дефекта до официального обращения.</strong>
</div>

# Ямоборец

<div align="center">
  <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/7/75/Max_logo_2025.png/600px-Max_logo_2025.png" alt="MAX Logo" width="200"/>
</div>

![AI Project](https://img.shields.io/badge/AI-Ямоборец-blue) 
![Python](https://img.shields.io/badge/Python-3.10-green) 
![FastAPI](https://img.shields.io/badge/FastAPI-API-red) 
![Docker](https://img.shields.io/badge/Docker-Ready-blue)
![React](https://img.shields.io/badge/React-Frontend-61dafb)
![Vue.js](https://img.shields.io/badge/Vue.js-Frontend-4fc08d)
![YOLO](https://img.shields.io/badge/YOLO11-CV-orange)

## 📋 О проекте

Документация проекта https://decodemax.yonote.ru/share/da62cda2-7468-4b95-8b6d-3d14f37f1852


**Ямоборец** — интеллектуальная система для автоматического обнаружения и анализа дорожных дефектов с использованием компьютерного зрения и современных веб-технологий.

---

## 🏗️ Архитектура системы

### **Backend Stack** 🖥️
- **FastAPI** - высокопроизводительный API фреймворк
- **PostgreSQL** - реляционная база данных
- **S3 VK** - облачное хранилище для медиафайлов
- **MailRu API** - интеграция с почтовыми сервисами
- **GigaChat API** - AI-ассистент для обработки данных
- **Docker** - контейнеризация приложения

### **Frontend Stack** 🌐
- **React** - библиотека для построения пользовательских интерфейсов
- **VueJS** - прогрессивный JavaScript фреймворк
- **MaxUIKit** - UI-библиотека от Mail.ru Group

### **Computer Vision** 👁️
- **Ultralytics YOLO11** - современная модель для детекции объектов

---

## ⚡ Быстрый старт

Для работы необходимо скачать модель для распознавания дорожных ям и поместить ее в папку проекта cv_models [https://drive.google.com/drive/folders/1-RHs2EtgeanoSNlOj6ZZBN2zhUpsnsob](https://disk.yandex.ru/d/BQkOm1xGN9l6hQ)


### Предварительные требования

- Docker и Docker Compose  
- Python 3.10+ (для локального запуска без Docker)  
- Доступ к API сервисам (GigaChat, MailRu SMTP, S3 VK Cloud, Telegram Bot, Dadata)  
- Настроенная база данных PostgreSQL (локальная или в Docker)  

### Установка и запуск

1. **Клонирование репозитория**

git clone https://github.com/Timsidorin/MAX_assistant
cd MAX_assistant


2. **Настройка переменных окружения**

Создайте файл `.env` в корне проекта (по аналогии с `.env.example`) и укажите все ключи:

#Bot
TOKEN_BOT=your_telegram_bot_token_here
WEBAPP_URL=your_webapp_url_here

#Dadata API
DADATA_API_KEY=your_dadata_api_key_here

#GigaChat API
GIGACHAT_CREDENTIALS=your_gigachat_authorization_key_here

#Mail.ru SMTP
MAILRU_SMTP_USER=your_mailru_smtp_user_here
MAILRU_SMTP_PASSWORD=your_mailru_smtp_password_here

#База данных
DB_USER=your_database_user_here
DB_NAME=your_database_name_here
DB_PASS=your_database_password_here
DB_HOST=db_or_localhost_here
DB_PORT=5432

#S3 хранилище VK Cloud
AWS_ACCESS_KEY_ID=your_aws_access_key_here
AWS_SECRET_ACCESS_KEY=your_aws_secret_key_here
S3_BUCKET_NAME=your_s3_bucket_name_here
S3_ENDPOINT_URL=your_s3_endpoint_url_here
S3_REGION_NAME=ru-msk


3. **Запуск через Docker (рекомендуемый способ)**
docker-compose up -d --build

После первого запуска:

- API будет доступен по адресу `http://localhost:8005`  
- бот начнёт работать (при корректно настроенных `TOKEN_BOT` и `WEBAPP_URL`)  

4. **Локальный запуск без Docker (опционально, для разработки)**

python -m venv venv
source venv/bin/activate # Linux / macOS

venv\Scripts\activate # Windows
pip install -r requirements.txt


Примените миграции к базе данных:

alembic upgrade head
Запустите API сервер и бота:

API + BOT 
python api/main.py


5. **Проверка работы**
- Откройте MAX, найдите бота и отправьте команду `/start`  
- Загрузите фото с дорожной ямой  
- Убедитесь, что:
  - дефект распознан моделью  
  - данные сохранены в БД  
  - файл/результаты при необходимости отправлены в S3 или по почте  



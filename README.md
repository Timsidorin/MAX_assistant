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
- Доступ к API сервисам (GigaChat, MailRu, S3 VK)

### Установка и запуск

1. **Клонирование репозитория**
```bash
git clone https://github.com/your-organization/yamoborets.git
cd yamoborets

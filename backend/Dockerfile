FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


COPY . .

COPY ../.env .env

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

EXPOSE 8005

CMD ["/bin/bash", "-c", "python backend/main.py"]
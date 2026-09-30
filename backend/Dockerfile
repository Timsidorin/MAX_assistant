FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir uv

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project && uv cache clean

COPY backend ./backend
COPY max_bot ./max_bot
COPY ["Шаблон заявления.docx", "./Шаблон заявления.docx"]

ENV PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PATH="/app/.venv/bin:$PATH"

EXPOSE 8005

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8005"]

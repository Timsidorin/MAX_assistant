FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir uv

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project --no-install-package torch --no-install-package torchvision
RUN uv pip install torch==2.9.0 torchvision==0.24.0 --index-url https://download.pytorch.org/whl/cpu
RUN uv cache clean

COPY backend ./backend
COPY max_bot ./max_bot
COPY ["Шаблон заявления.docx", "./Шаблон заявления.docx"]

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8005

CMD ["sh", "-c", "uvicorn backend.main:app --host 0.0.0.0 --port 8005"]

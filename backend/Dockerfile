FROM python:3.12-slim

WORKDIR /app

RUN pip install --no-cache-dir uv

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

COPY backend ./backend
COPY max_bot ./max_bot

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8005

CMD ["sh", "-c", "alembic -c backend/alembic/alembic.ini upgrade head && uvicorn backend.main:app --host 0.0.0.0 --port 8005"]

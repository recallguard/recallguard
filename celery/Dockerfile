FROM python:3.12-slim AS build
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend     ./backend
COPY alembic     ./alembic
COPY alembic.ini ./alembic.ini
COPY run.py      ./run.py

# ───────── runtime  ─────────
FROM python:3.12-slim
WORKDIR /app
ENV PYTHONUNBUFFERED=1 PATH=/root/.local/bin:$PATH

COPY --from=build /usr/local/lib/python*/site-packages /usr/local/lib/python*/site-packages
COPY --from=build /app /app

CMD ["celery", "-A", "backend.tasks", "worker", "--loglevel=info"]

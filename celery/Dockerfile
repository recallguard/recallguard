FROM python:3.12-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

FROM python:3.12-slim
ENV PYTHONUNBUFFERED=1
WORKDIR /app
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH
COPY backend backend
COPY alembic alembic
COPY alembic.ini alembic.ini
CMD ["celery", "-A", "backend.tasks", "worker", "--loglevel=info"]

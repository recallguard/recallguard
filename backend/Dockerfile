# ───────── Stage 1 – build ─────────
FROM python:3.12-slim AS build
WORKDIR /app

# 1  install Python deps (cache-friendly)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 2  copy project
COPY backend     ./backend
COPY alembic     ./alembic
COPY alembic.ini ./alembic.ini
COPY run.py      ./run.py

# ───────── Stage 2 – runtime ───────
FROM python:3.12-slim
WORKDIR /app
ENV PYTHONUNBUFFERED=1 PATH=/root/.local/bin:$PATH

# copy installed deps + source from build stage
COPY --from=build /usr/local/lib/python*/site-packages /usr/local/lib/python*/site-packages
COPY --from=build /app /app

CMD ["python", "run.py"]

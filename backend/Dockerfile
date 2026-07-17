FROM python:3.13-alpine AS base

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt && \
    addgroup -S appgroup && adduser -S appuser -G appgroup

COPY --chown=appuser:appgroup . .

FROM base AS development
# НЕ переключаемся на appuser

FROM base AS production
USER appuser
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

FROM base AS worker
USER appuser
CMD ["taskiq", "worker", "app.modules.market.taskiq_setup:broker", "app.modules.market.tasks", "app.modules.auth.tasks"]

FROM base AS test
COPY requirements-test.txt ./
RUN pip install --no-cache-dir -r requirements-test.txt
# НЕ переключаемся на appuser, чтобы тесты могли создавать отчеты

FROM base AS scheduler
USER appuser
CMD ["taskiq", "scheduler", "app.modules.market.taskiq_setup:scheduler"]

FROM python:3.13-alpine AS base

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt && \
    addgroup -S appgroup && adduser -S appuser -G appgroup

COPY --chown=appuser:appgroup . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

FROM base AS test
COPY requirements-test.txt ./
RUN pip install --no-cache-dir -r requirements-test.txt
# НЕ переключаемся на appuser, чтобы тесты могли создавать отчеты
# USER appuser

FROM base AS development
USER appuser

FROM base AS production
USER appuser

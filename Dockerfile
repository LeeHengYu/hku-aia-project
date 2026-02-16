# syntax=docker/dockerfile:1

FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY requirements-backend.txt ./
RUN pip install --no-cache-dir -r requirements-backend.txt

COPY web/backend ./web/backend

RUN adduser --disabled-password --gecos "" --uid 10001 appuser \
    && chown -R appuser:appuser /app

USER appuser

EXPOSE 8080
CMD ["sh", "-c", "uvicorn web.backend.main:app --host 0.0.0.0 --port ${PORT:-8080}"]

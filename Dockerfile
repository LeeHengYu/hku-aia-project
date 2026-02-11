# syntax=docker/dockerfile:1

FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements-backend.txt ./
RUN pip install --no-cache-dir -r requirements-backend.txt

COPY web/backend ./web/backend
COPY google-vertexai ./google-vertexai

EXPOSE 8080
CMD ["uvicorn", "web.backend.main:app", "--host", "0.0.0.0", "--port", "8080"]

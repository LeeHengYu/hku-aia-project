# syntax=docker/dockerfile:1

FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    CORS_ORIGINS="http://localhost:5173,http://127.0.0.1:5173,https://hku-aia-project.vercel.app" \
    VERTEX_PROJECT_ID="project-b8819359-0bf9-4214-88d" \
    VERTEX_LOCATION="global"

WORKDIR /app

COPY requirements-backend.txt ./
RUN pip install --no-cache-dir -r requirements-backend.txt

COPY web/backend ./web/backend

EXPOSE 8080
CMD ["uvicorn", "web.backend.main:app", "--host", "0.0.0.0", "--port", "8080"]

FROM node:20-slim AS frontend-builder
WORKDIR /build
COPY telemetrydashboard/frontend/package.json telemetrydashboard/frontend/package-lock.json* ./
RUN npm ci
COPY telemetrydashboard/frontend/ ./
RUN npm run build

FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/*

COPY telemetrydashboard/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY telemetrydashboard/app/ ./app/
COPY telemetrydashboard/collector/ ./collector/
COPY --from=frontend-builder /build/dist/ ./frontend/dist/

EXPOSE 8002

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8002}/health || exit 1

CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8002}

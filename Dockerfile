FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/*

COPY telemetrydashboard/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY telemetrydashboard/app/ ./app/
COPY telemetrydashboard/collector/ ./collector/

EXPOSE 8002

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8002}/health || exit 1

CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8002}

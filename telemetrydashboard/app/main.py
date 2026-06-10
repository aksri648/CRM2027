from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from datetime import datetime
import asyncio

from .telemetry import (
    tracer, meter, log_storage, metric_storage,
    collect_all_metrics, log_event, request_counter, request_duration
)

app = FastAPI(title="Telemetry Dashboard", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request timing middleware
@app.middleware("http")
async def track_requests(request, call_next):
    start_time = datetime.utcnow()
    request_counter.add(1, {"endpoint": request.url.path, "method": request.method})
    
    response = await call_next(request)
    
    duration = (datetime.utcnow() - start_time).total_seconds() * 1000
    request_duration.record(duration, {"endpoint": request.url.path, "method": request.method})
    
    return response

# Health endpoint
@app.get("/health")
async def health():
    return {"status": "healthy", "service": "telemetry-dashboard", "timestamp": datetime.utcnow().isoformat()}

# Metrics endpoints
@app.get("/api/v1/metrics")
async def get_all_metrics():
    """Get all collected metrics"""
    return await collect_all_metrics()

@app.get("/api/v1/metrics/services")
async def get_service_metrics():
    """Get metrics from all services"""
    return await collect_all_metrics()

@app.get("/api/v1/metrics/summary")
async def get_metrics_summary():
    """Get metrics summary"""
    metrics = await metric_storage.get_metrics()
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "metrics": metrics
    }

# Logs endpoints
@app.get("/api/v1/logs")
async def get_logs(
    limit: int = 100,
    service: Optional[str] = None,
    level: Optional[str] = None
):
    """Get logs with optional filtering"""
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "logs": await log_storage.get_logs(limit, service, level)
    }

@app.get("/api/v1/logs/services/{service_name}")
async def get_service_logs(service_name: str, limit: int = 100):
    """Get logs for a specific service"""
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "service": service_name,
        "logs": await log_storage.get_logs(limit, service=service_name)
    }

# Traces endpoint
@app.get("/api/v1/traces")
async def get_traces(limit: int = 50):
    """Get recent traces (simplified - in production use proper trace storage)"""
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "message": "Trace storage not implemented - use OTLP exporter for production"
    }

# Service status
@app.get("/api/v1/status")
async def get_status():
    """Get overall system status"""
    metrics = await collect_all_metrics()
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "status": "healthy" if metrics["summary"]["healthy_count"] == 2 else "degraded",
        "services": metrics["services"],
        "summary": metrics["summary"]
    }

# Log ingestion endpoint (for services to send logs)
class LogEntry(BaseModel):
    level: str
    message: str
    service: str
    metadata: Optional[Dict[str, Any]] = None

@app.post("/api/v1/logs")
async def ingest_log(entry: LogEntry):
    """Ingest logs from other services"""
    await log_event(entry.level, entry.message, entry.service, entry.metadata)
    return {"status": "ok"}

# Metric ingestion endpoint
class MetricEntry(BaseModel):
    name: str
    value: float
    labels: Optional[Dict[str, str]] = None

@app.post("/api/v1/metrics")
async def ingest_metric(entry: MetricEntry):
    """Ingest metrics from other services"""
    await metric_storage.record_metric(entry.name, entry.value, entry.labels)
    return {"status": "ok"}

# Background task to collect metrics periodically
async def metrics_collector_task():
    while True:
        try:
            await collect_all_metrics()
            await log_event("info", "Metrics collected successfully", "telemetry_dashboard")
        except Exception as e:
            await log_event("error", f"Failed to collect metrics: {str(e)}", "telemetry_dashboard")
        await asyncio.sleep(30)  # Collect every 30 seconds

@app.on_event("startup")
async def startup():
    asyncio.create_task(metrics_collector_task())
    await log_event("info", "Telemetry dashboard started", "telemetry_dashboard")

@app.on_event("shutdown")
async def shutdown():
    await log_event("info", "Telemetry dashboard stopped", "telemetry_dashboard")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
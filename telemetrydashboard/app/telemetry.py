import logging
from opentelemetry import trace, metrics
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.resources import Resource, SERVICE_NAME, SERVICE_VERSION
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.sdk.metrics.export import ConsoleMetricExporter, PeriodicExportingMetricReader
from opentelemetry.trace import Status, StatusCode
from datetime import datetime
from typing import Dict, Any, List, Optional
import asyncio

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Resource with service info
resource = Resource.create({
    SERVICE_NAME: "telemetry-dashboard",
    SERVICE_VERSION: "1.0.0",
    "deployment.environment": "development"
})

# Set up tracing
trace_provider = TracerProvider(resource=resource)
trace_provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))
trace.set_tracer_provider(trace_provider)

# Set up metrics
metric_reader = PeriodicExportingMetricReader(ConsoleMetricExporter(), export_interval_millis=10000)
meter_provider = MeterProvider(resource=resource, metric_readers=[metric_reader])
metrics.set_meter_provider(meter_provider)

# Get tracer and meter
tracer = trace.get_tracer(__name__)
meter = metrics.get_meter(__name__)

# Custom metrics
request_counter = meter.create_counter(
    name="telemetry.requests.total",
    description="Total number of requests",
    unit="1"
)

request_duration = meter.create_histogram(
    name="telemetry.request.duration",
    description="Request duration in milliseconds",
    unit="ms"
)

# Log storage (in-memory for demo, use proper storage in production)
class LogStorage:
    def __init__(self, max_logs: int = 1000):
        self.max_logs = max_logs
        self._logs: List[Dict[str, Any]] = []
        self._lock = asyncio.Lock()
    
    async def add_log(self, log_entry: Dict[str, Any]):
        async with self._lock:
            self._logs.append({
                "timestamp": datetime.utcnow().isoformat(),
                **log_entry
            })
            if len(self._logs) > self.max_logs:
                self._logs = self._logs[-self.max_logs:]
    
    async def get_logs(self, limit: int = 100, service: Optional[str] = None, level: Optional[str] = None) -> List[Dict[str, Any]]:
        async with self._lock:
            logs = self._logs
            if service:
                logs = [l for l in logs if l.get("service") == service]
            if level:
                logs = [l for l in logs if l.get("level") == level]
            return logs[-limit:]

log_storage = LogStorage()

# Metric storage
class MetricStorage:
    def __init__(self):
        self._metrics: Dict[str, List[Dict[str, Any]]] = {}
        self._lock = asyncio.Lock()
    
    async def record_metric(self, name: str, value: float, labels: Dict[str, str] = None):
        async with self._lock:
            if name not in self._metrics:
                self._metrics[name] = []
            self._metrics[name].append({
                "timestamp": datetime.utcnow().isoformat(),
                "value": value,
                "labels": labels or {}
            })
            # Keep last 100 values per metric
            if len(self._metrics[name]) > 100:
                self._metrics[name] = self._metrics[name][-100:]
    
    async def get_metrics(self, name: Optional[str] = None) -> Dict[str, List[Dict[str, Any]]]:
        async with self._lock:
            if name:
                return {name: self._metrics.get(name, [])}
            return self._metrics.copy()

metric_storage = MetricStorage()

# Service endpoints - read from environment variables
from os import getenv
APP_SERVICE_URL = getenv("APP_SERVICE_URL", "http://localhost:8000")
CHANNEL_SERVICE_URL = getenv("CHANNEL_SERVICE_URL", "http://localhost:8001")

async def fetch_service_metrics(service_name: str, base_url: str) -> Dict[str, Any]:
    """Fetch metrics from a service using OpenTelemetry context"""
    with tracer.start_as_current_span(f"fetch.{service_name}.metrics") as span:
        span.set_attribute("service.name", service_name)
        span.set_attribute("service.url", base_url)
        
        try:
            import httpx
            # 60s timeout absorbs Render free-tier cold starts (~30-60s)
            async with httpx.AsyncClient(timeout=60.0) as client:
                # Fetch health
                health_response = await client.get(f"{base_url}/health")
                health_data = health_response.json() if health_response.status_code == 200 else {}

                span.set_status(Status(StatusCode.OK))

                return {
                    "service": service_name,
                    "url": base_url,
                    "status": "healthy" if health_response.status_code == 200 else "unhealthy",
                    "health": health_data,
                    "stats": {},
                    "timestamp": datetime.utcnow().isoformat()
                }
        except Exception as e:
            span.set_status(Status(StatusCode.ERROR, str(e)))
            span.record_exception(e)
            logger.error(f"Failed to fetch metrics from {service_name}: {e}")
            return {
                "service": service_name,
                "url": base_url,
                "status": "unreachable",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }

async def collect_all_metrics() -> Dict[str, Any]:
    """Collect metrics from all monitored services"""
    with tracer.start_as_current_span("collect.all.metrics") as span:
        start_time = datetime.utcnow()
        
        # Collect from both services concurrently
        app_metrics, channel_metrics = await asyncio.gather(
            fetch_service_metrics("app_service", APP_SERVICE_URL),
            fetch_service_metrics("channel_service", CHANNEL_SERVICE_URL)
        )
        
        # Record metric about collection
        await metric_storage.record_metric(
            "telemetry.collection.duration",
            (datetime.utcnow() - start_time).total_seconds() * 1000,
            {"service": "telemetry_dashboard"}
        )
        
        await metric_storage.record_metric(
            "telemetry.service.status",
            1.0 if app_metrics["status"] == "healthy" else 0.0,
            {"service": "app_service"}
        )
        
        await metric_storage.record_metric(
            "telemetry.service.status",
            1.0 if channel_metrics["status"] == "healthy" else 0.0,
            {"service": "channel_service"}
        )
        
        span.set_attribute("app_service.status", app_metrics["status"])
        span.set_attribute("channel_service.status", channel_metrics["status"])
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "services": {
                "app_service": app_metrics,
                "channel_service": channel_metrics
            },
            "summary": {
                "total_services": 2,
                "healthy_count": sum(1 for s in [app_metrics, channel_metrics] if s["status"] == "healthy"),
                "unhealthy_count": sum(1 for s in [app_metrics, channel_metrics] if s["status"] != "healthy")
            }
        }

# Logging helper
async def log_event(level: str, message: str, service: str, metadata: Dict[str, Any] = None):
    """Log an event with OpenTelemetry context"""
    log_entry = {
        "level": level,
        "message": message,
        "service": service,
        "metadata": metadata or {}
    }
    
    # Log to console (in production, use proper OTLP exporter)
    log_message = f"[{service}] {level.upper()}: {message}"
    if metadata:
        log_message += f" | {metadata}"
    
    if level == "error":
        logger.error(log_message)
    elif level == "warning":
        logger.warning(log_message)
    elif level == "debug":
        logger.debug(log_message)
    else:
        logger.info(log_message)
    
    await log_storage.add_log(log_entry)
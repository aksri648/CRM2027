# OpenTelemetry Observability Implementation

This document describes the OpenTelemetry observability implementation for the monorepo services.

## Architecture

```
┌─────────────────┐     OTLP      ┌──────────────────────┐
│     backend     │──────────────▶│                      │
│  (FastAPI)      │   HTTP/4318   │   telemetry-dashboard │
└─────────────────┘               │   ┌────────────────┐  │
                                 │   │ OTEL Collector │  │
┌─────────────────────┐          │   │   (Receiver)   │  │
│ channelization-     │──────────▶│   └───────┬────────┘  │
│ microservice        │          │           │           │
│  (FastAPI)          │          │   ┌───────▼────────┐  │
└─────────────────────┘          │   │  Processors    │  │
                                 │   │  - batch       │  │
                                 │   │  - memory      │  │
                                 │   │  - transform   │  │
                                 │   └───────┬────────┘  │
                                 │           │           │
                                 │   ┌───────▼────────┐  │
                                 │   │   Exporters    │  │
                                 │   │  - logging     │  │
                                 │   │  - file        │  │
                                 │   │  - (prometheus)│  │
                                 │   │  - (loki)      │  │
                                 │   │  - (tempo)     │  │
                                 │   └───────────────┘  │
                                 └──────────────────────┘
```

## Services Instrumented

### 1. backend

Python FastAPI service providing CRM functionality.

**Telemetry Module:** `backend/telemetry/`

### 2. channelization-microservice

Python FastAPI service handling message delivery simulation.

**Telemetry Module:** `channel_service/telemetry/`

### 3. telemetry-dashboard

Python FastAPI service with OTEL Collector for telemetry ingestion.

**Collector Config:** `telemetrydashboard/collector/otel-collector-config.yaml`

---

## Metrics Collected

### Runtime Metrics (Auto-instrumented)

| Metric Name | Type | Description |
|-------------|------|-------------|
| `process.runtime.cpu_time` | Gauge | CPU time used by the process |
| `process.runtime.memory_usage` | Gauge | Memory usage in bytes |
| `process.runtime.thread_count` | Gauge | Number of active threads |
| `process.runtime.gc_count` | Counter | Garbage collection invocation count |

### HTTP Request Metrics (Auto-instrumented via FastAPI instrumentation)

| Metric Name | Type | Description |
|-------------|------|-------------|
| `http.server.request.duration` | Histogram | Request duration in milliseconds |
| `http.server.request.count` | Counter | Total request count |

### Custom Business Metrics

#### backend

| Metric Name | Type | Labels | Description |
|-------------|------|--------|-------------|
| `backend.requests.total` | Counter | `method`, `endpoint`, `status_code` | Total HTTP requests |
| `backend.request.duration` | Histogram | `method`, `endpoint`, `status_code` | Request duration |
| `backend.active.requests` | UpDownCounter | - | Active request count |
| `backend.messages.processed.total` | Counter | `channel` | Messages processed |
| `backend.messages.failed.total` | Counter | `channel`, `error_type` | Message failures |

#### channelization-microservice

| Metric Name | Type | Labels | Description |
|-------------|------|--------|-------------|
| `channelization.requests.total` | Counter | `method`, `endpoint`, `status_code` | Total HTTP requests |
| `channelization.request.duration` | Histogram | `method`, `endpoint`, `status_code` | Request duration |
| `channelization.active.requests` | UpDownCounter | - | Active request count |
| `channelization.messages.sent.total` | Counter | `channel` | Messages sent |
| `channelization.messages.failed.total` | Counter | `channel`, `error_type` | Send failures |
| `channelization.delivery.duration` | Histogram | `channel` | Delivery duration |

---

## Logs Collected

### Log Format (JSON)

All logs are structured JSON with the following fields:

```json
{
  "service": "backend",
  "timestamp": "2024-01-15T10:30:00.000Z",
  "level": "INFO",
  "message": "Request processed",
  "logger": "app.api.v1.campaigns",
  "module": "campaigns",
  "function": "get_campaigns",
  "line": 42,
  "trace_id": "abc123def456...",
  "span_id": "789xyz..."
}
```

### Log Levels

- `DEBUG`: Detailed debugging information
- `INFO`: General operational information
- `WARNING`: Warning conditions
- `ERROR`: Error conditions
- `CRITICAL`: Critical failures

### Trace Context

Logs automatically include `trace_id` and `span_id` when available, enabling correlation between logs, metrics, and traces.

---

## Traces Collected

### Trace Structure

```
Trace
└── Span (root)
    ├── Span (HTTP request)
    │   ├── Span (database query)
    │   └── Span (external API call)
    └── Span (background task)
```

### Span Attributes

| Attribute | Description |
|-----------|-------------|
| `service.name` | Service identifier |
| `service.version` | Service version |
| `deployment.environment` | Environment (dev/prod) |
| `http.method` | HTTP method |
| `http.url` | Request URL |
| `http.status_code` | Response status |
| `http.target` | Request path |

### Sampling

Trace sampling rate is configurable via `OTEL_TRACE_SAMPLING_RATE` (default: 10%).

---

## Environment Configuration

### backend / channelization-microservice

```bash
# Service identification
OTEL_SERVICE_NAME="backend"
OTEL_SERVICE_VERSION="1.0.0"
DEPLOYMENT_ENVIRONMENT="production"

# OTEL Collector endpoint
OTEL_EXPORTER_OTLP_ENDPOINT="http://telemetry-dashboard:4318"
OTEL_EXPORTER_OTLP_PROTOCOL="http/protobuf"
OTEL_EXPORTER_TIMEOUT="10"

# Tracing
OTEL_TRACE_SAMPLING_RATE="0.1"
OTEL_TRACE_EXPORT_INTERVAL="5000"

# Metrics
OTEL_METRICS_EXPORT_INTERVAL="30000"

# Logging
OTEL_LOG_LEVEL="INFO"
```

### telemetry-dashboard

```bash
# OTEL Collector endpoints
OTEL_COLLECTOR_ENDPOINT="http://localhost:4318"
OTEL_COLLECTOR_HTTP_ENDPOINT="http://localhost:4318"
OTEL_COLLECTOR_GRPC_ENDPOINT="localhost:4317"
```

---

## Deployment Instructions

### Local Development

1. **Start the OTEL Collector:**

```bash
cd telemetrydashboard
docker compose -f docker/docker-compose.yml up -d
```

2. **Start backend with telemetry:**

```bash
cd backend
pip install -r requirements.txt
export OTEL_EXPORTER_OTLP_ENDPOINT="http://localhost:4318"
export OTEL_SERVICE_NAME="backend"
export DEPLOYMENT_ENVIRONMENT="development"
uvicorn app.main:app --reload
```

3. **Start channelization-microservice with telemetry:**

```bash
cd channel_service
pip install -r requirements.txt
export OTEL_EXPORTER_OTLP_ENDPOINT="http://localhost:4318"
export OTEL_SERVICE_NAME="channelization-microservice"
export DEPLOYMENT_ENVIRONMENT="development"
uvicorn app.main:app --reload --port 8001
```

4. **Start telemetry-dashboard:**

```bash
cd telemetrydashboard
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Render Deployment

1. **Deploy OTEL Collector:**

```bash
cd telemetrydashboard
docker build -f docker/Dockerfile.collector -t otel-collector .
docker push your-registry/otel-collector
```

2. **Set environment variables in Render dashboard:**

For **backend**:
```
OTEL_SERVICE_NAME=backend
OTEL_EXPORTER_OTLP_ENDPOINT=http://telemetry-dashboard:4318
OTEL_TRACE_SAMPLING_RATE=0.1
DEPLOYMENT_ENVIRONMENT=production
```

For **channelization-microservice**:
```
OTEL_SERVICE_NAME=channelization-microservice
OTEL_EXPORTER_OTLP_ENDPOINT=http://telemetry-dashboard:4318
OTEL_TRACE_SAMPLING_RATE=0.1
DEPLOYMENT_ENVIRONMENT=production
```

---

## Validation Steps

### Verify Metrics Arriving

1. Check OTEL collector logs:
```bash
docker logs otel-collector 2>&1 | grep -i metric
```

2. Query the telemetry dashboard metrics endpoint:
```bash
curl http://localhost:8000/api/v1/metrics
```

3. Check Prometheus endpoint (if enabled):
```bash
curl http://localhost:8889/metrics
```

### Verify Logs Arriving

1. Check OTEL collector logs:
```bash
docker logs otel-collector 2>&1 | grep -i log
```

2. Query the telemetry dashboard logs endpoint:
```bash
curl http://localhost:8000/api/v1/logs
```

3. Check file exporter output:
```bash
cat telemetrydashboard/telemetry_data/telemetry.json | jq .
```

### Verify Traces Arriving

1. Check OTEL collector logs:
```bash
docker logs otel-collector 2>&1 | grep -i trace
```

2. Enable debug logging in collector config and observe span exports.

---

## Failure Safety

The implementation ensures telemetry failures never impact application functionality:

1. **Async Exporters**: All exporters use async processing (BatchSpanProcessor, PeriodicExportingMetricReader, BatchLogRecordProcessor)

2. **Graceful Degradation**: If collector is unavailable, services continue operating normally

3. **No Blocking**: Telemetry initialization errors are caught and logged, but do not prevent application startup

4. **Queue Limits**: Exporters have bounded queues (2048 items) to prevent memory exhaustion

5. **Timeout Protection**: All exporters have configurable timeouts (default 10s)

---

## Future Integrations

The collector config is prepared for future integrations:

### Prometheus (Metrics)

Uncomment in `otel-collector-config.yaml`:
```yaml
prometheus:
  endpoint: "0.0.0.0:8889"
  resource_to_telemetry_conversion:
    enabled: true
```

### Loki (Logs)

```yaml
loki:
  endpoint: "http://loki:3100/loki/api/v1/push"
  labels:
    attributes:
      service.name: service
```

### Tempo (Traces)

```yaml
otlp/tempo:
  endpoint: "tempo:4317"
  tls:
    insecure: true
```

---

## File Structure

```
/
├── backend/
│   ├── telemetry/
│   │   ├── __init__.py      # Telemetry initialization
│   │   ├── config.py        # Configuration from env
│   │   ├── tracing.py       # Tracing setup
│   │   ├── metrics.py       # Metrics setup
│   │   └── logging.py       # Structured logging
│   ├── requirements.txt     # Updated with OTel deps
│   ├── .env.example         # Updated with OTel config
│   └── app/main.py          # Telemetry init added
│
├── channel_service/
│   ├── telemetry/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── tracing.py
│   │   ├── metrics.py
│   │   └── logging.py
│   ├── requirements.txt
│   ├── .env.example
│   └── app/main.py
│
├── telemetrydashboard/
│   ├── collector/
│   │   └── otel-collector-config.yaml
│   ├── docker/
│   │   ├── Dockerfile.collector
│   │   └── docker-compose.yml
│   ├── requirements.txt
│   └── .env.example
│
└── docs/
    └── observability.md     # This document
```

---

## Troubleshooting

### Telemetry not appearing

1. Verify collector is running: `docker ps | grep otel`
2. Check collector logs: `docker logs otel-collector`
3. Verify endpoint configuration matches between services and collector
4. Check network connectivity between services

### High memory usage

1. Reduce batch sizes in collector config
2. Lower export intervals
3. Increase sampling rate reduction

### Application slow startup

1. Telemetry initialization is wrapped in try/except - should not block
2. Check for network timeouts when connecting to collector
3. Verify OTEL_EXPORTER_TIMEOUT is not too high

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2024-01-15 | Initial implementation |
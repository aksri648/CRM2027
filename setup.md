# Setup: Fix Telemetry Dashboard "Failed to Fetch Metrics" on Render

This document is a complete, deterministic recipe. Follow every step in order. Do not improvise. All file paths are absolute from the repository root `/home/akshat/Project/`.

You have these tools:
- File editing (Read/Edit/Write)
- Bash (`gh` CLI is authenticated)
- Render MCP server (tools prefixed `mcp__render__*`)

---

## 0. Background — read once, then proceed

**Architecture** (all on Render free tier):

| Service | Render name | Type | Public URL |
|---|---|---|---|
| Backend | `xeno-crm-2027-backend` | Python web | `https://xeno-crm-2027-backend.onrender.com` |
| Channel | `xeno-crm-2027-channel` | Python web | `https://xeno-crm-2027-channel.onrender.com` |
| Frontend | `xeno-crm-2027-frontend` | Node web | `https://xeno-crm-2027-frontend.onrender.com` |
| Telemetry dashboard | `xeno-crm-2027-telemetry` | Docker web | `https://xeno-crm-2027-telemetry.onrender.com` |

**Service IDs** (use these with Render MCP):
- Backend: `srv-d8ku7hkvikkc73c6udcg`
- Channel: `srv-d8ku7i0js32c73bpnde0`
- Frontend: `srv-d8ku7im7r5hc739e63d0`
- Telemetry: `srv-d8ku7lmrnols73c5b960`

**Data flow expected after the fix:**
1. Backend and Channel services PUSH OTLP HTTP/protobuf to `https://xeno-crm-2027-telemetry.onrender.com/v1/{metrics,logs,traces}`.
2. Telemetry dashboard FastAPI ALSO PULLs `/health` from Backend and Channel every 60 s as a liveness check.
3. React dashboard frontend GETs `/api/v1/metrics`, `/api/v1/logs`, `/api/v1/status` from the same FastAPI app it's served from.

**Bugs that cause "Failed to fetch metrics":**
1. `StaticFiles` mount at `"/"` registered before API routes — Starlette matches mount first, returns 404 for `/api/v1/*`.
2. No OTLP receiver exists — services PUSH to URLs that 404.
3. `httpx` timeout of 5 s in the PULL aggregator dies during Render cold starts (30–60 s).
4. `/stats` endpoint doesn't exist on Backend or Channel — dashboard calls it and swallows the error.

---

## 1. Verify you are on the right branch and tree is clean

```bash
cd /home/akshat/Project
git status
git branch --show-current
```

Expected: branch `master`, working tree clean except for `memory.md` (untracked, leave it alone).

If the branch is not `master`, stop and ask.

---

## 2. Apply the four code changes

### 2.1 Edit `telemetrydashboard/app/main.py`

There are FOUR edits to this file. Apply them in order.

**Edit A — remove the early static mount (line 17-19 originally).**

Find this block:
```python
app = FastAPI(title="Telemetry Dashboard", version="1.0.0")

frontend_dist = os.path.join(os.path.dirname(__file__), "..", "frontend", "dist")
if os.path.isdir(frontend_dist):
    app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="frontend")

# CORS
```

Replace with:
```python
app = FastAPI(title="Telemetry Dashboard", version="1.0.0")

frontend_dist = os.path.join(os.path.dirname(__file__), "..", "frontend", "dist")

# CORS
```

**Edit B — import the OTLP router.**

Find:
```python
from .telemetry import (
    tracer, meter, log_storage, metric_storage,
    collect_all_metrics, log_event, request_counter, request_duration
)
```

Replace with:
```python
from .telemetry import (
    tracer, meter, log_storage, metric_storage,
    collect_all_metrics, log_event, request_counter, request_duration
)
from .otlp_receiver import router as otlp_router
```

**Edit C — include the OTLP router after CORS.**

Find:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request timing middleware
```

Replace with:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(otlp_router)

# Request timing middleware
```

**Edit D — bump polling interval, mount static files at the END.**

Find:
```python
        await asyncio.sleep(30)  # Collect every 30 seconds
```

Replace with:
```python
        await asyncio.sleep(60)  # Services push every 30s; poll for health once a minute
```

Find:
```python
@app.on_event("shutdown")
async def shutdown():
    await log_event("info", "Telemetry dashboard stopped", "telemetry_dashboard")

if __name__ == "__main__":
```

Replace with:
```python
@app.on_event("shutdown")
async def shutdown():
    await log_event("info", "Telemetry dashboard stopped", "telemetry_dashboard")

# Mount static frontend LAST so /api/* and /v1/* routes match first
if os.path.isdir(frontend_dist):
    app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="frontend")

if __name__ == "__main__":
```

### 2.2 Edit `telemetrydashboard/app/telemetry.py`

ONE edit. Find this block (it spans roughly lines 116–141):

```python
        try:
            import httpx
            async with httpx.AsyncClient(timeout=5.0) as client:
                # Fetch health
                health_response = await client.get(f"{base_url}/health")
                health_data = health_response.json() if health_response.status_code == 200 else {}
                
                # Fetch stats if available
                stats_data = {}
                try:
                    stats_response = await client.get(f"{base_url}/stats")
                    if stats_response.status_code == 200:
                        stats_data = stats_response.json()
                except:
                    pass
                
                span.set_status(Status(StatusCode.OK))
                
                return {
                    "service": service_name,
                    "url": base_url,
                    "status": "healthy" if health_response.status_code == 200 else "unhealthy",
                    "health": health_data,
                    "stats": stats_data,
                    "timestamp": datetime.utcnow().isoformat()
                }
        except Exception as e:
```

Replace with:
```python
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
```

### 2.3 Edit `telemetrydashboard/requirements.txt`

Find:
```
opentelemetry-exporter-otlp>=1.22.0
opentelemetry-instrumentation-fastapi>=0.43b0
```

Replace with:
```
opentelemetry-exporter-otlp>=1.22.0
opentelemetry-proto>=1.22.0
opentelemetry-instrumentation-fastapi>=0.43b0
```

### 2.4 Create `telemetrydashboard/app/otlp_receiver.py`

This is a brand new file. Write it with this EXACT content:

```python
"""OTLP HTTP receiver — accepts protobuf pushes from backend / channel services.

Render free tier exposes only one HTTP port per service, so we cannot run the
standalone otel-collector binary on 4317/4318. Instead, FastAPI itself handles
the OTLP HTTP spec endpoints (/v1/traces, /v1/metrics, /v1/logs) and writes
decoded payloads into the in-memory storage used by the dashboard API.
"""

import gzip
import logging
from typing import Any, Dict, List

from fastapi import APIRouter, Request, Response
from opentelemetry.proto.collector.logs.v1 import logs_service_pb2
from opentelemetry.proto.collector.metrics.v1 import metrics_service_pb2
from opentelemetry.proto.collector.trace.v1 import trace_service_pb2

from .telemetry import log_storage, metric_storage

logger = logging.getLogger(__name__)
router = APIRouter()

OTLP_CONTENT_TYPE = "application/x-protobuf"


async def _read_body(request: Request) -> bytes:
    body = await request.body()
    if request.headers.get("content-encoding", "").lower() == "gzip":
        try:
            body = gzip.decompress(body)
        except OSError as exc:
            logger.warning("Failed to decompress OTLP gzip body: %s", exc)
    return body


def _attrs_to_dict(attributes) -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    for attr in attributes:
        v = attr.value
        if v.HasField("string_value"):
            out[attr.key] = v.string_value
        elif v.HasField("int_value"):
            out[attr.key] = v.int_value
        elif v.HasField("double_value"):
            out[attr.key] = v.double_value
        elif v.HasField("bool_value"):
            out[attr.key] = v.bool_value
        else:
            out[attr.key] = str(v)
    return out


def _resource_service_name(resource_attrs: Dict[str, Any]) -> str:
    return str(resource_attrs.get("service.name", "unknown"))


def _data_point_value(dp) -> float:
    if dp.HasField("as_double"):
        return float(dp.as_double)
    if dp.HasField("as_int"):
        return float(dp.as_int)
    return 0.0


@router.post("/v1/metrics")
async def receive_metrics(request: Request) -> Response:
    body = await _read_body(request)
    req = metrics_service_pb2.ExportMetricsServiceRequest()
    try:
        req.ParseFromString(body)
    except Exception as exc:
        logger.warning("OTLP metrics parse failed: %s", exc)
        return Response(content=b"", media_type=OTLP_CONTENT_TYPE, status_code=400)

    recorded = 0
    for rm in req.resource_metrics:
        resource_attrs = _attrs_to_dict(rm.resource.attributes)
        service = _resource_service_name(resource_attrs)
        for sm in rm.scope_metrics:
            for metric in sm.metrics:
                points: List = []
                if metric.HasField("sum"):
                    points = list(metric.sum.data_points)
                elif metric.HasField("gauge"):
                    points = list(metric.gauge.data_points)
                elif metric.HasField("histogram"):
                    for dp in metric.histogram.data_points:
                        labels = _attrs_to_dict(dp.attributes)
                        labels["service"] = service
                        await metric_storage.record_metric(
                            f"{metric.name}.sum", float(dp.sum), labels
                        )
                        await metric_storage.record_metric(
                            f"{metric.name}.count", float(dp.count), labels
                        )
                        recorded += 2
                    continue
                for dp in points:
                    labels = _attrs_to_dict(dp.attributes)
                    labels["service"] = service
                    await metric_storage.record_metric(
                        metric.name, _data_point_value(dp), labels
                    )
                    recorded += 1

    logger.debug("Received OTLP metrics: %d data points", recorded)
    resp = metrics_service_pb2.ExportMetricsServiceResponse().SerializeToString()
    return Response(content=resp, media_type=OTLP_CONTENT_TYPE)


_SEVERITY_TO_LEVEL = {
    1: "trace", 2: "trace", 3: "trace", 4: "trace",
    5: "debug", 6: "debug", 7: "debug", 8: "debug",
    9: "info", 10: "info", 11: "info", 12: "info",
    13: "warning", 14: "warning", 15: "warning", 16: "warning",
    17: "error", 18: "error", 19: "error", 20: "error",
    21: "fatal", 22: "fatal", 23: "fatal", 24: "fatal",
}


@router.post("/v1/logs")
async def receive_logs(request: Request) -> Response:
    body = await _read_body(request)
    req = logs_service_pb2.ExportLogsServiceRequest()
    try:
        req.ParseFromString(body)
    except Exception as exc:
        logger.warning("OTLP logs parse failed: %s", exc)
        return Response(content=b"", media_type=OTLP_CONTENT_TYPE, status_code=400)

    received = 0
    for rl in req.resource_logs:
        service = _resource_service_name(_attrs_to_dict(rl.resource.attributes))
        for sl in rl.scope_logs:
            for record in sl.log_records:
                level = _SEVERITY_TO_LEVEL.get(int(record.severity_number), "info")
                message = record.body.string_value if record.body.HasField("string_value") else str(record.body)
                await log_storage.add_log({
                    "level": level,
                    "message": message,
                    "service": service,
                    "metadata": _attrs_to_dict(record.attributes),
                })
                received += 1

    logger.debug("Received OTLP logs: %d records", received)
    resp = logs_service_pb2.ExportLogsServiceResponse().SerializeToString()
    return Response(content=resp, media_type=OTLP_CONTENT_TYPE)


@router.post("/v1/traces")
async def receive_traces(request: Request) -> Response:
    body = await _read_body(request)
    req = trace_service_pb2.ExportTraceServiceRequest()
    try:
        req.ParseFromString(body)
    except Exception as exc:
        logger.warning("OTLP traces parse failed: %s", exc)
        return Response(content=b"", media_type=OTLP_CONTENT_TYPE, status_code=400)

    spans = 0
    for rs in req.resource_spans:
        service = _resource_service_name(_attrs_to_dict(rs.resource.attributes))
        for ss in rs.scope_spans:
            for span in ss.spans:
                duration_ns = span.end_time_unix_nano - span.start_time_unix_nano
                await metric_storage.record_metric(
                    "trace.span.duration_ms",
                    duration_ns / 1_000_000.0,
                    {"service": service, "span": span.name},
                )
                spans += 1

    logger.debug("Received OTLP traces: %d spans", spans)
    resp = trace_service_pb2.ExportTraceServiceResponse().SerializeToString()
    return Response(content=resp, media_type=OTLP_CONTENT_TYPE)
```

---

## 3. Syntax-check all edited files

```bash
cd /home/akshat/Project
python3 -c "
import ast, sys
for p in [
    'telemetrydashboard/app/main.py',
    'telemetrydashboard/app/telemetry.py',
    'telemetrydashboard/app/otlp_receiver.py',
]:
    try:
        ast.parse(open(p).read())
        print(f'OK  {p}')
    except SyntaxError as e:
        print(f'ERR {p}: {e}'); sys.exit(1)
"
```

Expected: three `OK` lines. If any `ERR`, stop and re-read the failing file against section 2.

---

## 4. Verify Render env vars (read-only check)

Use Render MCP to confirm these env vars exist on the listed services. They should already be set; just verify.

For each service, list env vars and confirm the expected keys. Replace `<svc-id>` with the service ID from section 0.

```
mcp__render__list_env_vars(serviceId="srv-d8ku7hkvikkc73c6udcg")  # backend
mcp__render__list_env_vars(serviceId="srv-d8ku7i0js32c73bpnde0")  # channel
mcp__render__list_env_vars(serviceId="srv-d8ku7lmrnols73c5b960")  # telemetry
```

Required values:

| Service | Key | Value |
|---|---|---|
| backend | `OTEL_EXPORTER_OTLP_ENDPOINT` | `https://xeno-crm-2027-telemetry.onrender.com` |
| channel | `OTEL_EXPORTER_OTLP_ENDPOINT` | `https://xeno-crm-2027-telemetry.onrender.com` |
| telemetry | `APP_SERVICE_URL` | `https://xeno-crm-2027-backend.onrender.com` |
| telemetry | `CHANNEL_SERVICE_URL` | `https://xeno-crm-2027-channel.onrender.com` |

If any of these is missing or wrong, set it with `mcp__render__update_env_vars`. The URL must have NO trailing slash and NO port number.

---

## 5. Commit and push

```bash
cd /home/akshat/Project
git add telemetrydashboard/app/main.py \
        telemetrydashboard/app/telemetry.py \
        telemetrydashboard/app/otlp_receiver.py \
        telemetrydashboard/requirements.txt
git status
```

Verify only those four files are staged. Then commit:

```bash
git commit -m "$(cat <<'EOF'
Fix telemetry dashboard "failed to fetch metrics" on Render

- Move StaticFiles mount to end of main.py so /api/* routes match first
- Add OTLP HTTP receiver (/v1/metrics, /v1/logs, /v1/traces) so backend
  and channel can push telemetry without a separate collector container
- Bump PULL aggregator httpx timeout 5s->60s to survive Render cold starts
- Drop the /stats fetch that always 404s on backend and channel

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
git push origin master
```

---

## 6. Wait for Render to redeploy the telemetry dashboard

The telemetry dashboard is a Docker service; pushing to `master` auto-triggers a build.

Poll deploy status with Render MCP:

```
mcp__render__list_deploys(serviceId="srv-d8ku7lmrnols73c5b960", limit=1)
```

Wait until the most recent deploy has `status: "live"`. Builds typically take 4–8 minutes for this Docker image.

If status becomes `build_failed` or `update_failed`, fetch logs:

```
mcp__render__list_logs(resource=["srv-d8ku7lmrnols73c5b960"], type=["build"], limit=200)
```

Fix the build error, commit, push, re-poll.

---

## 7. Verify the fix

Run these four checks in order. Each must pass before moving to the next.

### 7.1 Routing fix works

```bash
curl -sS https://xeno-crm-2027-telemetry.onrender.com/api/v1/metrics | head -c 200
```

**Pass:** output starts with `{` and contains `"services"`. (JSON.)
**Fail:** output starts with `<!doctype html` or `<html`. (Static mount still wins.) → re-check section 2.1, Edit A and Edit D.

### 7.2 OTLP receiver is mounted

```bash
curl -sS -X POST -H "Content-Type: application/x-protobuf" --data-binary "" \
  -o /dev/null -w "%{http_code}\n" \
  https://xeno-crm-2027-telemetry.onrender.com/v1/metrics
```

**Pass:** `200`.
**Fail:** `404` → router not included; re-check section 2.1, Edit B and Edit C.
**Fail:** `405` → route registered for wrong method; re-check `otlp_receiver.py`.

### 7.3 Push pipeline works end-to-end

Generate traffic on the backend so it exports metrics, then check the dashboard received them:

```bash
for i in 1 2 3 4 5; do
  curl -sS -o /dev/null https://xeno-crm-2027-backend.onrender.com/health
  sleep 1
done

# Wait one full metrics export interval (services push every 30s)
sleep 70

curl -sS https://xeno-crm-2027-telemetry.onrender.com/api/v1/metrics/summary \
  | python3 -m json.tool | head -50
```

**Pass:** the JSON `metrics` object contains keys starting with `backend.` (e.g. `backend.requests.total`).
**Fail:** `metrics` is empty `{}` → check dashboard logs (next step) for OTLP parse errors.

### 7.4 Dashboard logs show OTLP POSTs

```
mcp__render__list_logs(
  resource=["srv-d8ku7lmrnols73c5b960"],
  type=["app"],
  limit=100,
  text=["/v1/metrics"]
)
```

**Pass:** log lines like `POST /v1/metrics HTTP/1.1 200`.
**Fail:** no `/v1/metrics` lines → backend/channel are not pushing. Confirm section 4 env vars and that backend status is `live`:

```
mcp__render__list_deploys(serviceId="srv-d8ku7hkvikkc73c6udcg", limit=1)
```

### 7.5 Browser smoke test

Open `https://xeno-crm-2027-telemetry.onrender.com/` in a browser. Within ~60 s:
- The "Failed to fetch metrics" banner is gone.
- The status panel shows both `app_service` and `channel_service` as `healthy` (or `unreachable` if the service is asleep — that's still a pass, the dashboard is *talking* to them).
- The Logs tab shows entries with `service: "xeno-crm-2027-backend"` or similar (proves OTLP log push works).

---

## 8. If you get stuck

- **Dashboard 502/503**: Docker build is still running or container crashed. Get app logs: `mcp__render__list_logs(resource=["srv-d8ku7lmrnols73c5b960"], type=["app"], limit=200)`.
- **`opentelemetry.proto` ImportError in dashboard logs**: requirements.txt edit didn't land. Re-check section 2.3, re-commit, push.
- **Dashboard endpoint returns React HTML for `/api/v1/*`**: the StaticFiles mount is still before the routes. Re-read `telemetrydashboard/app/main.py` — the `app.mount("/", StaticFiles(...))` line MUST be after `@app.on_event("shutdown")` and before `if __name__ == "__main__":`. There should be exactly ONE such mount call in the file.
- **Backend deploy is `update_failed`**: that is pre-existing per `memory.md` (missing `email-validator` was fixed in `201628a3`). Check most recent deploy — if still failing, get logs with `mcp__render__list_logs(resource=["srv-d8ku7hkvikkc73c6udcg"], type=["build","app"], limit=200)`.

Stop when section 7.5 passes. Report success with the URL the user should open.

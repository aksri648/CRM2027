# Session Memory

## Project
Xeno AI — Campaign Intelligence Platform (CRM2027)
Repo: `https://github.com/aksri648/CRM2027` (branch: `master`)

## Render Workspace
"Akshat's workspace" (ownerId: `tea-d49ivrur433s73akh3lg`) — only workspace available.

## Live Services (CRM2027 repo)

| Service | Render Name | URL | Status |
|---|---|---|---|
| Backend | `xeno-crm-2027-backend` | https://xeno-crm-2027-backend.onrender.com | **update_failed** (missing `email-validator`) |
| Channel Service | `xeno-crm-2027-channel` | https://xeno-crm-2027-channel.onrender.com | LIVE |
| Frontend | `xeno-crm-2027-frontend` | https://xeno-crm-2027-frontend.onrender.com | LIVE |
| Telemetry Dashboard | `xeno-crm-2027-telemetry` | https://xeno-crm-2027-telemetry.onrender.com | LIVE |

## Service IDs
- Backend: `srv-d8ku7hkvikkc73c6udcg`
- Channel Service: `srv-d8ku7i0js32c73bpnde0`
- Frontend: `srv-d8ku7im7r5hc739e63d0`
- Telemetry Dashboard: `srv-d8ku7lmrnols73c5b960`

## Build/Start Commands

### Backend (Python)
```
Build:   cd backend && pip install -r requirements.txt
Start:   cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT
Env:     python
```

### Channel Service (Python)
```
Build:   cd channel_service && pip install -r requirements.txt
Start:   cd channel_service && uvicorn app.main:app --host 0.0.0.0 --port $PORT
Env:     python
```

### Frontend (Node)
```
Build:   cd frontend && npm install && npm run build
Start:   cd frontend && npm run preview -- --host 0.0.0.0 --port $PORT
Env:     node
```

### Telemetry Dashboard (Docker)
```
Build:   (Dockerfile at repo root)
Start:   uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8002}
Env:     docker
```

## Cross-Service Environment Variables

### Backend (`xeno-crm-2027-backend`)
```
CHANNEL_SERVICE_URL=https://xeno-crm-2027-channel.onrender.com
FRONTEND_URL=https://xeno-crm-2027-frontend.onrender.com
OTEL_SERVICE_NAME=xeno-crm-2027-backend
OTEL_EXPORTER_OTLP_ENDPOINT=https://xeno-crm-2027-telemetry.onrender.com
```

### Channel Service (`xeno-crm-2027-channel`)
```
BACKEND_SERVICE_URL=https://xeno-crm-2027-backend.onrender.com
OTEL_SERVICE_NAME=xeno-crm-2027-channel
OTEL_EXPORTER_OTLP_ENDPOINT=https://xeno-crm-2027-telemetry.onrender.com
```

### Frontend (`xeno-crm-2027-frontend`)
```
VITE_API_URL=https://xeno-crm-2027-backend.onrender.com
```

### Telemetry Dashboard (`xeno-crm-2027-telemetry`)
```
APP_SERVICE_URL=https://xeno-crm-2027-backend.onrender.com
CHANNEL_SERVICE_URL=https://xeno-crm-2027-channel.onrender.com
```

## Git History (branch `master`, chronological)

```
3d4c2921 Xeno AI - Campaign Intelligence Platform (initial commit)
01be389b Add .gitignore
26410608 Add project documentation with architecture, API system, and deployment guide
b557d5f2 Add Clerk authentication support
f6b3e72f Fix all bugs from codebase audit
e0464db1 Update env examples for Render deployment and add telemetry dashboard env var support
727da1fa Update env examples, requirements, and source files; untrack pycache/db/dist
007023e9 Add Dockerfile for telemetrydashboard
2d4ff597 Add root Dockerfile for telemetrydashboard Render deployment
3e879355 Fix telemetry deps: remove non-existent otel-instrumentation-runtime/psutil packages
4c462d5a Pin Python to 3.12, remove asyncpg (no wheel for 3.14), relax channel_service pins
d9aa73bb Upgrade sqlalchemy to support Python 3.14
c45d3bc8 Serve telemetry dashboard frontend from FastAPI, add multi-stage Docker build
201628a3 Add email-validator for pydantic email validation  ← HEAD
```

## Issues Encountered & Solutions

### 1. Python 3.14 Incompatibility on Render
- Render uses Python 3.14.3 by default (no `runtime.txt` at repo root is honored)
- `runtime.txt` with `3.12.8` was created but not picked up by build
- **Workaround**: Relax version pins to `>=` so newer wheels (compiled for 3.14) are pulled

### 2. SQLAlchemy 2.0.25 Fails on Python 3.14
- Error: `AssertionError: Class SQLCoreOperations directly inherits TypingOnly but has additional attributes`
- **Fix**: Changed `sqlalchemy==2.0.25` → `sqlalchemy>=2.0.25` in `backend/requirements.txt`
- **Status**: Now builds successfully (but runtime fails for other reasons, see #6)

### 3. pydantic-core 2.14.6 Fails to Build on Render
- Channel service had `pydantic-core==2.14.6` pinned
- No prebuilt wheel for Python 3.14; requires Cargo/Rust to compile from source (unavailable on Render)
- **Fix**: Changed all `==` pins → `>=` in `channel_service/requirements.txt`
- **Status**: Channel service builds and is LIVE

### 4. Missing `opentelemetry-instrumentation-runtime` and `opentelemetry-instrumentation-psutil`
- These packages do NOT exist on PyPI for Python (they are for Node.js/other ecosystems)
- Caused `pip install` to fail
- **Fix**: Removed both from both `backend/requirements.txt` and `channel_service/requirements.txt`
- Guarded imports in both `backend/telemetry/metrics.py` and `channel_service/telemetry/metrics.py` with try/except
- **Alternative**: Use `opentelemetry-instrumentation-system-metrics` if runtime metrics are needed

### 5. asyncpg Missing Wheel for Python 3.14
- `asyncpg==0.29.0` has no prebuilt wheel for Python 3.14 on Linux x86_64
- **Fix**: Removed `asyncpg` from `backend/requirements.txt` (backend defaults to SQLite)

### 6. email-validator Required by Newer pydantic on Python 3.14
- Backend fails at runtime with: `ImportError: email-validator is not installed`
- Newer pydantic versions (auto-pulled via `>=` pins) require explicit `email-validator` dep
- **Fix**: Added `email-validator>=2.0.0` to `backend/requirements.txt`
- **Status**: Commit `201628a3` — backend build in progress

### 7. Telemetry Dashboard Served JSON Only (No Frontend UI)
- React frontend existed at `telemetrydashboard/frontend/` but was not built/served
- **Fix**: 
  - Updated `telemetrydashboard/app/main.py` to mount `frontend/dist` as static files with `StaticFiles(directory=..., html=True)`
  - Updated `Dockerfile` to multi-stage build (Node stage builds frontend, Python stage serves it)
- **Status**: Telemetry dashboard now serves HTML frontend at `https://xeno-crm-2027-telemetry.onrender.com/`

## Key Files Modified

### `backend/requirements.txt`
```txt
fastapi>=0.136.0
uvicorn[standard]>=0.30.0
sqlalchemy>=2.0.25        # was ==2.0.25
alembic==1.13.1
pydantic>=2.9.0
pydantic-settings>=2.5.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart>=0.0.9
httpx>=0.27.0
openai>=1.12.0
psycopg2-binary>=2.9.9
python-dotenv==1.0.0
email-validator>=2.0.0    # ADDED
langgraph>=1.0.0
langchain-groq>=0.1.0
groq>=0.30.0

# OpenTelemetry - Observability
opentelemetry-api>=1.22.0
opentelemetry-sdk>=1.22.0
opentelemetry-exporter-otlp>=1.22.0
opentelemetry-instrumentation-fastapi>=0.43b0
opentelemetry-instrumentation-httpx>=0.43b0
opentelemetry-instrumentation-logging>=0.43b0
opentelemetry-semantic-conventions>=0.43b0
psutil>=5.9.0

# REMOVED: opentelemetry-instrumentation-runtime
# REMOVED: opentelemetry-instrumentation-psutil
# REMOVED: asyncpg
```

### `channel_service/requirements.txt`
```txt
fastapi>=0.109.0          # was ==0.109.0
uvicorn[standard]>=0.27.0 # was ==0.27.0
pydantic>=2.5.3           # was ==2.5.3
pydantic-settings>=2.1.0  # was ==2.1.0
httpx>=0.26.0             # was ==0.26.0
python-dotenv>=1.0.0      # was ==1.0.0

# OpenTelemetry - Observability
opentelemetry-api>=1.22.0
opentelemetry-sdk>=1.22.0
opentelemetry-exporter-otlp>=1.22.0
opentelemetry-instrumentation-fastapi>=0.43b0
opentelemetry-instrumentation-httpx>=0.43b0
opentelemetry-instrumentation-logging>=0.43b0
opentelemetry-semantic-conventions>=0.43b0
psutil>=5.9.0

# REMOVED: opentelemetry-instrumentation-runtime
# REMOVED: opentelemetry-instrumentation-psutil
```

### `telemetrydashboard/app/main.py`
- Added `from fastapi.staticfiles import StaticFiles` and `import os`
- Added frontend static mount (line 17-19):
  ```python
  frontend_dist = os.path.join(os.path.dirname(__file__), "..", "frontend", "dist")
  if os.path.isdir(frontend_dist):
      app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="frontend")
  ```

### `Dockerfile` (root)
- Multi-stage build:
  - Stage 1: `node:20-slim` builds `telemetrydashboard/frontend/` → `dist/`
  - Stage 2: `python:3.11-slim` serves the app, copies `dist/` from stage 1

### `runtime.txt`
```txt
3.12.8
```
- Created but NOT honored by Render (still uses Python 3.14)
- Only used by telemetry dashboard Docker image (which uses its own `python:3.11-slim`)

### `backend/telemetry/metrics.py` & `channel_service/telemetry/metrics.py`
- Both have guarded imports for `RuntimeInstrumentor` and `PsutilInstrumentor`:
  ```python
  try:
      from opentelemetry.instrumentation.runtime import RuntimeInstrumentor
  except ImportError:
      RuntimeInstrumentor = None
  ```

## Suspended Services (Old CRM repo, `main` branch)
These were suspended by the user and belong to the old `CRM` repo:
- `xeno-crm-app-service` (`srv-d8k8og06dvec73fnh4fg`)
- `xeno-crm-agent-service` (`srv-d8k8og77f7vs73c32ag0`)
- `xeno-crm-communication-service` (`srv-d8k8ogbeo5us73eprmag`)
- `xeno-crm-agent-worker` (`srv-d8kmf6d7vvec73cc79j0`)
- `xeno-crm-frontend` static site (`srv-d8k8nv6k1jcs739mava0`)
- `xeno-crm-frontend-web` (`srv-d8kn50l8nd3s73bdqnjg`)

## Other Render Services (Unrelated Projects)
Multiple services for `ai_router`, `sql-xlsx-agent`, `Medical-AI-Report-Analyzer`, `AI_STOCK_MONITOR`, `AI_DATA_ANALYTICS_PIPELINE`, `pdf-drm-backend`, `sip-tts`, `tts-api`, `VoipP2P`, `n8n`, `corporate_agentic_ai_ticket_system`, `Slack-clone-master`, `Event-Managment-Platform` — all suspended.

## Next Steps
1. Wait for backend deploy to finish (commit `201628a3` with `email-validator` fix).
2. Verify telemetry dashboard serves the React frontend and API endpoints work.
3. Verify frontend → backend → channel service communication works end-to-end.
4. Clean up `runtime.txt` from repo root if not needed (Docker image uses `python:3.11-slim`).
5. Consider switching to `opentelemetry-instrumentation-system-metrics` if runtime/psutil metrics are needed.

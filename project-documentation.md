# Xeno AI - Campaign Intelligence Platform

## Project Overview

Xeno AI is an AI-native marketing CRM that helps brands discover customer audiences, generate campaign strategies, create personalized messaging, and track engagement through a complete callback-driven architecture.

### Core Features

- **AI Campaign Studio**: Natural language interface to build campaigns
- **Customer Management**: Store and analyze customer data with LTV tracking
- **Audience Segmentation**: AI-powered and manual segment creation
- **Multi-Channel Campaigns**: WhatsApp, SMS, Email, RCS support
- **Real-Time Pipeline Monitor**: Track campaign delivery and engagement
- **Analytics Dashboard**: Channel performance and funnel analytics
- **Human-in-the-Loop**: AI proposals require approval before launch

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend                                 │
│                   React + Vite + TailwindCSS                    │
│                      Port: 5173                                  │
└─────────────────────────────┬───────────────────────────────────┘
                              │ REST + SSE
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      App Service (Backend)                       │
│                   FastAPI + SQLAlchemy + LangGraph              │
│                         Port: 8000                               │
│                                                                  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │
│  │   Routers   │  │  Services   │  │   LangGraph Agent       │  │
│  │  /api/v1/*  │  │  Business   │  │   /agent/               │  │
│  │             │  │    Logic    │  │   - nodes/              │  │
│  │             │  │             │  │   - tools/              │  │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘  │
└─────────────────────────────┬───────────────────────────────────┘
                              │
         ┌────────────────────┼────────────────────┐
         │                    │                    │
         ▼                    ▼                    ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│   PostgreSQL    │  │  LangGraph      │  │ Channel Service │
│   (Production)  │  │  (AI Agent)     │  │   Port: 8001    │
│   SQLite (Dev)  │  │                 │  │                 │
└─────────────────┘  └─────────────────┘  └────────┬────────┘
                                                   │
                                                   ▼
                                          ┌─────────────────┐
                                          │  Delivery       │
                                          │  Simulation     │
                                          │  + Callbacks    │
                                          └─────────────────┘
```

### Services

| Service | Technology | Port | Purpose |
|---------|------------|------|---------|
| **Frontend** | React + Vite + TailwindCSS | 5173 | UI presentation |
| **App Service** | FastAPI + SQLAlchemy | 8000 | API + Business Logic |
| **Channel Service** | FastAPI + asyncio | 8001 | Message delivery simulation |
| **Database** | SQLite (dev) / PostgreSQL (prod) | - | Data persistence |

---

## API System

### Base URL

- **Development**: `http://localhost:8000`
- **Production**: Your deployed backend URL

### Authentication

All protected endpoints require JWT Bearer token:

```
Authorization: Bearer <token>
```

### API Endpoints

#### Auth

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/register` | Register new user |
| POST | `/api/v1/auth/login` | Login and get token |
| POST | `/api/v1/auth/refresh` | Refresh access token |
| GET | `/api/v1/auth/me` | Get current user |

#### Customers

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/customers` | List customers (paginated) |
| GET | `/api/v1/customers/{id}` | Get customer details |
| POST | `/api/v1/customers` | Create customer |
| PUT | `/api/v1/customers/{id}` | Update customer |
| DELETE | `/api/v1/customers/{id}` | Delete customer |
| GET | `/api/v1/customers/stats` | Get customer statistics |

#### Segments

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/segments` | List segments |
| GET | `/api/v1/segments/{id}` | Get segment details |
| POST | `/api/v1/segments` | Create segment |
| PUT | `/api/v1/segments/{id}` | Update segment |
| DELETE | `/api/v1/segments/{id}` | Delete segment |
| POST | `/api/v1/segments/preview` | Preview segment (count customers) |

#### Campaigns

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/campaigns` | List campaigns |
| GET | `/api/v1/campaigns/{id}` | Get campaign details |
| POST | `/api/v1/campaigns` | Create campaign |
| PUT | `/api/v1/campaigns/{id}` | Update campaign |
| DELETE | `/api/v1/campaigns/{id}` | Delete campaign |
| POST | `/api/v1/campaigns/{id}/launch` | Launch campaign |
| GET | `/api/v1/campaigns/{id}/communications` | Get campaign communications |

#### Orders

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/orders` | List orders |
| GET | `/api/v1/orders/{id}` | Get order details |
| POST | `/api/v1/orders` | Create order |

#### Analytics

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/analytics/overview` | Dashboard overview metrics |
| GET | `/api/v1/analytics/channels` | Channel performance stats |
| GET | `/api/v1/analytics/campaigns/top` | Top performing campaigns |
| GET | `/api/v1/analytics/funnel` | Campaign funnel data |

#### Opportunities

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/opportunities` | List opportunities |
| GET | `/api/v1/opportunities/{id}` | Get opportunity details |
| POST | `/api/v1/opportunities` | Create opportunity |
| PUT | `/api/v1/opportunities/{id}` | Update opportunity |
| DELETE | `/api/v1/opportunities/{id}` | Delete opportunity |

#### Agent Proposals

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/proposals` | List proposals |
| GET | `/api/v1/proposals/{id}` | Get proposal details |
| POST | `/api/v1/proposals/{id}/approve` | Approve proposal |
| POST | `/api/v1/proposals/{id}/reject` | Reject proposal |

#### AI Agent

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/agent/chat` | Chat with AI (SSE streaming) |

#### Pipeline

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/pipeline/status` | Get pipeline status |
| GET | `/api/v1/pipeline/events` | Get recent events |

#### Settings

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/settings` | Get settings |
| PUT | `/api/v1/settings` | Update settings |

#### A/B Tests

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/ab-tests` | List A/B tests |
| GET | `/api/v1/ab-tests/{id}` | Get A/B test details |
| POST | `/api/v1/ab-tests` | Create A/B test |

#### Callbacks

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/callbacks/receive` | Receive channel service callbacks |

---

## Campaign Lifecycle

```
1. AI Agent generates proposal
         ↓
2. Human approves proposal
         ↓
3. Campaign created (status: draft)
         ↓
4. Campaign launched (status: running)
         ↓
5. Communications created (status: queued)
         ↓
6. POST /send to Channel Service
         ↓
7. Channel Service queues job
         ↓
8. Worker picks up job
         ↓
9. Events generated (sent → delivered → opened → clicked → converted)
         ↓
10. Callbacks sent to App Service
         ↓
11. Database updated
         ↓
12. Analytics updated
         ↓
13. Frontend polls and displays
```

---

## Setup Instructions (Local Development)

### Prerequisites

- Python 3.12+
- Node.js 18+
- npm or yarn

### 1. Clone the Repository

```bash
git clone https://github.com/aksri648/CRM2027.git
cd CRM2027
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cat > .env << 'EOF'
DATABASE_URL=sqlite:///./xeno_crm.db
KIMCHI_BASE_URL=https://api.groq.com/openai/v1
KIMCHI_API_KEY=your_groq_api_key
AI_MODEL=llama-3.3-70b-versatile
CHANNEL_SERVICE_URL=http://localhost:8001
SECRET_KEY=your-secret-key-here
EOF

# Run database migrations (if using Alembic)
# alembic upgrade head

# Seed the database
python seed.py

# Start the backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 3. Channel Service Setup

```bash
cd channel_service

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start the channel service
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

### 4. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Create .env file
cat > .env << 'EOF'
VITE_API_URL=http://localhost:8000
EOF

# Start the frontend
npm run dev
```

### 5. Access the Application

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **Backend Docs**: http://localhost:8000/docs
- **Channel Service**: http://localhost:8001

### Default Login

```
Email: admin@example.com
Password: admin123
```

---

## Deployment to Render

### 1. Create Render Account

Sign up at https://render.com

### 2. Deploy PostgreSQL Database

1. Go to Dashboard → New → PostgreSQL
2. Configure:
   - **Name**: `xeno-crm-db`
   - **Region**: Choose closest to you
   - **Instance Type**: Free tier for development
3. Note the Connection URL

### 3. Deploy Backend (App Service)

1. Go to Dashboard → New → Web Service
2. Connect your GitHub repository
3. Configure:
   - **Name**: `xeno-crm-backend`
   - **Region**: Choose closest to you
   - **Branch**: `master`
   - **Root Directory**: `backend`
   - **Runtime**: `Python 3.12`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port 8000`
4. Add Environment Variables:
   ```
   DATABASE_URL=<your-postgresql-connection-url>
   KIMCHI_BASE_URL=https://api.groq.com/openai/v1
   KIMCHI_API_KEY=<your-groq-api-key>
   AI_MODEL=llama-3.3-70b-versatile
   CHANNEL_SERVICE_URL=https://xeno-crm-channel.onrender.com
   SECRET_KEY=<generate-random-secret>
   ```
5. Click "Create Web Service"

### 4. Deploy Channel Service

1. Go to Dashboard → New → Web Service
2. Connect your GitHub repository
3. Configure:
   - **Name**: `xeno-crm-channel`
   - **Region**: Same as backend
   - **Branch**: `master`
   - **Root Directory**: `channel_service`
   - **Runtime**: `Python 3.12`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port 8001`
4. Add Environment Variables:
   ```
   CORE_BACKEND_URL=https://xeno-crm-backend.onrender.com
   ```
5. Click "Create Web Service"

### 5. Deploy Frontend (Optional - Vercel)

1. Go to https://vercel.com
2. Import your GitHub repository
3. Configure:
   - **Framework Preset**: `Vite`
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
4. Add Environment Variables:
   ```
   VITE_API_URL=https://xeno-crm-backend.onrender.com
   ```
5. Click "Deploy"

### 6. Update Channel Service URL

After deploying backend, update the Channel Service's `CORE_BACKEND_URL` environment variable to point to the actual backend URL.

### 7. Verify Deployment

1. Test backend health: `https://xeno-crm-backend.onrender.com/health`
2. Test channel service: `https://xeno-crm-channel.onrender.com/health`
3. Access frontend at the Vercel URL

---

## Environment Variables

### Backend (.env)

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://user:pass@host:5432/db` |
| `KIMCHI_BASE_URL` | LLM API base URL | `https://api.groq.com/openai/v1` |
| `KIMCHI_API_KEY` | LLM API key | `gsk_...` |
| `AI_MODEL` | Model to use | `llama-3.3-70b-versatile` |
| `CHANNEL_SERVICE_URL` | Channel service URL | `http://localhost:8001` |
| `SECRET_KEY` | JWT signing secret | `random-secret-string` |

### Frontend (.env)

| Variable | Description | Example |
|----------|-------------|---------|
| `VITE_API_URL` | Backend API URL | `http://localhost:8000` |

### Channel Service (.env)

| Variable | Description | Example |
|----------|-------------|---------|
| `CORE_BACKEND_URL` | App Service URL | `http://localhost:8000` |

---

## Production Tradeoffs

### Why asyncio.Queue?

Used for simplicity. No external dependencies. Fast implementation.

**At scale, use:**
- Redis + Celery
- RabbitMQ
- Kafka

### Why Polling Instead of WebSockets?

Simpler. Adequate for campaign monitoring. Lower complexity.

### Why In-Memory Logs?

Assignment scope.

**At scale, use:**
- Redis
- Kafka
- ClickHouse
- Elasticsearch

---

## Support

For issues or questions, please refer to the GitHub repository or contact the development team.
# Xeno Mini CRM - AI-Native Marketing & Engagement Platform

An AI-native Mini CRM for consumer brands to intelligently reach their shoppers through personalized marketing campaigns.

## Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Frontend      │     │   CRM Backend   │     │ Channel Service │
│   (React SPA)   │────▶│   (FastAPI)     │────▶│   (Stubbed)     │
│   Port 3000     │     │   Port 8000     │     │   Port 8001     │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                              │                        │
                              │    Async Callbacks     │
                              │◀───────────────────────┘
                              │
                              ▼
                        ┌─────────────┐
                        │ PostgreSQL  │
                        │  (Neon)     │
                        └─────────────┘
```

## Features

- **Customer Management**: Import, search, and manage customer profiles
- **Audience Segmentation**: Rule-based segmentation with AI suggestions
- **Campaign Management**: Multi-channel campaigns (Email, SMS, WhatsApp, RCS)
- **Channel Service**: Stubbed messaging provider with realistic delivery simulation
- **Performance Analytics**: Track sent, delivered, opened, clicked, converted
- **AI Assistant**: Natural language interface for marketing assistance

## Tech Stack

- **Frontend**: React 18, TypeScript, Vite, TailwindCSS
- **Backend**: FastAPI, SQLAlchemy, Pydantic
- **Database**: PostgreSQL (Neon)
- **AI**: kimchi.dev (OpenAI-compatible API)

## Setup Instructions

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL database (or use Neon cloud)

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env with your database URL and API keys

# Run the server
uvicorn app.main:app --reload --port 8000
```

### Channel Service Setup

```bash
cd channel_service

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn app.main:app --reload --port 8001
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Run the dev server
npm run dev
```

## Environment Variables

### Backend (.env)
```
DATABASE_URL=postgresql://user:pass@host:5432/dbname
SECRET_KEY=your-secret-key
CHANNEL_SERVICE_URL=http://localhost:8001
CHANNEL_SERVICE_API_KEY=channel-service-api-key
KIMCHI_BASE_URL=https://api.kimchi.dev/v1
KIMCHI_API_KEY=your-kimchi-api-key
CRM_CALLBACK_URL=http://localhost:8000/api/v1/callbacks
```

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login
- `POST /api/v1/auth/refresh` - Refresh token
- `GET /api/v1/auth/me` - Get current user

### Customers
- `GET /api/v1/customers` - List customers
- `POST /api/v1/customers` - Create customer
- `GET /api/v1/customers/{id}` - Get customer
- `PUT /api/v1/customers/{id}` - Update customer
- `DELETE /api/v1/customers/{id}` - Delete customer
- `GET /api/v1/customers/{id}/timeline` - Get customer timeline
- `POST /api/v1/customers/import` - Bulk import

### Segments
- `GET /api/v1/segments` - List segments
- `POST /api/v1/segments` - Create segment
- `GET /api/v1/segments/{id}` - Get segment
- `PUT /api/v1/segments/{id}` - Update segment
- `DELETE /api/v1/segments/{id}` - Delete segment
- `POST /api/v1/segments/{id}/preview` - Preview segment
- `POST /api/v1/segments/preview` - Preview rules

### Campaigns
- `GET /api/v1/campaigns` - List campaigns
- `POST /api/v1/campaigns` - Create campaign
- `GET /api/v1/campaigns/{id}` - Get campaign
- `PUT /api/v1/campaigns/{id}` - Update campaign
- `DELETE /api/v1/campaigns/{id}` - Delete campaign
- `POST /api/v1/campaigns/{id}/send` - Send campaign
- `GET /api/v1/campaigns/{id}/stats` - Get campaign stats

### AI
- `POST /api/v1/ai/chat` - Natural language interface
- `POST /api/v1/ai/suggest-segment` - AI suggest segment
- `POST /api/v1/ai/generate-messages` - Generate message variants
- `POST /api/v1/ai/suggest-channel` - Suggest best channel
- `POST /api/v1/ai/analyze-campaign` - Analyze campaign performance

## Communication Flow

1. Marketer creates campaign and segment
2. CRM sends communications to Channel Service
3. Channel Service simulates delivery (1-5 second delay)
4. Channel Service calls back to CRM with status updates
5. CRM updates communication and campaign stats

## License

MIT
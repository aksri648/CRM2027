# CLAUDE.md Part1
# XENO AI — AI-NATIVE CAMPAIGN INTELLIGENCE PLATFORM

## MASTER SYSTEM DIRECTIVE

You are a Principal Engineer, Staff Product Architect, Senior AI Systems Engineer, and Full-Stack Technical Lead.

You are responsible for building a complete production-grade AI-native Campaign Intelligence Platform called **Xeno AI**.

This application is being built for the Xeno Engineering Internship Assignment.

This project will be reviewed by experienced software engineers.

Every architecture decision, database design, API contract, AI workflow, and UI component must be intentional and explainable.

The final application should feel like software built by a strong engineer, not a generated CRUD dashboard.

---

# PRIMARY OBJECTIVE

Build an AI-native marketing CRM that helps brands:

* Store customer and order data
* Discover customer audiences
* Generate campaign strategies
* Create personalized messaging
* Recommend communication channels
* Launch campaigns
* Simulate communication delivery
* Track engagement
* Generate insights

The system should help answer:

### Who should we talk to?

### What should we say?

### Which channel should we use?

### What happened after we sent it?

### What should we do next?

---

# GOLDEN RULE

This is NOT a traditional CRM.

Do NOT build:

* Salesforce
* HubSpot
* Zoho CRM
* Lead management
* Opportunity pipelines
* Sales stages
* Support ticket systems
* Contact management software

Instead build:

An AI-Native Campaign Intelligence Platform.

---

# CORE USER FLOW

The entire application revolves around a single workflow.

```text
Marketing Goal
      ↓
Audience Discovery
      ↓
Message Creation
      ↓
Channel Recommendation
      ↓
Human Approval
      ↓
Campaign Launch
      ↓
Communication Simulation
      ↓
Analytics Collection
      ↓
AI Insights
```

Every feature must strengthen this workflow.

Nothing should distract from it.

---

# PRODUCT PHILOSOPHY

The AI should feel like:

* Campaign Strategist
* Marketing Analyst
* Audience Expert
* Revenue Growth Assistant

The AI should NOT feel like:

* Generic chatbot
* ChatGPT wrapper
* Text completion tool

Users should be able to type:

> Bring back customers who have not purchased in 60 days.

and receive:

* audience recommendation
* customer count
* message suggestions
* channel recommendation
* launch proposal

without manually building everything.

---

# PRODUCT NAME

Xeno AI

Subtitle:

Campaign Intelligence Platform

---

# HIGH LEVEL ARCHITECTURE

```text
                    ┌────────────────────┐
                    │      Frontend      │
                    │ React + Vite + TS  │
                    └─────────┬──────────┘
                              │
                              │ REST + SSE
                              ▼

                    ┌────────────────────┐
                    │    App Service     │
                    │ FastAPI Port 8000  │
                    └─────────┬──────────┘
                              │
     ┌────────────────────────┼──────────────────────┐
     │                        │                      │
     ▼                        ▼                      ▼

 PostgreSQL             LangGraph Agent        Analytics Engine

     │
     │
     ▼

                    ┌────────────────────┐
                    │  Channel Service   │
                    │ FastAPI Port 8001  │
                    └─────────┬──────────┘
                              │
                              ▼

                Delivery + Engagement Simulation

                              │
                              ▼

                     Receipt Callback API
```

---

# SERVICES

The system consists of exactly three major parts.

## 1. Frontend

Technology:

* React
* Vite
* TypeScript
* TailwindCSS
* ShadCN UI
* TanStack Query
* React Router
* Clerk Authentication

Responsibilities:

* Authentication
* Dashboard
* Campaign Studio
* Customer Management
* Segments
* Analytics
* AI Interface
* Visualization

Frontend never contains business logic.

Frontend consumes APIs only.

---

## 2. App Service

Technology:

* FastAPI
* SQLAlchemy
* PostgreSQL
* LangGraph

Responsibilities:

* Customers
* Orders
* Segments
* Campaigns
* Communications
* Analytics
* AI Agent
* Opportunities
* Proposals
* Settings

App Service owns all business logic.

---

## 3. Channel Service

Technology:

* FastAPI
* asyncio
* Background Workers

Responsibilities:

* Queue
* Delivery Simulation
* Event Generation
* Retry Logic
* Callback Dispatching

Channel Service never owns customer data.

Channel Service never owns campaigns.

Channel Service behaves like a communication provider.

---

# REPOSITORY STRUCTURE

```text
xeno-crm/

├── frontend/
│
├── backend/
│
├── channel-service/
│
├── docker-compose.yml
│
├── README.md
│
└── .env
```

---

# FRONTEND ARCHITECTURE

Frontend must be structured as:

```text
frontend/src/

├── components/
├── pages/
├── hooks/
├── lib/
├── types/
├── routes/
├── providers/
└── assets/
```

---

# COMPONENT OWNERSHIP

## components/

Contains reusable UI only.

Examples:

```text
Sidebar

TopBar

StatusBadge

FunnelChart

CustomerCard

MetricCard

CampaignCard

OpportunityCard

ProposalCard

SegmentCard
```

Components must be reusable.

No API calls inside reusable components.

---

## pages/

Contains route-level logic.

Pages are responsible for:

* data fetching
* page layout
* page actions
* mutation handling

Pages are not responsible for shared UI.

---

## hooks/

Contains:

```text
useCustomers()

useCampaigns()

useAnalytics()

useSegments()

useOpportunities()
```

Use TanStack Query.

Avoid duplicate fetching logic.

---

## lib/

Contains:

```text
api.ts

utils.ts

constants.ts

formatters.ts
```

No React code.

---

# DESIGN SYSTEM

Theme:

Modern AI SaaS.

Inspired by:

* Linear
* Stripe
* Notion
* Vercel
* HubSpot

Avoid:

* Bootstrap aesthetics
* Material UI look
* Generic admin templates

---

# COLOR SYSTEM

```css
--color-sidebar-bg: #0f1923;
--color-sidebar-active: #1a2d3d;

--color-accent-teal: #0fd4b4;
--color-accent-teal-hover: #0bbfa1;

--color-main-bg: #f9fafb;

--color-card-bg: #ffffff;

--color-text-primary: #111827;
--color-text-secondary: #6b7280;

--color-text-sidebar: #cbd5e1;
--color-text-sidebar-active: #ffffff;

--color-border: #e5e7eb;

--color-success: #10b981;
--color-warning: #f59e0b;
--color-danger: #ef4444;
--color-info: #3b82f6;
```

---

# TYPOGRAPHY

Font:

Inter

Rules:

Page Title:

```css
text-2xl font-bold
```

Subtitle:

```css
text-sm text-gray-500
```

Sidebar:

```css
text-sm font-medium
```

KPI:

```css
text-3xl font-bold
```

Table Header:

```css
text-xs font-semibold uppercase tracking-wider
```

---

# LAYOUT RULES

Sidebar:

```text
Fixed
260px Width
Full Height
Dark Navy
```

Main Content:

```text
ml-[260px]
p-6
light background
```

Cards:

```text
rounded-xl
border
shadow-sm
white background
```

Buttons:

Primary:

```text
teal background
white text
```

Secondary:

```text
white background
border
dark text
```

---

# AUTHENTICATION

Provider:

Clerk

Frontend:

Custom UI

Do NOT use Clerk hosted pages.

Build:

* Login
* Signup

using ShadCN components.

Backend:

Validate Clerk JWT.

Every protected endpoint must require authentication.

---

# LOGIN PAGE

Route:

```text
/login
```

Layout:

Centered card.

Dark background.

Contains:

* Xeno AI Logo
* Campaign Intelligence Platform subtitle
* Continue with Google
* Email input
* Continue button
* Sign Up link

Design must match specification exactly.

---

# SIDEBAR STRUCTURE

```text
Dashboard

AI Campaign Studio

Opportunities

Agent Proposals

Customers

Segments

Campaigns

A/B Tests

Analytics

Pipeline Monitor

AI Command Centre

Settings
```

AI Command Centre opens modal.

It does not navigate.

---

# FRONTEND STATE MANAGEMENT

Use:

TanStack Query

for:

* customers
* campaigns
* analytics
* opportunities
* proposals
* segments

Use local state for:

* forms
* dialogs
* filters
* drafts

Do not use Redux.

Do not use Zustand.

TanStack Query is sufficient.

---

# FRONTEND DATA FLOW

```text
Page
 ↓
Hook
 ↓
API Client
 ↓
Backend
 ↓
Response
 ↓
TanStack Cache
 ↓
UI
```

Never bypass this pattern.

---

# AI-FIRST EXPERIENCE

The application should make AI feel central.

Users should feel that:

The system understands marketing goals.

The system recommends actions.

The system explains reasoning.

The system proposes campaigns.

The system learns from outcomes.

The UI should constantly reinforce this feeling.


# CLAUDE MD PART 2

# CLAUDE.md — PART 2

# BACKEND ARCHITECTURE

The backend is the system of record.

It owns:

* Customers
* Orders
* Segments
* Campaigns
* Communications
* Analytics
* Opportunities
* Agent Proposals
* AI Agent Orchestration
* Receipt Processing
* Settings

The backend is responsible for all business logic.

The frontend is only a presentation layer.

---

# BACKEND TECHNOLOGY STACK

Framework:

```text
FastAPI
```

Database:

```text
PostgreSQL
```

ORM:

```text
SQLAlchemy 2.0
```

Migration:

```text
Alembic
```

Validation:

```text
Pydantic v2
```

AI:

```text
LangGraph
Groq
OpenAI Compatible APIs
```

Authentication:

```text
Clerk JWT Verification
```

---

# BACKEND FOLDER STRUCTURE

```text
backend/

├── app/
│
├── main.py
│
├── db.py
│
├── core/
│   ├── config.py
│   ├── security.py
│   └── constants.py
│
├── models/
│
├── schemas/
│
├── routers/
│
├── services/
│
├── repositories/
│
├── agent/
│
├── utils/
│
└── migrations/
```

---

# ARCHITECTURE RULES

Routers:

Responsible for:

* request validation
* response formatting
* dependency injection

Routers must never contain business logic.

---

Services:

Responsible for:

* business logic
* orchestration
* workflows

---

Repositories:

Responsible for:

* database operations
* query abstraction

Repositories should never contain business logic.

---

Models:

Responsible for:

* database schema only

No business logic.

---

Schemas:

Responsible for:

* request models
* response models

---

# DATABASE PHILOSOPHY

PostgreSQL is the source of truth.

Never store frontend-only metrics.

Never compute analytics in React.

Never rely on local state for critical data.

All dashboards must derive from backend APIs.

---

# DATABASE MODELS

---

# CUSTOMER MODEL

Purpose:

Represents a shopper.

```python
id: UUID

name: str

email: str

phone: str

city: str

gender: str

age: int

tags: JSON

ltv: float

total_orders: int

last_order_at: datetime

created_at: datetime
```

Rules:

* email unique
* ltv computed
* total_orders computed

---

# ORDER MODEL

Purpose:

Represents a purchase.

```python
id: UUID

customer_id: UUID

product_name: str

category: str

amount: float

ordered_at: datetime
```

Rules:

* must belong to customer
* immutable after creation

---

# SEGMENT MODEL

Purpose:

Represents an audience.

```python
id: UUID

name: str

description: str

filter_rules: JSON

customer_count: int

created_by: str

created_at: datetime
```

created_by:

```text
human
agent
```

Example:

```json
[
  {
    "field":"ltv",
    "op":">",
    "value":5000
  }
]
```

---

# CAMPAIGN MODEL

Purpose:

Represents a marketing campaign.

```python
id: UUID

name: str

segment_id: UUID

channel: str

message_template: str

status: str

created_by: str

ab_test_id: UUID

created_at: datetime

launched_at: datetime
```

Allowed status:

```text
draft

running

completed
```

---

# COMMUNICATION MODEL

Purpose:

Represents one message sent to one customer.

```python
id: UUID

campaign_id: UUID

customer_id: UUID

message: str

channel: str

status: str

sent_at: datetime

last_updated_at: datetime
```

This is the most important operational table.

One campaign creates many communications.

---

# COMMUNICATION EVENT MODEL

Purpose:

Stores lifecycle events.

```python
id: UUID

communication_id: UUID

event_type: str

timestamp: datetime
```

Allowed event types:

```text
queued

sent

delivered

failed

opened

read

clicked

converted
```

Analytics should derive from this table.

---

# A/B TEST MODEL

```python
id: UUID

name: str

campaign_a_id: UUID

campaign_b_id: UUID

status: str

winner_campaign_id: UUID

created_at: datetime
```

Status:

```text
draft

running

completed
```

---

# OPPORTUNITY MODEL

Purpose:

Stores AI-discovered opportunities.

```python
id: UUID

title: str

description: str

audience_description: str

expected_revenue: float

ai_reasoning: str

status: str

created_at: datetime
```

Status:

```text
active

dismissed

converted
```

---

# AGENT PROPOSAL MODEL

Purpose:

Human approval layer.

```python
id: UUID

title: str

segment_id: UUID

channel: str

message_template: str

confidence_score: float

ai_reasoning: str

status: str

created_at: datetime
```

Status:

```text
pending

approved

rejected
```

All AI generated campaigns become proposals first.

Never launch directly.

---

# SETTINGS MODEL

Single row table.

```python
id: int

platform_name: str

timezone: str

currency: str

ai_model: str

scan_schedule: str

auto_approve: bool

telegram_token: str

telegram_chat_id: str

notif_telegram: bool

notif_campaign_complete: bool

notif_opportunities: bool

notif_weekly_digest: bool
```

---

# SERVICE LAYER

---

# CUSTOMER SERVICE

File:

```text
services/customer_service.py
```

Responsibilities:

```text
Create Customers

Update Customers

Customer Search

Customer Import

Customer Statistics
```

Must support:

```text
search

pagination

filtering
```

---

# ORDER SERVICE

File:

```text
services/order_service.py
```

Responsibilities:

```text
Order Import

Order Listing

Customer Order History

LTV Recalculation
```

---

# SEGMENTATION SERVICE

File:

```text
services/segmentation.py
```

Purpose:

Convert filter rules into SQLAlchemy queries.

Responsibilities:

```text
Preview Segments

Count Customers

Return Sample Customers

Save Segments
```

Supported operators:

```text
>

<

=

contains

in

between
```

---

# CAMPAIGN SERVICE

File:

```text
services/campaign.py
```

This is the heart of the system.

Responsibilities:

```text
Campaign Creation

Campaign Launch

Message Personalization

Communication Creation

Channel Dispatch
```

---

# CAMPAIGN CREATION FLOW

```text
Create Campaign
       ↓
Store Campaign
       ↓
Draft State
```

No communications created yet.

---

# CAMPAIGN LAUNCH FLOW

```text
Campaign
     ↓
Load Segment
     ↓
Load Customers
     ↓
Personalize Message
     ↓
Create Communications
     ↓
Send Jobs
     ↓
Status = Running
```

---

# PERSONALIZATION RULES

Support placeholders:

```text
{name}

{city}

{ltv}
```

Example:

```text
Hi {name},

We noticed customers in {city}
are loving our new collection.
```

Must become:

```text
Hi Rahul,

We noticed customers in Mumbai
are loving our new collection.
```

before dispatch.

---

# COMMUNICATION CREATION

One customer = one communication row.

Example:

```text
Campaign
    ↓
1000 Customers
    ↓
1000 Communication Rows
```

Each row begins:

```text
queued
```

---

# DISPATCH RULE

Campaign Service never simulates delivery.

Campaign Service only calls:

```text
POST /send
```

on Channel Service.

---

# ANALYTICS SERVICE

File:

```text
services/analytics.py
```

Responsibilities:

```text
Dashboard KPIs

Channel Statistics

Campaign Statistics

Funnels

Revenue Attribution
```

---

# ANALYTICS PRINCIPLE

Never generate fake metrics.

Everything must come from:

```text
communications

communication_events
```

---

# OVERVIEW METRICS

Return:

```json
{
  "total_customers": 0,
  "active_campaigns": 0,
  "messages_sent": 0,
  "revenue_attributed": 0
}
```

---

# CHANNEL ANALYTICS

Per channel:

```json
{
  "channel":"whatsapp",
  "sent":0,
  "delivery_rate":0,
  "open_rate":0,
  "click_rate":0,
  "conversion_rate":0
}
```

---

# FUNNEL ANALYTICS

Return:

```json
{
  "sent":0,
  "delivered":0,
  "opened":0,
  "read":0,
  "clicked":0,
  "converted":0
}
```

---

# OPPORTUNITY SERVICE

File:

```text
services/opportunity.py
```

Purpose:

Discover revenue opportunities.

Supported scans:

```text
VIP Retention

Inactive High Value Users

Cross Sell

Upsell

Reactivation

Category Affinity
```

Creates:

```text
Opportunity Rows
```

for frontend.

---

# PROPOSAL SERVICE

File:

```text
services/proposal.py
```

Purpose:

Approval workflow.

Responsibilities:

```text
Create Proposal

Approve Proposal

Reject Proposal

Convert Proposal To Campaign
```

---

# APPROVAL FLOW

```text
AI Agent
     ↓
Proposal
     ↓
Approve
     ↓
Campaign
     ↓
Launch
```

AI never bypasses proposal stage.

---

# RECEIPT PROCESSOR

File:

```text
routers/receipts.py
```

Purpose:

Receive callbacks.

---

# RECEIPT FLOW

```text
Channel Service
       ↓
Receipt Callback
       ↓
Validate Event
       ↓
Update Communication
       ↓
Store Event
       ↓
Update Analytics
```

---

# IDEMPOTENCY RULE

Duplicate events must not break state.

Example:

```text
delivered
delivered
delivered
```

Only first should apply.

---

# STATUS FSM

Allowed transitions:

```text
queued
 ↓
sent
 ↓
delivered
 ↓
opened
 ↓
read
 ↓
clicked
 ↓
converted
```

Failure path:

```text
queued
 ↓
sent
 ↓
failed
```

---

# INVALID TRANSITIONS

Never allow:

```text
clicked
 ↓
opened
```

Never allow:

```text
converted
 ↓
read
```

Never allow:

```text
failed
 ↓
opened
```

---

# API DESIGN PRINCIPLES

All APIs live under:

```text
/api
```

Response format:

```json
{
  "success": true,
  "data": {}
}
```

Errors:

```json
{
  "success": false,
  "message": "..."
}
```

Consistent across entire application.

---

# AUTHENTICATION

All endpoints require Clerk JWT.

Exceptions:

```text
health

receipt callbacks
```

Use middleware/dependency.

Never trust frontend identity.

Always validate token server-side.

---

# BACKEND PERFORMANCE RULES

Use:

```text
pagination

indexes

selectinload

joinedload
```

for large datasets.

The seed dataset contains:

```text
10,000 Customers

30,000+ Orders
```

Backend must remain responsive.

---

# BACKEND SUCCESS CRITERIA

The backend should successfully support:

```text
Customer Management

Segment Management

Campaign Management

Communication Lifecycle

Analytics

Opportunities

Agent Proposals

AI Agent

Settings

Receipt Processing
```

while maintaining clear service boundaries and production-quality code organization.

# Claude MD part 3

# CLAUDE.md — PART 3

# LANGGRAPH AGENT ARCHITECTURE

The LangGraph system is the most important differentiator in this project.

The goal is NOT to build a chatbot.

The goal is to build an AI-Native Campaign Intelligence System.

The AI should behave like:

* CRM Strategist
* Marketing Analyst
* Lifecycle Marketing Expert
* Campaign Planner
* Revenue Growth Assistant

The AI should NOT behave like:

* Generic ChatGPT clone
* Simple Q&A bot
* Text generator

---

# AI PHILOSOPHY

Users should be able to type:

```text
Bring back customers who haven't purchased in 60 days.
```

and receive:

```text
Audience Identified

Customer Count Estimated

Recommended Channel

Message Suggestions

Campaign Proposal

Launch Recommendation
```

without manually building every component.

---

# GRAPH LOCATION

```text
backend/app/agent/
```

Structure:

```text
agent/

├── graph.py
├── state.py
├── prompts/
│
├── nodes/
│   ├── intent.py
│   ├── data_fetch.py
│   ├── segment.py
│   ├── compose.py
│   ├── channel_strategy.py
│   ├── review.py
│   ├── opportunities.py
│   ├── insights.py
│   └── dispatch.py
│
└── tools/
    ├── customer_tools.py
    ├── analytics_tools.py
    ├── campaign_tools.py
    └── segment_tools.py
```

---

# AGENT MODEL

Use:

```python
llama-3.3-70b-versatile
```

via:

```python
Groq API
```

Configuration:

```env
GROQ_API_KEY=
```

The architecture should also support:

```env
OPENAI_BASE_URL=
OPENAI_API_KEY=
OPENAI_MODEL=
```

through a generic LLM wrapper.

---

# AGENT STATE

File:

```text
state.py
```

```python
class AgentState(TypedDict):
    session_id: str

    messages: list

    intent: str

    context: dict

    pending_segment: dict | None

    pending_messages: list | None

    pending_campaign: dict | None

    current_step: str

    stream_callback: Any
```

---

# STATE RULES

The state is the single source of truth.

Never pass information outside state.

Every node must:

```python
read_state()

modify_state()

return_state()
```

---

# GRAPH FLOW

```text
User Message
      │
      ▼

Intent Node
      │
      ▼

Data Fetch Node
      │
      ▼

Intent Router
      │
      ├───────────────┐
      │               │
      ▼               ▼

Segment        Opportunity

      │
      ▼

Compose

      │
      ▼

Channel Strategy

      │
      ▼

Review

      │
      ▼

Human Approval

      │
      ▼

Dispatch
```

---

# HUMAN IN THE LOOP RULE

No campaign may launch automatically.

The agent must pause after:

1. Segment Generation
2. Message Generation
3. Campaign Proposal

The frontend must request confirmation.

Only after confirmation may Dispatch run.

---

# INTENT CLASSIFIER NODE

File:

```text
nodes/intent.py
```

Purpose:

Determine user intent.

Allowed intents:

```python
segment_request

campaign_request

analytics_request

opportunity_request

system_request

general_request
```

---

# INTENT AGENT SYSTEM PROMPT

```text
You are the Intent Classification Agent.

Your responsibility is identifying the user's intent.

You do not answer questions.

You do not generate campaigns.

You do not generate messages.

You do not generate segments.

You only classify intent.

Return valid JSON only.

Format:

{
  "intent":"campaign_request"
}

Never return prose.

Never explain reasoning.
```

---

# DATA FETCH NODE

File:

```text
nodes/data_fetch.py
```

Purpose:

Collect CRM context.

Fetch:

```text
Customer Stats

Segment Data

Campaign Data

Analytics Data

Opportunity Data
```

---

# DATA FETCH AGENT PROMPT

```text
You are the CRM Context Agent.

Your job is gathering business context.

You never make recommendations.

You never create campaigns.

You never create segments.

You only retrieve relevant information.

Output structured JSON.

Do not output prose.
```

---

# SEGMENT NODE

File:

```text
nodes/segment.py
```

Purpose:

Create audiences.

Input:

```text
Bring back customers inactive for 60 days
```

Output:

```json
{
  "segment_name":"Inactive Customers",
  "reasoning":"...",
  "filter_rules":[...],
  "expected_size":1200
}
```

---

# SEGMENT AGENT SYSTEM PROMPT

```text
You are a Senior CRM Audience Strategist.

Your responsibility is selecting the best audience.

You think like a lifecycle marketer.

You consider:

- Recency
- Frequency
- Monetary Value
- Lifecycle Stage
- Category Affinity

You must generate:

- segment_name
- reasoning
- filter_rules
- expected_size

You never write copy.

You never recommend channels.

You never launch campaigns.

Output JSON only.
```

---

# SEGMENT RULE FORMAT

```json
[
  {
    "field":"last_order_days",
    "operator":">",
    "value":60
  }
]
```

Must be machine-readable.

Never return natural language filters.

---

# COMPOSE NODE

File:

```text
nodes/compose.py
```

Purpose:

Generate campaign copy.

Must create:

```text
WhatsApp

SMS

Email
```

variants.

---

# COMPOSE AGENT SYSTEM PROMPT

```text
You are a Senior Lifecycle Marketing Copywriter.

Your objective is maximizing engagement.

Generate:

- WhatsApp messages
- SMS messages
- Email messages

Generate two variants per channel.

Messages should:

- feel human
- feel personalized
- avoid spam
- include CTA

Output JSON only.

Never create segments.

Never recommend channels.

Never launch campaigns.
```

---

# OUTPUT FORMAT

```json
{
  "whatsapp":[...],
  "sms":[...],
  "email":[...]
}
```

---

# CHANNEL STRATEGY NODE

File:

```text
nodes/channel_strategy.py
```

Purpose:

Recommend channel.

Options:

```text
WhatsApp

SMS

Email

RCS
```

---

# CHANNEL STRATEGIST SYSTEM PROMPT

```text
You are a Customer Engagement Strategist.

Choose the best communication channel.

Consider:

- urgency
- customer behavior
- engagement patterns
- campaign objective

Return:

{
  "recommended_channel":"",
  "confidence":0.0,
  "reasoning":""
}

Never write copy.

Never create segments.

Never launch campaigns.
```

---

# REVIEW NODE

File:

```text
nodes/review.py
```

Purpose:

Create campaign proposal.

This is the final planning step.

---

# REVIEW AGENT SYSTEM PROMPT

```text
You are a Campaign Director.

Your responsibility is creating final campaign proposals.

Combine:

- audience
- messaging
- channel recommendation

Generate:

- campaign title
- audience summary
- expected outcome
- risk assessment

Do not launch campaigns.

Do not change strategy.

Summarize only.
```

---

# REVIEW OUTPUT

```json
{
  "campaign_name":"",
  "summary":"",
  "channel":"",
  "expected_outcome":"",
  "risks":""
}
```

---

# OPPORTUNITY NODE

File:

```text
nodes/opportunities.py
```

Purpose:

Find revenue opportunities.

---

# OPPORTUNITY AGENT SYSTEM PROMPT

```text
You are a Revenue Opportunity Analyst.

Your objective is discovering growth opportunities.

Search for:

- churn risk
- VIP retention
- cross-sell opportunities
- upsell opportunities
- inactive high-value customers

Every opportunity must include:

- title
- expected_revenue
- confidence
- reasoning

Output JSON only.

Never generate messages.

Never launch campaigns.
```

---

# OPPORTUNITY OUTPUT

```json
{
  "title":"",
  "expected_revenue":0,
  "confidence":0.0,
  "reasoning":""
}
```

---

# INSIGHTS NODE

File:

```text
nodes/insights.py
```

Purpose:

Convert analytics into recommendations.

---

# INSIGHTS AGENT SYSTEM PROMPT

```text
You are a Marketing Intelligence Analyst.

Your responsibility is converting raw metrics into actionable insights.

Analyze:

- Open Rate
- Click Rate
- Conversion Rate
- Revenue
- Channel Performance

Generate:

1. Key Findings
2. Explanations
3. Recommendations
4. Next Best Actions

Avoid generic observations.

Be specific.
```

---

# INSIGHT OUTPUT FORMAT

```json
{
  "findings":[],
  "recommendations":[],
  "next_actions":[]
}
```

---

# DISPATCH NODE

File:

```text
nodes/dispatch.py
```

Purpose:

Execute approved campaigns.

This node must NEVER make decisions.

---

# DISPATCH AGENT SYSTEM PROMPT

```text
You are the Campaign Execution Agent.

You do not think.

You do not strategize.

You do not generate messages.

You do not create audiences.

You only execute approved campaigns.

Responsibilities:

1. Create Campaign
2. Create Communications
3. Send To Channel Service
4. Mark Campaign Running

Nothing else.
```

---

# SSE STREAMING PROTOCOL

All AI interactions use:

```http
POST /api/agent/chat
```

Response:

```http
text/event-stream
```

---

# STREAM EVENT TYPES

### Text

```json
{
  "type":"text",
  "content":"..."
}
```

---

### Segment Proposal

```json
{
  "type":"segment_proposal",
  "data":{}
}
```

---

### Message Proposal

```json
{
  "type":"message_proposal",
  "data":{}
}
```

---

### Campaign Proposal

```json
{
  "type":"campaign_proposal",
  "data":{}
}
```

---

### Opportunity

```json
{
  "type":"opportunity",
  "data":{}
}
```

---

### Insight

```json
{
  "type":"insight",
  "data":{}
}
```

---

### Done

```json
{
  "type":"done"
}
```

---

# FRONTEND RENDERING RULES

Never display raw JSON.

Convert every response into UI cards.

Examples:

```text
Segment Proposal Card

Message Proposal Card

Campaign Proposal Card

Opportunity Card

Insight Card
```

---

# AI STUDIO WORKFLOW

```text
User Goal
      ↓
Agent Chat
      ↓
Segment Proposal
      ↓
Approve
      ↓
Message Proposal
      ↓
Approve
      ↓
Campaign Proposal
      ↓
Approve
      ↓
Dispatch
      ↓
Launch Campaign
```

This is the primary product experience.

---

# AI COMMAND CENTRE

Purpose:

Global AI Copilot.

Capabilities:

```text
Campaign Creation

Opportunity Discovery

Analytics Interpretation

System Monitoring

CRM Questions
```

Accessible from every page.

---

# AGENT SUCCESS CRITERIA

The AI layer is successful only if:

✓ Understands marketing goals

✓ Creates meaningful segments

✓ Generates campaign copy

✓ Recommends channels

✓ Produces opportunities

✓ Explains analytics

✓ Requires approval before launch

✓ Launches campaigns after approval

✓ Streams responses to frontend

The AI system should feel like a Campaign Intelligence Platform, not a chatbot.

# Claude MD part 4
# CLAUDE.md — PART 4

# CHANNEL SERVICE ARCHITECTURE

The Channel Service is a completely independent FastAPI microservice.

Its purpose is to simulate real-world communication providers.

Think of it as:

* Twilio
* SendGrid
* Gupshup
* Meta WhatsApp
* RCS Provider

combined into a single simulated service.

The Channel Service does NOT deliver real messages.

It simulates:

* sending
* delivery
* opens
* reads
* clicks
* conversions
* failures

and reports those events back to the App Service.

---

# CHANNEL SERVICE DESIGN PRINCIPLE

The App Service owns:

* Customers
* Orders
* Segments
* Campaigns
* Analytics

The Channel Service owns:

* Queue
* Workers
* Event Simulation
* Retry Logic
* Delivery Lifecycle

These boundaries are strict.

Never place simulation logic in the App Service.

Never place campaign logic in the Channel Service.

---

# CHANNEL SERVICE DIRECTORY STRUCTURE

```text
channel-service/

├── main.py
│
├── queue_worker.py
│
├── simulator.py
│
├── schemas.py
│
├── models.py
│
├── services/
│   ├── callback_service.py
│   ├── event_service.py
│   └── queue_service.py
│
├── utils/
│   ├── logger.py
│   └── retry.py
│
└── requirements.txt
```

---

# CHANNEL SERVICE RESPONSIBILITIES

The Channel Service must:

1. Accept send requests
2. Queue jobs
3. Process jobs asynchronously
4. Simulate delivery lifecycle
5. Send callbacks
6. Retry failed callbacks
7. Track statistics
8. Expose monitoring endpoints

---

# SEND API

Endpoint:

```http
POST /send
```

Request:

```json
{
  "communication_id": "uuid",
  "campaign_id": "uuid",
  "customer_id": "uuid",
  "channel": "whatsapp",
  "message": "Hi Rahul...",
  "callback_url": "http://backend:8000/api/receipts/callback"
}
```

Response:

```json
{
  "accepted": true,
  "job_id": "uuid"
}
```

Rules:

* Must return immediately
* Must never block
* Must enqueue work
* Must never simulate inside request handler

---

# JOB MODEL

Internal queue object:

```python
{
    "job_id": str,
    "communication_id": str,
    "campaign_id": str,
    "customer_id": str,
    "channel": str,
    "message": str,
    "callback_url": str,
    "created_at": datetime
}
```

---

# QUEUE ARCHITECTURE

Use:

```python
asyncio.Queue
```

Do not use:

```text
Celery
Redis
RabbitMQ
Kafka
```

Reason:

Assignment scope.

Document in README:

At scale replace asyncio.Queue with Redis/Celery.

---

# QUEUE WORKER

File:

```text
queue_worker.py
```

Purpose:

Consume queued jobs.

---

# WORKER STARTUP

On FastAPI startup:

```python
asyncio.create_task(worker())
```

must launch.

Workers run continuously.

---

# WORKER FLOW

```text
Receive Job
      ↓
Queue
      ↓
Worker Picks Job
      ↓
Send Event
      ↓
Delivery Event
      ↓
Open Event
      ↓
Read Event
      ↓
Click Event
      ↓
Conversion Event
```

Every step happens asynchronously.

---

# EVENT LIFECYCLE

Success path:

```text
queued
 ↓
sent
 ↓
delivered
 ↓
opened
 ↓
read
 ↓
clicked
 ↓
converted
```

Failure path:

```text
queued
 ↓
sent
 ↓
failed
```

---

# EVENT TIMING

Use realistic delays.

### sent

Immediately.

```text
0-1 sec
```

---

### delivered

```text
1-4 sec
```

after sent.

---

### opened

```text
3-10 sec
```

after delivered.

---

### read

```text
2-6 sec
```

after opened.

---

### clicked

```text
1-4 sec
```

after read.

---

### converted

```text
2-8 sec
```

after clicked.

---

# CHANNEL BEHAVIOR MODEL

Different channels should behave differently.

Avoid identical probabilities.

---

# WHATSAPP

```python
DELIVERY = 0.92
OPEN = 0.75
READ = 0.82
CLICK = 0.28
CONVERT = 0.10
```

Characteristics:

* Highest engagement
* Strong read rates
* Strong click rates

---

# SMS

```python
DELIVERY = 0.96
OPEN = 0.85
READ = 0.90
CLICK = 0.12
CONVERT = 0.05
```

Characteristics:

* Excellent delivery
* Short attention span
* Lower conversions

---

# EMAIL

```python
DELIVERY = 0.87
OPEN = 0.35
READ = 0.65
CLICK = 0.18
CONVERT = 0.14
```

Characteristics:

* Lower opens
* Better purchase intent

---

# RCS

```python
DELIVERY = 0.85
OPEN = 0.50
READ = 0.70
CLICK = 0.22
CONVERT = 0.09
```

Characteristics:

* Rich media
* Moderate engagement

---

# EVENT SIMULATOR

File:

```text
simulator.py
```

Responsibilities:

```text
Generate outcomes

Generate delays

Generate engagement

Generate conversions
```

Must feel realistic.

Never always succeed.

---

# RANDOMIZATION RULES

Each communication should produce unique outcomes.

Avoid deterministic behavior.

Example:

Campaign A

```text
Customer 1 → converted

Customer 2 → clicked

Customer 3 → opened

Customer 4 → failed
```

Campaign B

Different outcomes.

---

# CALLBACK SERVICE

Purpose:

Send events back to App Service.

---

# CALLBACK PAYLOAD

```json
{
  "communication_id":"uuid",
  "campaign_id":"uuid",
  "customer_id":"uuid",
  "channel":"whatsapp",
  "event":"opened",
  "timestamp":"2026-01-01T12:00:00Z"
}
```

---

# CALLBACK FLOW

```text
Worker
   ↓
Generate Event
   ↓
Callback Service
   ↓
POST Receipt
   ↓
App Service
```

---

# CALLBACK RETRY SYSTEM

Real systems experience failures.

Simulate that behavior.

---

# FAILURE RATE

Artificially simulate:

```python
10%
```

callback failure rate.

Purpose:

Exercise retry logic.

---

# RETRY STRATEGY

Attempt:

```text
Attempt 1
```

If fail:

```text
2 sec delay
```

---

Attempt 2:

```text
4 sec delay
```

---

Attempt 3:

```text
8 sec delay
```

---

If still failing:

Mark:

```text
callback_failed
```

and log error.

---

# RETRY RULES

Retry only:

```text
network failures

5xx responses

timeouts
```

Do not retry:

```text
400

401

403
```

---

# EVENT LOG

Maintain in-memory event log.

Purpose:

Pipeline Monitor page.

---

# EVENT LOG FORMAT

```python
{
    "timestamp": "...",
    "event": "delivered",
    "communication_id": "...",
    "status": "OK"
}
```

---

# PIPELINE EVENTS

Examples:

```text
Campaign Queued

Worker Picked Job

Sent

Delivered

Opened

Clicked

Converted

Retry Attempt

Callback Failed
```

---

# HEALTH ENDPOINT

Endpoint:

```http
GET /health
```

Response:

```json
{
  "status":"ok",
  "queue_depth":10,
  "processed_total":4500
}
```

---

# STATS ENDPOINT

Endpoint:

```http
GET /stats
```

Response:

```json
{
  "total_sent":1000,
  "total_delivered":900,
  "total_opened":450,
  "total_clicked":120,
  "total_converted":12
}
```

---

# PIPELINE MONITOR INTEGRATION

Pipeline Monitor page depends on:

```text
queue depth

active jobs

recent events

worker status
```

Channel Service must expose all required metrics.

---

# REAL-TIME MONITORING

Frontend polls:

```text
every 5 seconds
```

No WebSockets required.

Polling is acceptable for assignment scope.

---

# CAMPAIGN EXECUTION FLOW

Complete lifecycle:

```text
AI Agent
     ↓
Proposal
     ↓
Approve
     ↓
Campaign Created
     ↓
Launch Campaign
     ↓
Create Communications
     ↓
POST /send
     ↓
Channel Queue
     ↓
Worker
     ↓
Simulated Events
     ↓
Receipt Callback
     ↓
Database Update
     ↓
Analytics Update
     ↓
Frontend Refresh
```

This flow MUST work end-to-end.

---

# PIPELINE MONITOR PAGE REQUIREMENTS

The following metrics should be derivable:

```text
Active Campaigns

Queue Depth

Workers Processing

Messages Sent

Messages Delivered

Messages Opened

Messages Clicked

Messages Converted
```

---

# FAILURE SCENARIOS TO HANDLE

### Duplicate Callback

```text
opened
opened
opened
```

Backend should ignore duplicates.

---

### Delayed Callback

```text
clicked arrives late
```

Backend should process normally.

---

### Out-of-Order Event

```text
clicked before opened
```

Backend should reject.

---

### Worker Crash

If worker fails:

```text
log error
continue processing
```

Do not crash service.

---

# LOGGING

Every major action must log:

```text
job accepted

job queued

worker picked

event generated

callback sent

callback retry

callback failed
```

Logs should be human-readable.

---

# PRODUCTION TRADEOFF DOCUMENTATION

README must explain:

### Why asyncio.Queue?

Simple.

No external dependencies.

Fast implementation.

---

### Why polling instead of WebSockets?

Simpler.

Adequate for campaign monitoring.

Lower complexity.

---

### Why in-memory logs?

Assignment scope.

At scale:

```text
Redis

Kafka

ClickHouse

Elasticsearch
```

would be used.

---

# CHANNEL SERVICE SUCCESS CRITERIA

The Channel Service is considered complete only when:

✓ Jobs are queued

✓ Workers process jobs

✓ Events are generated

✓ Callbacks are delivered

✓ Retries work

✓ Pipeline monitor updates

✓ Analytics update

✓ Campaign detail page reflects event progression

✓ End-to-end campaign lifecycle is visible to users

The callback-driven architecture is one of the most important evaluation points of this assignment.

Implement it carefully and make it demonstrable during the walkthrough video.


# Claude MD part 5

# CLAUDE.md — PART 5

# SEED DATA STRATEGY

The application should look realistic immediately after setup.

After running:

```bash
python seed.py
```

the application should feel like a real CRM with active campaigns and meaningful analytics.

---

# CUSTOMER SEEDING

Generate:

```text
10,000 Customers
```

Use:

```python
faker
locale="en_IN"
```

Generate:

* Indian names
* realistic emails
* realistic phone numbers
* realistic cities
* realistic ages
* realistic demographics

Cities:

```text
Mumbai
Delhi
Bangalore
Hyderabad
Chennai
Kolkata
Pune
Jaipur
Ahmedabad
```

Age Distribution:

```text
18-65
```

Gender:

```text
male
female
other
```

---

# ORDER SEEDING

Generate:

```text
30,000+ Orders
```

Average:

```text
3 orders per customer
```

Categories:

```text
fashion

beauty

food

electronics

accessories
```

Order Value:

```text
₹200
↓
₹15,000
```

Order Dates:

```text
Last 24 Months
```

---

# CUSTOMER METRICS

Compute:

```python
ltv

total_orders

last_order_at
```

after inserting orders.

Store values on Customer table.

---

# AI SUGGESTED SEGMENTS

Automatically create:

### VIP Customers

```text
ltv > 10000
```

---

### Inactive 60+ Days

```text
last_order > 60 days
```

---

### High Value Fashion Buyers

```text
category=fashion

AND

ltv > 5000
```

---

### New Customers

```text
created_at < 30 days
```

---

### At Risk Reactivation

```text
ltv > 2000

AND

last_order > 45 days
```

---

# OPPORTUNITY SEEDING

Generate:

```text
5 Opportunities
```

Examples:

```text
Cross Sell Accessories

VIP Retention

High Value Reactivation

Fashion Upsell

Beauty Cross Sell
```

Each should include:

```text
Expected Revenue

Confidence

AI Reasoning
```

---

# AGENT PROPOSAL SEEDING

Generate:

```text
3 Pending Proposals
```

Each proposal should include:

```text
Campaign Name

Audience

Message

Confidence Score

Reasoning
```

---

# A/B TEST SEEDING

Generate:

```text
2 Completed Tests
```

Example:

### Summer Sale Offer Test

Variant A:

```text
72.5% Open

22.3% CTR

4.8% Conversion
```

Variant B:

```text
68.2% Open

18.7% CTR

3.9% Conversion
```

Winner:

```text
A
```

---

### Re-engagement Test

Variant A:

```text
WhatsApp
```

Variant B:

```text
SMS
```

Status:

```text
Running
```

---

# PAGE IMPLEMENTATION PRIORITY

Build pages in this order.

---

## Login

Route:

```text
/login
```

Features:

* Clerk Auth
* Google Login
* Email Login
* Custom ShadCN UI

---

## Dashboard

Route:

```text
/
```

Features:

* KPI Cards
* Quick Actions
* Recent Campaigns
* Analytics Overview

---

## Customers

Route:

```text
/customers
```

Features:

* Search
* Filters
* Pagination
* Customer Cards
* Customer Details

---

## Segments

Route:

```text
/segments
```

Features:

* AI Suggested
* Manual Segments
* Segment Builder

---

## Campaigns

Route:

```text
/campaigns
```

Features:

* Campaign List
* Status Tracking
* Metrics

---

## Campaign Detail

Route:

```text
/campaigns/:id
```

Features:

* Funnel
* Communication Table
* Real-Time Updates

---

## AI Campaign Studio

Route:

```text
/ai-studio
```

Features:

* AI Chat
* Segment Proposal
* Message Proposal
* Campaign Proposal
* Approval Workflow

---

## Opportunities

Route:

```text
/opportunities
```

Features:

* Opportunity Cards
* Generate Campaign
* Dismiss

---

## Agent Proposals

Route:

```text
/proposals
```

Features:

* Approve
* Reject
* Launch

Must load real DB data.

Never show:

```text
Failed to load proposals
```

---

## A/B Tests

Route:

```text
/ab-tests
```

Features:

* Variant Comparison
* Winner Display
* Metrics

---

## Analytics

Route:

```text
/analytics
```

Features:

* Channel Performance
* Funnel
* Revenue Analysis

---

## Pipeline Monitor

Route:

```text
/pipeline
```

Features:

* Queue Metrics
* Event Timeline
* Worker Status

---

## Settings

Route:

```text
/settings
```

Features:

* General Settings
* Notification Settings
* AI Configuration
* Telegram Integration

---

# AI COMMAND CENTRE

Global modal.

Accessible from every page.

Purpose:

```text
CRM Copilot

System Monitor

Campaign Assistant
```

Capabilities:

```text
Generate Campaigns

Explain Analytics

Discover Opportunities

Answer CRM Questions

Show System Health
```

---

# DEPLOYMENT ARCHITECTURE

Frontend:

```text
Vercel
```

Backend:

```text
Render
```

Channel Service:

```text
Render
```

Database:

```text
Render PostgreSQL

or

Supabase
```

---

# DOCKER REQUIREMENTS

Application must run via:

```bash
docker-compose up
```

No manual setup.

Services:

```text
postgres

backend

channel-service

frontend
```

must start successfully.

---

# ENVIRONMENT VARIABLES

Frontend:

```env
VITE_API_URL=

VITE_CLERK_PUBLISHABLE_KEY=
```

Backend:

```env
DATABASE_URL=

GROQ_API_KEY=

OPENAI_API_KEY=

OPENAI_BASE_URL=

OPENAI_MODEL=

CHANNEL_SERVICE_URL=

CLERK_SECRET_KEY=
```

Channel Service:

```env
CORE_BACKEND_URL=
```

---

# README REQUIREMENTS

README must contain:

---

## Project Overview

Explain:

```text
What Xeno AI Is
```

---

## Architecture Diagram

Show:

```text
Frontend

Backend

Agent Layer

Channel Service

Database
```

---

## Setup

Document:

```bash
docker-compose up
```

---

## Environment Variables

List all required variables.

---

## Database Setup

Explain migrations.

---

## Seed Data

Explain:

```bash
python seed.py
```

---

## Deployment

Explain:

```text
Frontend → Vercel

Backend → Render

Channel → Render

Database → PostgreSQL
```

---

## AI Architecture

Explain:

```text
Intent Agent

Segment Agent

Compose Agent

Channel Agent

Review Agent

Dispatch Agent

Insights Agent

Opportunity Agent
```

---

## Campaign Lifecycle

Document:

```text
Create

Approve

Launch

Queue

Simulate

Callback

Analytics
```

---

## Tradeoffs

Document explicitly:

### asyncio.Queue

Used for simplicity.

At scale:

```text
Redis

Celery
```

---

### Polling

Used instead of WebSockets.

Simpler.

Adequate for assignment.

---

### Single LangGraph

Chosen for:

```text
Maintainability

Observability

Debugging
```

instead of multiple autonomous agents.

---

### App Service + Channel Service

Separated intentionally.

Mirrors real communication systems.

---

### PostgreSQL

Single source of truth.

---

# WALKTHROUGH VIDEO REQUIREMENTS

The final application must support a 5-6 minute walkthrough.

Recommended flow:

---

## Product Intro

30 Seconds

Explain:

```text
AI Native Campaign Intelligence Platform
```

---

## AI Studio

Show:

```text
Natural Language Goal
↓
Audience Discovery
↓
Campaign Proposal
```

---

## Campaign Launch

Show:

```text
Approve
↓
Launch
```

---

## Pipeline Monitor

Show:

```text
Queue

Workers

Events
```

---

## Campaign Detail

Show:

```text
Real-Time Updates

Funnel Progression
```

---

## Analytics

Show:

```text
Open Rates

Clicks

Conversions
```

---

## Architecture

Show:

```text
Frontend

Backend

Agent

Channel Service
```

---

## Code Walkthrough

Explain:

```text
Service Layer

LangGraph

Receipt Processor

Channel Simulation
```

---

# NON-NEGOTIABLES

The following MUST work.

---

### Separate Channel Service

Required.

No exceptions.

---

### Callback Lifecycle

Required.

No fake analytics.

---

### Agent Proposals

Must come from database.

Not hardcoded.

---

### AI Suggested Segments

Must compute customer counts.

Not hardcoded.

---

### Real AI Responses

Must use LLM.

No mocked outputs.

---

### Human Approval

Required before launch.

---

### Idempotent Receipt Processing

Required.

---

### Campaign Funnel

Must reflect real communication events.

---

### Pipeline Monitor

Must show real queue activity.

---

### Dashboard Metrics

Must come from database.

---

### Deployment

Must be publicly accessible.

---

# BUILD ORDER

Follow exactly.

```text
1. Database Models
2. Alembic Migrations
3. Seed Script
4. CRUD APIs
5. Channel Service
6. Campaign Launch
7. Receipt Processing
8. Analytics
9. Opportunities
10. Proposals
11. LangGraph
12. SSE Streaming
13. Frontend
14. AI Studio
15. Pipeline Monitor
16. Docker
17. Deployment
18. Walkthrough
```

---

# FINAL SUCCESS DEFINITION

The project is complete when a marketer can:

```text
Describe Goal
      ↓
AI Builds Audience
      ↓
AI Creates Message
      ↓
AI Recommends Channel
      ↓
Human Approves
      ↓
Campaign Launches
      ↓
Channel Service Simulates Events
      ↓
Analytics Update
      ↓
AI Generates Insights
```

without manual intervention.

The application should feel like a modern AI-native Campaign Intelligence Platform and clearly demonstrate strong product thinking, system design, and engineering execution.

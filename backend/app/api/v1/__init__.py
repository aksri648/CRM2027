from fastapi import APIRouter
from app.api.v1 import auth, customers, segments, campaigns, callbacks, ai
from app.api.v1 import opportunities, proposals, ab_tests, pipeline, settings, analytics, agent
from app.api.v1 import orders

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(customers.router)
api_router.include_router(segments.router)
api_router.include_router(campaigns.router)
api_router.include_router(callbacks.router)
api_router.include_router(ai.router)
api_router.include_router(opportunities.router)
api_router.include_router(proposals.router)
api_router.include_router(ab_tests.router)
api_router.include_router(pipeline.router)
api_router.include_router(settings.router)
api_router.include_router(analytics.router)
api_router.include_router(agent.router)
api_router.include_router(orders.router)
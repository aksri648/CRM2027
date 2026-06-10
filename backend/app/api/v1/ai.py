from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.customer import Customer
from app.models.order import Order
from app.models.product import Product
from app.services.ai_service import ai_service

router = APIRouter(prefix="/ai", tags=["AI"])


class ChatRequest(BaseModel):
    message: str
    context: Optional[Dict[str, Any]] = None


class ChatResponse(BaseModel):
    response: str


class SuggestSegmentRequest(BaseModel):
    goal: str


class GenerateMessageRequest(BaseModel):
    campaign_goal: str
    audience: str
    count: int = 3


class AnalyzeCampaignRequest(BaseModel):
    sent_count: int
    delivered_count: int
    delivered_rate: float
    opened_count: int
    opened_rate: float
    clicked_count: int
    clicked_rate: float
    converted_count: int
    converted_rate: float
    revenue: float


@router.post("/chat", response_model=ChatResponse)
def ai_chat(
    request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Natural language interface for the CRM"""
    # Get context about the brand
    customer_count = db.query(Customer).filter(Customer.brand_id == current_user.brand_id).count()
    order_count = db.query(Order).filter(Order.brand_id == current_user.brand_id).count()
    
    context = {
        "brand_id": current_user.brand_id,
        "customer_count": customer_count,
        "order_count": order_count
    }
    
    response = ai_service.chat(request.message, context)
    return ChatResponse(response=response)


@router.post("/suggest-segment")
def suggest_segment(
    request: SuggestSegmentRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """AI suggest a segment based on marketing goal"""
    # Get customer data summary
    total_customers = db.query(Customer).filter(Customer.brand_id == current_user.brand_id).count()
    
    # Get top cities
    top_cities = db.query(Customer.city, func.count(Customer.id).label("count")).filter(
        Customer.brand_id == current_user.brand_id,
        Customer.city.isnot(None)
    ).group_by(Customer.city).order_by(func.count(Customer.id).desc()).limit(5).all()
    
    # Get average order value
    avg_order = db.query(func.avg(Order.total)).filter(
        Order.brand_id == current_user.brand_id
    ).scalar() or 0
    
    customer_data = {
        "total_customers": total_customers,
        "avg_order_value": float(avg_order),
        "top_cities": [c[0] for c in top_cities] if top_cities else [],
        "top_products": []  # Would need product join
    }
    
    suggestion = ai_service.suggest_segment(request.goal, customer_data)
    return suggestion


@router.post("/generate-messages", response_model=List[str])
def generate_message_variants(
    request: GenerateMessageRequest,
    current_user: User = Depends(get_current_user)
):
    """Generate message variants for a campaign"""
    variants = ai_service.generate_message_variants(
        request.campaign_goal,
        request.audience,
        request.count
    )
    return variants


@router.post("/suggest-channel")
def suggest_channel(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Suggest best channel for a customer"""
    customer = db.query(Customer).filter(
        Customer.id == customer_id,
        Customer.brand_id == current_user.brand_id
    ).first()
    
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    customer_data = {
        "email": customer.email,
        "phone": customer.phone,
        "preferred_channel": customer.preferred_channel.value if customer.preferred_channel else None,
        "engagement_score": customer.engagement_score,
        "last_engaged_at": customer.last_engaged_at.isoformat() if customer.last_engaged_at else None
    }
    
    suggestion = ai_service.suggest_channel(customer_data)
    return {"suggested_channel": suggestion}


@router.post("/analyze-campaign")
def analyze_campaign(
    request: AnalyzeCampaignRequest,
    current_user: User = Depends(get_current_user)
):
    """AI-powered campaign analysis"""
    stats = request.model_dump()
    analysis = ai_service.analyze_campaign_performance(stats)
    return analysis
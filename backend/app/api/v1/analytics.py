from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from pydantic import BaseModel

from app.core.database import get_db
from app.core.security import get_current_user
from app.models import Campaign, Communication, Customer, User

router = APIRouter(prefix="/analytics", tags=["analytics"])


class OverviewStats(BaseModel):
    total_customers: int
    active_campaigns: int
    messages_sent: int
    revenue_attributed: float
    trends: dict = {}


class ChannelStats(BaseModel):
    channel: str
    sent: int
    delivery_rate: float
    open_rate: float
    click_rate: float
    conversion: float


class CampaignStats(BaseModel):
    id: str
    name: str
    channel: str
    sent: int
    revenue: float


class FunnelStats(BaseModel):
    sent: int
    delivered: int
    opened: int
    clicked: int
    converted: int


@router.get("/overview")
def get_overview(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get analytics overview"""
    total_customers = db.query(Customer).count()
    active_campaigns = db.query(Campaign).filter(Campaign.status == "running").count()
    
    # Count messages
    messages_sent = db.query(Communication).filter(
        Communication.status.in_(["sent", "delivered", "opened", "read", "clicked", "converted"])
    ).count()
    
    # Calculate revenue (mock for now)
    revenue_attributed = messages_sent * 12.5  # Mock calculation
    
    return {
        "total_customers": total_customers,
        "active_campaigns": active_campaigns,
        "messages_sent": messages_sent,
        "revenue_attributed": revenue_attributed,
        "trends": {
            "customers_change": 12.5,
            "campaigns_change": 2,
            "messages_change": 12.3,
            "revenue_change": 5.4
        }
    }


@router.get("/channels", response_model=List[ChannelStats])
def get_channel_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get per-channel statistics"""
    channels = ["whatsapp", "sms", "email", "rcs"]
    stats = []
    
    for channel in channels:
        sent = db.query(Communication).filter(
            Communication.channel == channel,
            Communication.status.in_(["sent", "delivered", "opened", "read", "clicked", "converted"])
        ).count()
        
        delivered = db.query(Communication).filter(
            Communication.channel == channel,
            Communication.status.in_(["delivered", "opened", "read", "clicked", "converted"])
        ).count()
        
        opened = db.query(Communication).filter(
            Communication.channel == channel,
            Communication.status.in_(["opened", "read", "clicked", "converted"])
        ).count()
        
        clicked = db.query(Communication).filter(
            Communication.channel == channel,
            Communication.status.in_(["clicked", "converted"])
        ).count()
        
        converted = db.query(Communication).filter(
            Communication.channel == channel,
            Communication.status == "converted"
        ).count()
        
        stats.append(ChannelStats(
            channel=channel,
            sent=sent,
            delivery_rate=(delivered / sent * 100) if sent > 0 else 0,
            open_rate=(opened / delivered * 100) if delivered > 0 else 0,
            click_rate=(clicked / opened * 100) if opened > 0 else 0,
            conversion=(converted / clicked * 100) if clicked > 0 else 0,
        ))
    
    return stats


@router.get("/campaigns/top", response_model=List[CampaignStats])
def get_top_campaigns(
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get top campaigns by revenue"""
    campaigns = db.query(Campaign).limit(limit).all()
    return [
        CampaignStats(
            id=str(c.id),
            name=c.name,
            channel=c.channel,
            sent=0,  # Would need to join with communications
            revenue=0  # Would need to calculate from communications
        )
        for c in campaigns
    ]


@router.get("/funnel", response_model=FunnelStats)
def get_funnel_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get aggregate funnel counts"""
    sent = db.query(Communication).filter(
        Communication.status.in_(["sent", "delivered", "opened", "read", "clicked", "converted"])
    ).count()
    
    delivered = db.query(Communication).filter(
        Communication.status.in_(["delivered", "opened", "read", "clicked", "converted"])
    ).count()
    
    opened = db.query(Communication).filter(
        Communication.status.in_(["opened", "read", "clicked", "converted"])
    ).count()
    
    clicked = db.query(Communication).filter(
        Communication.status.in_(["clicked", "converted"])
    ).count()
    
    converted = db.query(Communication).filter(
        Communication.status == "converted"
    ).count()
    
    return FunnelStats(
        sent=sent,
        delivered=delivered,
        opened=opened,
        clicked=clicked,
        converted=converted
    )
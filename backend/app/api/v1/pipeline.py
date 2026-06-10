from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel
from typing import List

from app.core.database import get_db
from app.core.security import get_current_user
from app.models import Campaign, Communication, User

router = APIRouter(prefix="/pipeline", tags=["pipeline"])


class PipelineStatus(BaseModel):
    active_campaigns: int
    queue_depth: int
    workers_processing: int
    total_sent: int
    total_delivered: int
    total_opened: int
    total_clicked: int
    total_converted: int


class PipelineEvent(BaseModel):
    id: str
    timestamp: str
    event_type: str
    description: str
    status: str


@router.get("/status", response_model=PipelineStatus)
def get_pipeline_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get pipeline status"""
    # Count active campaigns for this brand
    active_campaigns = db.query(Campaign).filter(
        Campaign.brand_id == current_user.brand_id,
        Campaign.status == "running"
    ).count()
    
    # Count queued communications for this brand
    queue_depth = db.query(Communication).filter(
        Communication.brand_id == current_user.brand_id,
        Communication.status == "queued"
    ).count()
    
    # Count communications by status for this brand
    total_sent = db.query(Communication).filter(
        Communication.brand_id == current_user.brand_id,
        Communication.status.in_(["sent", "delivered", "opened", "read", "clicked", "converted"])
    ).count()
    total_delivered = db.query(Communication).filter(
        Communication.brand_id == current_user.brand_id,
        Communication.status.in_(["delivered", "opened", "read", "clicked", "converted"])
    ).count()
    total_opened = db.query(Communication).filter(
        Communication.brand_id == current_user.brand_id,
        Communication.status.in_(["opened", "read", "clicked", "converted"])
    ).count()
    total_clicked = db.query(Communication).filter(
        Communication.brand_id == current_user.brand_id,
        Communication.status.in_(["clicked", "converted"])
    ).count()
    total_converted = db.query(Communication).filter(
        Communication.brand_id == current_user.brand_id,
        Communication.status == "converted"
    ).count()
    
    # Count workers processing (communications with 'sending' status indicates active processing)
    workers_processing = db.query(Communication).filter(
        Communication.brand_id == current_user.brand_id,
        Communication.status == "sending"
    ).count()
    
    return PipelineStatus(
        active_campaigns=active_campaigns,
        queue_depth=queue_depth,
        workers_processing=workers_processing,
        total_sent=total_sent,
        total_delivered=total_delivered,
        total_opened=total_opened,
        total_clicked=total_clicked,
        total_converted=total_converted,
    )


@router.get("/events", response_model=List[PipelineEvent])
def get_pipeline_events(
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get recent pipeline events from communications"""
    from datetime import datetime
    
    # Get recent communications with status changes
    communications = db.query(Communication).filter(
        Communication.brand_id == current_user.brand_id
    ).order_by(Communication.updated_at.desc()).limit(limit).all()
    
    events = []
    for comm in communications:
        # Create events based on communication status
        status_map = {
            "queued": ("Queued", "event"),
            "sending": ("Sending", "event"),
            "sent": ("Sent", "ok"),
            "delivered": ("Delivered", "ok"),
            "opened": ("Opened", "ok"),
            "read": ("Read", "ok"),
            "clicked": ("Clicked", "ok"),
            "converted": ("Converted", "ok"),
            "failed": ("Failed", "error"),
        }
        
        event_type, status = status_map.get(comm.status, ("Unknown", "event"))
        
        events.append(PipelineEvent(
            id=str(comm.id),
            timestamp=comm.updated_at.isoformat() if comm.updated_at else datetime.utcnow().isoformat(),
            event_type=event_type,
            description=f"Campaign {comm.campaign_id} - {comm.channel} to {comm.recipient[:20]}..." if comm.recipient else f"Campaign {comm.campaign_id}",
            status=status
        ))
    
    return events
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
    # Count active campaigns
    active_campaigns = db.query(Campaign).filter(Campaign.status == "running").count()
    
    # Count queued communications
    queue_depth = db.query(Communication).filter(Communication.status == "queued").count()
    
    # Count communications by status
    total_sent = db.query(Communication).filter(Communication.status.in_(["sent", "delivered", "opened", "read", "clicked", "converted"])).count()
    total_delivered = db.query(Communication).filter(Communication.status.in_(["delivered", "opened", "read", "clicked", "converted"])).count()
    total_opened = db.query(Communication).filter(Communication.status.in_(["opened", "read", "clicked", "converted"])).count()
    total_clicked = db.query(Communication).filter(Communication.status.in_(["clicked", "converted"])).count()
    total_converted = db.query(Communication).filter(Communication.status == "converted").count()
    
    return PipelineStatus(
        active_campaigns=active_campaigns,
        queue_depth=queue_depth,
        workers_processing=3,  # Mock value
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
    """Get recent pipeline events"""
    # Mock events for demo
    events = [
        PipelineEvent(
            id="1",
            timestamp="10:32:15 AM",
            event_type="Campaign Dispatched",
            description="Summer Sale → WhatsApp Queue",
            status="event"
        ),
        PipelineEvent(
            id="2",
            timestamp="10:32:18 AM",
            event_type="Worker Picked",
            description="worker-03 processing message batch",
            status="ok"
        ),
        PipelineEvent(
            id="3",
            timestamp="10:32:22 AM",
            event_type="Message Sent",
            description="Batch of 50 messages dispatched",
            status="ok"
        ),
        PipelineEvent(
            id="4",
            timestamp="10:32:25 AM",
            event_type="Delivery Confirmed",
            description="47/50 messages delivered",
            status="ok"
        ),
        PipelineEvent(
            id="5",
            timestamp="10:32:30 AM",
            event_type="Retry Attempt",
            description="3 messages retrying after timeout",
            status="retry"
        ),
    ]
    return events
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from datetime import datetime
import json
from app.core.database import get_db
from app.core.config import settings
from app.models.communication import Communication, CommunicationEvent, CommunicationStatus, CommunicationEventType
from app.models.campaign import Campaign, CampaignStatus
from app.models.customer import Customer
from app.schemas.communication import CallbackRequest, CallbackResponse

router = APIRouter(prefix="/callbacks", tags=["Callbacks"])


def verify_api_key(x_api_key: str = Header(None)):
    if x_api_key != settings.CHANNEL_SERVICE_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return True


@router.post("/{external_id}", response_model=CallbackResponse)
def handle_callback(
    external_id: str,
    request: CallbackRequest,
    db: Session = Depends(get_db),
    _: bool = Depends(verify_api_key)
):
    """Handle callbacks from channel service"""
    # Find communication by external_id
    comm = db.query(Communication).filter(Communication.external_id == external_id).first()
    
    if not comm:
        return CallbackResponse(success=False, message="Communication not found")
    
    event_type = request.event_type
    occurred_at = request.occurred_at or datetime.utcnow()
    
    # Create event record
    event = CommunicationEvent(
        communication_id=comm.id,
        event_type=event_type,
        metadata=request.metadata,
        occurred_at=occurred_at
    )
    db.add(event)
    
    # Update communication status based on event
    if event_type == "delivered":
        comm.status = CommunicationStatus.DELIVERED
        comm.delivered_at = occurred_at
        # Update campaign delivered count
        if comm.campaign_id:
            campaign = db.query(Campaign).filter(Campaign.id == comm.campaign_id).first()
            if campaign:
                campaign.delivered_count = (campaign.delivered_count or 0) + 1
    
    elif event_type in ["opened", "read"]:
        comm.status = CommunicationStatus.DELIVERED
        comm.opened_at = occurred_at
        # Update campaign opened count
        if comm.campaign_id:
            campaign = db.query(Campaign).filter(Campaign.id == comm.campaign_id).first()
            if campaign:
                campaign.opened_count = (campaign.opened_count or 0) + 1
        # Update customer engagement
        customer = db.query(Customer).filter(Customer.id == comm.customer_id).first()
        if customer:
            customer.engagement_score = (customer.engagement_score or 0) + 10
            customer.last_engaged_at = occurred_at
    
    elif event_type == "clicked":
        comm.status = CommunicationStatus.DELIVERED
        comm.clicked_at = occurred_at
        # Update campaign clicked count
        if comm.campaign_id:
            campaign = db.query(Campaign).filter(Campaign.id == comm.campaign_id).first()
            if campaign:
                campaign.clicked_count = (campaign.clicked_count or 0) + 1
        # Update customer engagement
        customer = db.query(Customer).filter(Customer.id == comm.customer_id).first()
        if customer:
            customer.engagement_score = (customer.engagement_score or 0) + 20
            customer.last_engaged_at = occurred_at
    
    elif event_type == "failed":
        comm.status = CommunicationStatus.FAILED
        # Update campaign failed count
        if comm.campaign_id:
            campaign = db.query(Campaign).filter(Campaign.id == comm.campaign_id).first()
            if campaign:
                campaign.failed_count = (campaign.failed_count or 0) + 1
    
    elif event_type == "bounced":
        comm.status = CommunicationStatus.BOUNCED
        if comm.campaign_id:
            campaign = db.query(Campaign).filter(Campaign.id == comm.campaign_id).first()
            if campaign:
                campaign.failed_count = (campaign.failed_count or 0) + 1
    
    elif event_type == "unsubscribed":
        comm.status = CommunicationStatus.UNSUBSCRIBED
        # Update customer unsubscribe status
        customer = db.query(Customer).filter(Customer.id == comm.customer_id).first()
        if customer:
            customer.is_unsubscribed = True
            customer.unsubscribed_at = occurred_at
    
    db.commit()
    
    return CallbackResponse(success=True, message=f"Callback processed: {event_type}")


@router.post("/delivery", response_model=CallbackResponse)
def handle_delivery_callback(
    request: CallbackRequest,
    db: Session = Depends(get_db),
    _: bool = Depends(verify_api_key)
):
    """Handle delivery status callbacks"""
    return handle_callback(request.metadata or "", request, db, _)


@router.post("/engagement", response_model=CallbackResponse)
def handle_engagement_callback(
    request: CallbackRequest,
    db: Session = Depends(get_db),
    _: bool = Depends(verify_api_key)
):
    """Handle engagement event callbacks"""
    return handle_callback(request.metadata or "", request, db, _)
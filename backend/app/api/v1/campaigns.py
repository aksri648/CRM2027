from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Optional
import json
import httpx
from datetime import datetime
from app.core.database import get_db
from app.core.security import get_current_user
from app.core.config import settings
from app.models.user import User
from app.models.campaign import Campaign, CampaignTemplate, CampaignStatus, CampaignChannel
from app.models.segment import Segment
from app.models.customer import Customer
from app.models.communication import Communication, CommunicationStatus
from app.schemas.campaign import (
    CampaignCreate, CampaignUpdate, CampaignResponse, CampaignStats,
    CampaignSendRequest, CampaignTemplateCreate, CampaignTemplateResponse
)

router = APIRouter(prefix="/campaigns", tags=["Campaigns"])


async def send_to_channel_service(communication_ids: list, campaign_id: int, brand_id: int):
    """Background task to send communications to channel service"""
    from app.core.database import SessionLocal
    
    async with httpx.AsyncClient() as client:
        for comm_id in communication_ids:
            # Re-query the communication with a fresh session
            db = SessionLocal()
            try:
                comm = db.query(Communication).filter(Communication.id == comm_id).first()
                if not comm:
                    continue
                    
                try:
                    response = await client.post(
                        f"{settings.CHANNEL_SERVICE_URL}/send",
                        json={
                            "external_id": comm.external_id,
                            "recipient": comm.recipient,
                            "channel": comm.channel,
                            "subject": comm.subject,
                            "content": comm.content,
                            "callback_url": f"{settings.CRM_CALLBACK_URL}/{comm.external_id}"
                        },
                        headers={"x-api-key": settings.CHANNEL_SERVICE_API_KEY},
                        timeout=30.0
                    )
                    if response.status_code != 202:
                        comm.status = CommunicationStatus.FAILED
                    else:
                        comm.status = CommunicationStatus.SENT
                        comm.sent_at = datetime.utcnow()
                except Exception as e:
                    comm.status = CommunicationStatus.FAILED
                
                db.commit()
            finally:
                db.close()


def get_segment_customers(db: Session, segment_id: int, brand_id: int) -> list:
    """Get customers from a segment"""
    segment = db.query(Segment).filter(
        Segment.id == segment_id,
        Segment.brand_id == brand_id
    ).first()
    
    if not segment:
        return []
    
    # Parse and apply segment rules
    rules = json.loads(segment.rules)
    from app.api.v1.segments import apply_segment_rules
    return apply_segment_rules(db, brand_id, rules)


def personalise_message(content: str, customer: Customer) -> str:
    """Replace personalisation tokens with customer data"""
    replacements = {
        "{{first_name}}": customer.first_name or "there",
        "{{last_name}}": customer.last_name or "",
        "{{email}}": customer.email or "",
        "{{city}}": customer.city or "",
    }
    
    result = content
    for token, value in replacements.items():
        result = result.replace(token, value)
    return result


@router.get("")
def list_campaigns(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    status: Optional[CampaignStatus] = None,
    channel: Optional[CampaignChannel] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Campaign).filter(Campaign.brand_id == current_user.brand_id)
    
    if status:
        query = query.filter(Campaign.status == status)
    if channel:
        query = query.filter(Campaign.channel == channel)
    
    total = query.count()
    campaigns = query.order_by(Campaign.created_at.desc()).offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "data": [CampaignResponse.model_validate(c) for c in campaigns]
    }


@router.post("")
def create_campaign(
    campaign_data: CampaignCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    campaign = Campaign(
        brand_id=current_user.brand_id,
        created_by=current_user.id,
        **campaign_data.model_dump()
    )
    db.add(campaign)
    db.commit()
    db.refresh(campaign)
    return CampaignResponse.model_validate(campaign)


@router.get("/{campaign_id}")
def get_campaign(
    campaign_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    campaign = db.query(Campaign).filter(
        Campaign.id == campaign_id,
        Campaign.brand_id == current_user.brand_id
    ).first()
    
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    return CampaignResponse.model_validate(campaign)


@router.put("/{campaign_id}")
def update_campaign(
    campaign_id: int,
    campaign_data: CampaignUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    campaign = db.query(Campaign).filter(
        Campaign.id == campaign_id,
        Campaign.brand_id == current_user.brand_id
    ).first()
    
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    if campaign.status == CampaignStatus.SENT:
        raise HTTPException(status_code=400, detail="Cannot update a sent campaign")
    
    update_data = campaign_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(campaign, field, value)
    
    db.commit()
    db.refresh(campaign)
    return CampaignResponse.model_validate(campaign)


@router.delete("/{campaign_id}")
def delete_campaign(
    campaign_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    campaign = db.query(Campaign).filter(
        Campaign.id == campaign_id,
        Campaign.brand_id == current_user.brand_id
    ).first()
    
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    if campaign.status == CampaignStatus.SENDING:
        raise HTTPException(status_code=400, detail="Cannot delete a campaign that is being sent")
    
    db.delete(campaign)
    db.commit()
    return {"message": "Campaign deleted successfully"}


@router.post("/{campaign_id}/send")
async def send_campaign(
    campaign_id: int,
    request: CampaignSendRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    campaign = db.query(Campaign).filter(
        Campaign.id == campaign_id,
        Campaign.brand_id == current_user.brand_id
    ).first()
    
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    if campaign.status == CampaignStatus.SENT:
        raise HTTPException(status_code=400, detail="Campaign already sent")
    
    # Get target customers
    if request.customer_ids:
        customers = db.query(Customer).filter(
            Customer.id.in_(request.customer_ids),
            Customer.brand_id == current_user.brand_id,
            Customer.is_unsubscribed == False
        ).all()
    elif request.segment_id:
        customers = get_segment_customers(db, request.segment_id, current_user.brand_id)
        customers = [c for c in customers if not c.is_unsubscribed]
    elif campaign.segment_id:
        customers = get_segment_customers(db, campaign.segment_id, current_user.brand_id)
        customers = [c for c in customers if not c.is_unsubscribed]
    else:
        raise HTTPException(status_code=400, detail="No target audience specified")
    
    if not customers:
        raise HTTPException(status_code=400, detail="No customers to send to")
    
    # Update campaign status
    campaign.status = CampaignStatus.SENDING
    campaign.target_count = len(customers)
    campaign.sent_at = datetime.utcnow()
    db.commit()
    
    # Create communications
    communications = []
    for customer in customers:
        # Determine recipient
        if campaign.channel == CampaignChannel.EMAIL:
            if not customer.email:
                continue
            recipient = customer.email
        elif campaign.channel == CampaignChannel.SMS or campaign.channel == CampaignChannel.WHATSAPP:
            if not customer.phone:
                continue
            recipient = customer.phone
        else:
            recipient = customer.email or customer.phone
            if not recipient:
                continue
        
        # Personalise message
        content = personalise_message(campaign.message_content or "", customer)
        subject = personalise_message(campaign.subject or "", customer) if campaign.subject else None
        
        # Generate external ID
        external_id = f"comm-{campaign.id}-{customer.id}-{datetime.utcnow().timestamp()}"
        
        comm = Communication(
            brand_id=current_user.brand_id,
            campaign_id=campaign.id,
            customer_id=customer.id,
            channel=campaign.channel.value,
            recipient=recipient,
            subject=subject,
            content=content,
            external_id=external_id,
            status=CommunicationStatus.QUEUED
        )
        db.add(comm)
        communications.append(comm)
    
    db.commit()
    
    # Update campaign stats
    campaign.sent_count = len(communications)
    db.commit()
    
    # Send to channel service in background (pass IDs to avoid detached objects)
    communication_ids = [comm.id for comm in communications]
    background_tasks.add_task(send_to_channel_service, communication_ids, campaign.id, current_user.brand_id)
    
    return {
        "message": "Campaign sending started",
        "campaign_id": campaign.id,
        "total_recipients": len(communications)
    }


@router.get("/{campaign_id}/stats")
def get_campaign_stats(
    campaign_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    campaign = db.query(Campaign).filter(
        Campaign.id == campaign_id,
        Campaign.brand_id == current_user.brand_id
    ).first()
    
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    sent = campaign.sent_count or 0
    delivered = campaign.delivered_count or 0
    opened = campaign.opened_count or 0
    clicked = campaign.clicked_count or 0
    converted = campaign.converted_count or 0
    failed = campaign.failed_count or 0
    
    return CampaignStats(
        campaign_id=campaign.id,
        sent_count=sent,
        delivered_count=delivered,
        delivered_rate=delivered / sent if sent > 0 else 0,
        opened_count=opened,
        opened_rate=opened / delivered if delivered > 0 else 0,
        clicked_count=clicked,
        clicked_rate=clicked / opened if opened > 0 else 0,
        converted_count=converted,
        converted_rate=converted / clicked if clicked > 0 else 0,
        failed_count=failed,
        failed_rate=failed / sent if sent > 0 else 0,
        revenue=campaign.revenue or 0
    )


# Templates
@router.get("/templates", tags=["Templates"])
def list_templates(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(CampaignTemplate).filter(CampaignTemplate.brand_id == current_user.brand_id)
    total = query.count()
    templates = query.order_by(CampaignTemplate.created_at.desc()).offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "data": [CampaignTemplateResponse.model_validate(t) for t in templates]
    }


@router.post("/templates", tags=["Templates"])
def create_template(
    template_data: CampaignTemplateCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    template = CampaignTemplate(
        brand_id=current_user.brand_id,
        **template_data.model_dump()
    )
    db.add(template)
    db.commit()
    db.refresh(template)
    return CampaignTemplateResponse.model_validate(template)
"""
Campaign Service - Business logic for campaign operations

Per CLAUDE.md responsibilities:
- Campaign Creation
- Campaign Launch
- Message Personalization
- Communication Creation
- Channel Dispatch

Campaign Creation Flow:
    Create Campaign → Store Campaign → Draft State

Campaign Launch Flow:
    Load Segment → Load Customers → Personalize Message → Create Communications → Send Jobs → Status = Running
"""

from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime
import json
import httpx
import uuid

from app.models.campaign import Campaign, CampaignStatus, CampaignChannel
from app.models.segment import Segment
from app.models.customer import Customer
from app.models.communication import Communication, CommunicationStatus
from app.schemas.campaign import CampaignCreate, CampaignUpdate
from app.core.config import settings
from app.services.segmentation import SegmentationService


class CampaignService:
    
    # Personalisation tokens
    PERSONALISATION_TOKENS = {
        "{name}": "first_name",
        "{first_name}": "first_name",
        "{last_name}": "last_name",
        "{email}": "email",
        "{phone}": "phone",
        "{city}": "city",
        "{state}": "state",
    }
    
    @staticmethod
    def create_campaign(
        db: Session,
        brand_id: int,
        campaign_data: CampaignCreate,
        created_by: Optional[int] = None
    ) -> Campaign:
        """
        Create a new campaign in DRAFT state
        
        Per CLAUDE.md: Campaign Creation Flow starts with Draft State
        """
        campaign = Campaign(
            brand_id=brand_id,
            name=campaign_data.name,
            subject=campaign_data.subject,
            channel=campaign_data.channel,
            status=CampaignStatus.DRAFT,
            message_content=campaign_data.message_content,
            personalisation_tokens=campaign_data.personalisation_tokens,
            segment_id=campaign_data.segment_id,
            scheduled_at=campaign_data.scheduled_at,
            created_by=created_by,
        )
        db.add(campaign)
        db.flush()
        
        # Calculate target count if segment is specified
        if campaign_data.segment_id:
            segment = db.query(Segment).filter(Segment.id == campaign_data.segment_id).first()
            if segment:
                campaign.target_count = segment.customer_count
        
        db.commit()
        db.refresh(campaign)
        return campaign
    
    @staticmethod
    def update_campaign(
        db: Session,
        campaign_id: int,
        campaign_data: CampaignUpdate
    ) -> Optional[Campaign]:
        """Update a campaign"""
        campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
        if not campaign:
            return None
        
        update_data = campaign_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(campaign, field, value)
        
        # Update target count if segment changed
        if campaign_data.segment_id is not None:
            if campaign_data.segment_id:
                segment = db.query(Segment).filter(Segment.id == campaign_data.segment_id).first()
                campaign.target_count = segment.customer_count if segment else 0
            else:
                campaign.target_count = 0
        
        campaign.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(campaign)
        return campaign
    
    @staticmethod
    def get_campaign(db: Session, campaign_id: int) -> Optional[Campaign]:
        """Get campaign by ID"""
        return db.query(Campaign).filter(Campaign.id == campaign_id).first()
    
    @staticmethod
    def list_campaigns(
        db: Session,
        brand_id: int,
        status: Optional[CampaignStatus] = None,
        channel: Optional[CampaignChannel] = None,
        skip: int = 0,
        limit: int = 50
    ) -> Tuple[List[Campaign], int]:
        """
        List campaigns with filters
        
        Returns: (campaigns, total_count)
        """
        query = db.query(Campaign).filter(Campaign.brand_id == brand_id)
        
        if status:
            query = query.filter(Campaign.status == status)
        if channel:
            query = query.filter(Campaign.channel == channel)
        
        total = query.count()
        campaigns = query.order_by(Campaign.created_at.desc()).offset(skip).limit(limit).all()
        return campaigns, total
    
    @staticmethod
    def personalise_message(template: str, customer: Customer) -> str:
        """
        Replace personalisation tokens with customer data
        
        Per CLAUDE.md:
        Support placeholders: {name}, {city}, {ltv}
        
        Example:
        "Hi {name}, We noticed customers in {city} are loving our new collection."
        becomes:
        "Hi Rahul, We noticed customers in Mumbai are loving our new collection."
        """
        result = template
        
        for token, field in CampaignService.PERSONALISATION_TOKENS.items():
            value = getattr(customer, field, None) or ""
            result = result.replace(token, str(value))
        
        return result
    
    @staticmethod
    def prepare_campaign_send(
        db: Session,
        campaign_id: int
    ) -> Tuple[Campaign, List[Customer], List[Dict]]:
        """
        Prepare campaign send - load segment customers and create communication data
        
        Per CLAUDE.md: Campaign Launch Flow steps 1-4
        
        Returns: (campaign, customers, communication_data_list)
        """
        campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
        if not campaign:
            raise ValueError(f"Campaign {campaign_id} not found")
        
        # Load segment customers
        if campaign.segment_id:
            customers = SegmentationService.evaluate_segment(db, campaign.segment_id)
        else:
            # No segment - should not happen in normal flow
            customers = []
        
        # Filter out unsubscribed customers
        customers = [c for c in customers if not c.is_unsubscribed]
        
        # Prepare communication data
        communications = []
        for customer in customers:
            # Determine recipient based on channel
            if campaign.channel == CampaignChannel.EMAIL:
                recipient = customer.email
            elif campaign.channel in [CampaignChannel.SMS, CampaignChannel.WHATSAPP]:
                recipient = customer.phone
            else:
                recipient = customer.email or customer.phone
            
            if not recipient:
                continue
            
            # Personalise message
            content = CampaignService.personalise_message(
                campaign.message_content or "", 
                customer
            )
            
            communications.append({
                "customer": customer,
                "recipient": recipient,
                "content": content,
                "subject": campaign.subject,
            })
        
        return campaign, customers, communications
    
    @staticmethod
    def create_communications(
        db: Session,
        campaign_id: int,
        communications_data: List[Dict]
    ) -> int:
        """
        Create communication records for a campaign
        
        Per CLAUDE.md: One customer = one communication row
        
        Returns: count of communications created
        """
        campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
        if not campaign:
            return 0
        
        count = 0
        for comm_data in communications_data:
            customer = comm_data["customer"]
            
            communication = Communication(
                brand_id=campaign.brand_id,
                campaign_id=campaign_id,
                customer_id=customer.id,
                channel=campaign.channel.value if hasattr(campaign.channel, 'value') else campaign.channel,
                status=CommunicationStatus.QUEUED,
                recipient=comm_data["recipient"],
                subject=comm_data.get("subject"),
                content=comm_data["content"],
                external_id=f"comm-{uuid.uuid4().hex[:12]}",
            )
            db.add(communication)
            count += 1
        
        db.flush()
        return count
    
    @staticmethod
    async def dispatch_to_channel_service(
        db: Session,
        campaign_id: int
    ) -> Dict[str, Any]:
        """
        Send communications to channel service
        
        Per CLAUDE.md:
        - Campaign Service never simulates delivery
        - Campaign Service only calls POST /send on Channel Service
        
        Returns: result with success count and failed count
        """
        campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
        if not campaign:
            return {"success": 0, "failed": 0, "error": "Campaign not found"}
        
        # Get queued communications
        communications = db.query(Communication).filter(
            Communication.campaign_id == campaign_id,
            Communication.status == CommunicationStatus.QUEUED
        ).all()
        
        if not communications:
            return {"success": 0, "failed": 0, "error": "No queued communications"}
        
        success_count = 0
        failed_count = 0
        
        async with httpx.AsyncClient() as client:
            for comm in communications:
                try:
                    response = await client.post(
                        f"{settings.CHANNEL_SERVICE_URL}/send",
                        json={
                            "communication_id": comm.external_id,
                            "campaign_id": str(campaign_id),
                            "customer_id": str(comm.customer_id),
                            "channel": comm.channel,
                            "message": comm.content,
                            "callback_url": f"{settings.CRM_CALLBACK_URL}/{comm.external_id}"
                        },
                        headers={"x-api-key": settings.CHANNEL_SERVICE_API_KEY},
                        timeout=30.0
                    )
                    
                    if response.status_code == 202:
                        comm.status = CommunicationStatus.SENT
                        comm.sent_at = datetime.utcnow()
                        success_count += 1
                    else:
                        comm.status = CommunicationStatus.FAILED
                        failed_count += 1
                        
                except Exception as e:
                    comm.status = CommunicationStatus.FAILED
                    failed_count += 1
        
        db.commit()
        
        # Update campaign stats
        campaign.sent_count = success_count
        if success_count > 0:
            campaign.status = CampaignStatus.SENDING
        
        db.commit()
        
        return {
            "success": success_count,
            "failed": failed_count,
            "total": len(communications)
        }
    
    @staticmethod
    def launch_campaign(db: Session, campaign_id: int) -> Campaign:
        """
        Full campaign launch flow
        
        Per CLAUDE.md: Campaign Launch Flow
        """
        campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
        if not campaign:
            raise ValueError(f"Campaign {campaign_id} not found")
        
        if campaign.status not in [CampaignStatus.DRAFT, CampaignStatus.SCHEDULED]:
            raise ValueError(f"Campaign {campaign_id} cannot be launched from status {campaign.status}")
        
        # Prepare and create communications
        _, customers, comms_data = CampaignService.prepare_campaign_send(db, campaign_id)
        
        if not comms_data:
            raise ValueError("No customers to send to")
        
        count = CampaignService.create_communications(db, campaign_id, comms_data)
        
        # Update campaign
        campaign.target_count = count
        campaign.status = CampaignStatus.SENDING
        campaign.sent_at = datetime.utcnow()
        
        db.commit()
        db.refresh(campaign)
        
        return campaign
    
    @staticmethod
    def pause_campaign(db: Session, campaign_id: int) -> Optional[Campaign]:
        """Pause a running campaign"""
        campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
        if not campaign:
            return None
        
        if campaign.status == CampaignStatus.SENDING:
            campaign.status = CampaignStatus.DRAFT
            db.commit()
            db.refresh(campaign)
        
        return campaign
    
    @staticmethod
    def cancel_campaign(db: Session, campaign_id: int) -> Optional[Campaign]:
        """Cancel a campaign"""
        campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
        if not campaign:
            return None
        
        campaign.status = CampaignStatus.CANCELLED
        db.commit()
        db.refresh(campaign)
        
        return campaign
    
    @staticmethod
    def get_campaign_analytics(db: Session, campaign_id: int) -> Dict[str, Any]:
        """
        Get detailed campaign analytics
        
        Per CLAUDE.md: Campaign Statistics
        """
        campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
        if not campaign:
            return {}
        
        # Get communication stats
        total = db.query(Communication).filter(
            Communication.campaign_id == campaign_id
        ).count()
        
        sent = db.query(Communication).filter(
            Communication.campaign_id == campaign_id,
            Communication.status.in_([CommunicationStatus.SENT, CommunicationStatus.DELIVERED])
        ).count()
        
        delivered = db.query(Communication).filter(
            Communication.campaign_id == campaign_id,
            Communication.status == CommunicationStatus.DELIVERED
        ).count()
        
        opened = db.query(Communication).filter(
            Communication.campaign_id == campaign_id,
            Communication.opened_at.isnot(None)
        ).count()
        
        clicked = db.query(Communication).filter(
            Communication.campaign_id == campaign_id,
            Communication.clicked_at.isnot(None)
        ).count()
        
        failed = db.query(Communication).filter(
            Communication.campaign_id == campaign_id,
            Communication.status == CommunicationStatus.FAILED
        ).count()
        
        # Calculate rates
        def calc_rate(part, whole):
            return (part / whole * 100) if whole > 0 else 0
        
        return {
            "campaign_id": campaign_id,
            "campaign_name": campaign.name,
            "status": campaign.status.value if hasattr(campaign.status, 'value') else campaign.status,
            "channel": campaign.channel.value if hasattr(campaign.channel, 'value') else campaign.channel,
            "target_count": campaign.target_count,
            "sent_count": sent,
            "delivered_count": delivered,
            "delivered_rate": calc_rate(delivered, sent),
            "opened_count": opened,
            "opened_rate": calc_rate(opened, delivered),
            "clicked_count": clicked,
            "clicked_rate": calc_rate(clicked, delivered),
            "failed_count": failed,
            "failed_rate": calc_rate(failed, sent),
            "revenue": campaign.revenue,
        }
    
    @staticmethod
    def calculate_campaign_roi(db: Session, campaign_id: int) -> Dict[str, float]:
        """
        Calculate campaign ROI based on attributed revenue
        
        Per CLAUDE.md: Revenue Attribution
        """
        campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
        if not campaign:
            return {}
        
        # Get attributed orders
        from app.models.order import Order
        attributed_revenue = db.query(func.sum(Order.total)).filter(
            Order.campaign_id == campaign_id,
            Order.status == "completed"
        ).scalar() or 0
        
        # Calculate costs (simplified - could be enhanced with actual cost data)
        cost_per_message = 0.5  # Example cost
        total_cost = campaign.sent_count * cost_per_message
        
        roi = ((float(attributed_revenue) - total_cost) / total_cost * 100) if total_cost > 0 else 0
        
        return {
            "attributed_revenue": float(attributed_revenue),
            "campaign_cost": total_cost,
            "roi_percentage": roi,
            "net_revenue": float(attributed_revenue) - total_cost,
        }
    
    @staticmethod
    def get_campaigns_summary(db: Session, brand_id: int) -> Dict[str, Any]:
        """Get summary of all campaigns for a brand"""
        total = db.query(Campaign).filter(Campaign.brand_id == brand_id).count()
        
        by_status = {}
        for status in CampaignStatus:
            count = db.query(Campaign).filter(
                Campaign.brand_id == brand_id,
                Campaign.status == status
            ).count()
            by_status[status.value] = count
        
        total_sent = db.query(func.sum(Campaign.sent_count)).filter(
            Campaign.brand_id == brand_id
        ).scalar() or 0
        
        total_revenue = db.query(func.sum(Campaign.revenue)).filter(
            Campaign.brand_id == brand_id
        ).scalar() or 0
        
        return {
            "total_campaigns": total,
            "by_status": by_status,
            "total_messages_sent": total_sent,
            "total_attributed_revenue": float(total_revenue),
        }
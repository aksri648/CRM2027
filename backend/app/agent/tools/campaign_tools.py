"""
Campaign Tools for Agent

Per CLAUDE.md: Tools for campaign operations
"""

from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session

from app.services.campaign_service import CampaignService
from app.models.campaign import Campaign, CampaignStatus, CampaignChannel
from app.schemas.campaign import CampaignCreate


class CampaignTools:
    """Tools for campaign operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_campaign(
        self,
        brand_id: int,
        name: str,
        segment_id: Optional[int] = None,
        channel: str = "email",
        message_content: str = "",
        subject: str = ""
    ) -> Dict[str, Any]:
        """
        Create a new campaign
        """
        campaign_data = CampaignCreate(
            name=name,
            subject=subject,
            channel=CampaignChannel(channel) if hasattr(CampaignChannel, channel.upper()) else CampaignChannel.EMAIL,
            message_content=message_content,
            segment_id=segment_id,
        )
        
        campaign = CampaignService.create_campaign(self.db, brand_id, campaign_data)
        
        return {
            "id": campaign.id,
            "name": campaign.name,
            "channel": campaign.channel.value if hasattr(campaign.channel, 'value') else campaign.channel,
            "status": campaign.status.value if hasattr(campaign.status, 'value') else campaign.status,
            "segment_id": campaign.segment_id,
            "target_count": campaign.target_count,
        }
    
    def get_campaign_status(self, campaign_id: int) -> Dict[str, Any]:
        """
        Get campaign details and metrics
        """
        return CampaignService.get_campaign_analytics(self.db, campaign_id)
    
    def list_campaigns(
        self,
        brand_id: int,
        status: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        List campaigns for brand
        """
        status_enum = CampaignStatus(status) if status else None
        campaigns, _ = CampaignService.list_campaigns(
            self.db,
            brand_id=brand_id,
            status=status_enum,
            limit=limit
        )
        
        return [
            {
                "id": c.id,
                "name": c.name,
                "channel": c.channel.value if hasattr(c.channel, 'value') else c.channel,
                "status": c.status.value if hasattr(c.status, 'value') else c.status,
                "sent_count": c.sent_count,
                "delivered_count": c.delivered_count,
                "revenue": c.revenue,
            }
            for c in campaigns
        ]
    
    def launch_campaign(self, campaign_id: int) -> Dict[str, Any]:
        """
        Launch a campaign (creates communications and sends to channel service)
        """
        try:
            campaign = CampaignService.launch_campaign(self.db, campaign_id)
            return {
                "success": True,
                "campaign_id": campaign.id,
                "status": campaign.status.value if hasattr(campaign.status, 'value') else campaign.status,
                "target_count": campaign.target_count,
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }
    
    def pause_campaign(self, campaign_id: int) -> Dict[str, Any]:
        """
        Pause a running campaign
        """
        campaign = CampaignService.pause_campaign(self.db, campaign_id)
        if not campaign:
            return {"error": f"Campaign {campaign_id} not found"}
        
        return {
            "campaign_id": campaign.id,
            "status": campaign.status.value if hasattr(campaign.status, 'value') else campaign.status,
        }
    
    def get_campaign_roi(self, campaign_id: int) -> Dict[str, Any]:
        """
        Get campaign ROI metrics
        """
        return CampaignService.calculate_campaign_roi(self.db, campaign_id)
    
    def get_campaigns_summary(self, brand_id: int) -> Dict[str, Any]:
        """
        Get summary of all campaigns
        """
        return CampaignService.get_campaigns_summary(self.db, brand_id)
    
    def personalise_message(self, template: str, customer_data: Dict[str, Any]) -> str:
        """
        Personalise a message template with customer data
        """
        from app.models.customer import Customer
        
        # Create a mock customer object for personalisation
        customer = Customer(
            first_name=customer_data.get("first_name"),
            last_name=customer_data.get("last_name"),
            email=customer_data.get("email"),
            phone=customer_data.get("phone"),
            city=customer_data.get("city"),
        )
        
        return CampaignService.personalise_message(template, customer)
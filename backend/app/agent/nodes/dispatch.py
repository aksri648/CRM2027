"""
Dispatch Node

Per CLAUDE.md:
- Execute approved campaigns
- This node must NEVER make decisions
- Responsibilities: Create Campaign, Create Communications, Send To Channel Service, Mark Campaign Running
"""

from typing import Dict, Any
from sqlalchemy.orm import Session
import json

from app.agent.state import AgentState
from app.services.campaign_service import CampaignService
from app.agent.tools.segment_tools import SegmentTools


class DispatchNode:
    """
    Executes approved campaigns (never makes decisions)
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.campaign_service = CampaignService()
        self.segment_tools = SegmentTools(db)
    
    async def dispatch(self, state: AgentState) -> AgentState:
        """
        Execute the approved campaign
        
        Per CLAUDE.md: Human must approve before dispatch
        """
        campaign_proposal = state.get("pending_campaign")
        
        if not campaign_proposal:
            state["error"] = "No approved campaign to dispatch"
            return state
        
        brand_id = state["brand_id"]
        
        try:
            # 1. Create segment if needed
            segment_data = campaign_proposal.get("segment", {})
            segment_id = None
            
            if segment_data and segment_data.get("rules"):
                segment_result = self.segment_tools.create_segment(
                    brand_id=brand_id,
                    name=segment_data.get("name", "AI Generated Segment"),
                    rules=segment_data.get("rules", []),
                    description=segment_data.get("reasoning", "")
                )
                segment_id = segment_result.get("id")
            
            # 2. Create campaign
            messages = campaign_proposal.get("messages", {})
            channel = campaign_proposal.get("channel", "email")
            
            # Get email content (default to first email variant)
            email_content = ""
            if "email" in messages and len(messages["email"]) > 0:
                email_body = messages["email"][0].get("body", "")
                email_subject = messages["email"][0].get("subject", "")
                email_content = f"Subject: {email_subject}\n\n{email_body}"
            else:
                # Use any available message
                for ch, variants in messages.items():
                    if variants:
                        email_content = variants[0] if isinstance(variants[0], str) else variants[0].get("body", "")
                        break
            
            campaign = self.campaign_service.create_campaign(
                db=self.db,
                brand_id=brand_id,
                campaign_data={
                    "name": campaign_proposal.get("name", "AI Campaign"),
                    "channel": channel,
                    "message_content": email_content,
                    "segment_id": segment_id,
                }
            )
            
            # 3. Launch campaign (creates communications and sends to channel service)
            launch_result = self.campaign_service.launch_campaign(self.db, campaign.id)
            
            state["results"] = {
                "success": True,
                "campaign_id": campaign.id,
                "campaign_name": campaign.name,
                "status": "launched",
                "target_count": campaign.target_count,
                "message": f"Campaign '{campaign.name}' launched successfully"
            }
            state["current_step"] = "complete"
            
        except Exception as e:
            state["error"] = f"Dispatch failed: {str(e)}"
            state["results"] = {
                "success": False,
                "error": str(e)
            }
        
        return state
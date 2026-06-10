"""
Data Fetch Node

Per CLAUDE.md:
- Collect CRM context
- Fetch: Customer Stats, Segment Data, Campaign Data, Analytics Data, Opportunity Data
"""

from typing import Dict, Any
from sqlalchemy.orm import Session

from app.agent.state import AgentState
from app.agent.tools.customer_tools import CustomerTools
from app.agent.tools.segment_tools import SegmentTools
from app.agent.tools.campaign_tools import CampaignTools
from app.agent.tools.analytics_tools import AnalyticsTools


class DataFetcher:
    """
    Fetches relevant CRM context based on intent
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.customer_tools = CustomerTools(db)
        self.segment_tools = SegmentTools(db)
        self.campaign_tools = CampaignTools(db)
        self.analytics_tools = AnalyticsTools(db)
    
    async def fetch(self, state: AgentState) -> AgentState:
        """
        Fetch CRM context based on classified intent
        """
        brand_id = state["brand_id"]
        intent = state["intent"]
        
        context = {
            "brand_id": brand_id,
            "intent": intent,
        }
        
        # Always fetch basic brand stats
        context["brand_stats"] = self.customer_tools.get_brand_customer_stats(brand_id)
        
        # Fetch additional context based on intent
        if intent in ["segment_request", "campaign_request"]:
            # Segments are relevant for both
            context["segments"] = self.segment_tools.list_segments(brand_id)
            context["customer_distribution"] = self.customer_tools.get_customer_distribution(brand_id)
        
        if intent == "campaign_request":
            # Campaigns for campaign requests
            context["campaigns"] = self.campaign_tools.list_campaigns(brand_id, limit=10)
            context["campaigns_summary"] = self.campaign_tools.get_campaigns_summary(brand_id)
        
        if intent == "analytics_request":
            # Analytics data
            context["overview"] = self.analytics_tools.get_overview(brand_id)
            context["channel_performance"] = self.analytics_tools.get_channel_performance(brand_id)
            context["top_segments"] = self.analytics_tools.get_top_segments(brand_id)
        
        if intent == "opportunity_request":
            # Opportunity-related data
            context["segments"] = self.segment_tools.list_segments(brand_id)
            context["campaigns_summary"] = self.campaign_tools.get_campaigns_summary(brand_id)
        
        state["context"] = context
        state["current_step"] = "data_fetched"
        
        return state
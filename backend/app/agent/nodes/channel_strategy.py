"""
Channel Strategy Node

Per CLAUDE.md:
- Recommend best communication channel
- Options: WhatsApp, SMS, Email, RCS
"""

from typing import Dict, Any
import json
from sqlalchemy.orm import Session

from app.agent.state import AgentState
from app.services.ai_service import AIService


class ChannelStrategist:
    """
    Recommends the best channel for a campaign
    """
    
    SYSTEM_PROMPT = """You are a Customer Engagement Strategist.

Choose the best communication channel.

Consider:
- urgency
- customer behavior
- engagement patterns
- campaign objective

Return:

{
  "recommended_channel": "whatsapp",
  "confidence": 0.85,
  "reasoning": "Why this channel is best"
}

Never write copy.
Never create segments.
Never launch campaigns."""
    
    def __init__(self, db: Session):
        self.db = db
        self.ai_service = AIService()
    
    async def recommend(self, state: AgentState) -> AgentState:
        """
        Recommend channel based on context
        """
        segment = state.get("pending_segment", {})
        messages = state.get("pending_messages", {})
        context = state.get("context", {})
        
        try:
            # Build context for AI
            customer_dist = context.get("customer_distribution", {})
            segment_name = segment.get("name", "Target Audience")
            
            # Get channel preferences from customer data
            email_pct = 0
            phone_pct = 0
            total = customer_dist.get("total_customers", 0)
            if total > 0:
                email_pct = customer_dist.get("customers_with_email", 0) / total * 100
                phone_pct = customer_dist.get("customers_with_phone", 0) / total * 100
            
            prompt = f"""Recommend the best channel for this campaign.

Target audience: {segment_name}
Customers with email: {email_pct:.0f}%
Customers with phone: {phone_pct:.0f}%

Campaign messages prepared for: {list(messages.keys())}"""
            
            response = self.ai_service.chat(
                message=prompt,
                context={"system_prompt": self.SYSTEM_PROMPT}
            )
            
            # Parse JSON response
            try:
                result = json.loads(response)
            except:
                # Fallback recommendation
                result = self._fallback_recommendation(email_pct, phone_pct)
            
            state["channel_recommendation"] = result
            state["current_step"] = "channel_recommended"
            
        except Exception as e:
            state["error"] = f"Channel recommendation failed: {str(e)}"
        
        return state
    
    def _fallback_recommendation(self, email_pct: float, phone_pct: float) -> Dict[str, Any]:
        """
        Fallback channel recommendation based on customer contactability
        """
        if phone_pct > email_pct:
            return {
                "recommended_channel": "whatsapp",
                "confidence": 0.7,
                "reasoning": "Higher percentage of customers have phone numbers"
            }
        else:
            return {
                "recommended_channel": "email",
                "confidence": 0.7,
                "reasoning": "Higher percentage of customers have email addresses"
            }
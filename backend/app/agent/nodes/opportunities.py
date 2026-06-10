"""
Opportunity Finder Node

Per CLAUDE.md:
- Find revenue opportunities
- Output: {title, expected_revenue, confidence, reasoning}
"""

from typing import Dict, Any, List
import json
from sqlalchemy.orm import Session

from app.agent.state import AgentState
from app.services.ai_service import AIService
from app.services.opportunity_service import OpportunityService


class OpportunityFinder:
    """
    Discovers revenue opportunities using AI analysis
    """
    
    SYSTEM_PROMPT = """You are a Revenue Opportunity Analyst.

Your objective is discovering growth opportunities.

Search for:
- churn risk
- VIP retention
- cross-sell opportunities
- upsell opportunities
- inactive high-value customers

Every opportunity must include:
- title
- expected_revenue
- confidence
- reasoning

Output JSON only.

Format:
{
  "opportunities": [
    {
      "title": "Opportunity name",
      "description": "What it is",
      "expected_revenue": 10000,
      "confidence": 0.8,
      "reasoning": "Why this matters"
    }
  ]
}

Never generate messages.
Never launch campaigns."""
    
    def __init__(self, db: Session):
        self.db = db
        self.ai_service = AIService()
        self.opportunity_service = OpportunityService()
    
    async def find(self, state: AgentState) -> AgentState:
        """
        Find revenue opportunities
        """
        brand_id = state["brand_id"]
        context = state.get("context", {})
        
        try:
            # Get brand stats
            brand_stats = context.get("brand_stats", {})
            campaigns_summary = context.get("campaigns_summary", {})
            
            prompt = f"""Analyze this brand for revenue opportunities.

Brand stats:
- Total customers: {brand_stats.get('total_customers', 0)}
- Total revenue: ₹{brand_stats.get('total_revenue', 0)}
- Average LTV: ₹{brand_stats.get('average_ltv', 0)}

Campaign performance:
- Total campaigns: {campaigns_summary.get('total_campaigns', 0)}
- Total messages sent: {campaigns_summary.get('total_messages_sent', 0)}

Identify top 3 revenue opportunities."""
            
            response = self.ai_service.chat(
                message=prompt,
                context={"system_prompt": self.SYSTEM_PROMPT}
            )
            
            # Parse JSON response
            try:
                result = json.loads(response)
                opportunities = result.get("opportunities", [])
            except:
                # Fallback: use rule-based detection
                opportunities = self._fallback_opportunities(brand_stats)
            
            state["opportunities"] = opportunities
            state["current_step"] = "opportunities_found"
            
        except Exception as e:
            state["error"] = f"Opportunity finding failed: {str(e)}"
        
        return state
    
    def _fallback_opportunities(self, brand_stats: Dict) -> List[Dict]:
        """
        Fallback opportunity detection using rules
        """
        total_customers = brand_stats.get("total_customers", 0)
        avg_ltv = brand_stats.get("average_ltv", 0)
        
        opportunities = []
        
        # VIP retention opportunity
        if total_customers > 100:
            opportunities.append({
                "title": "VIP Customer Retention",
                "description": "High-value customers showing engagement decline",
                "expected_revenue": total_customers * 0.1 * avg_ltv,
                "confidence": 0.7,
                "reasoning": "Retaining high-value customers is more cost-effective than acquisition"
            })
        
        # Reactivation opportunity
        if total_customers > 50:
            opportunities.append({
                "title": "Lapsed Customer Reactivation",
                "description": "Customers who haven't purchased in 60+ days",
                "expected_revenue": total_customers * 0.2 * avg_ltv * 0.3,
                "confidence": 0.6,
                "reasoning": "Win-back campaigns typically achieve 10-20% conversion"
            })
        
        return opportunities
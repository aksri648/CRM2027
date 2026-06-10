"""
Insight Generator Node

Per CLAUDE.md:
- Convert analytics into recommendations
- Output: {findings: [], recommendations: [], next_actions: []}
"""

from typing import Dict, Any, List
import json
from sqlalchemy.orm import Session

from app.agent.state import AgentState
from app.services.ai_service import AIService


class InsightGenerator:
    """
    Generates actionable insights from analytics data
    """
    
    SYSTEM_PROMPT = """You are a Marketing Intelligence Analyst.

Your responsibility is converting raw metrics into actionable insights.

Analyze:
- Open Rate
- Click Rate
- Conversion Rate
- Revenue
- Channel Performance

Generate:
1. Key Findings
2. Explanations
3. Recommendations
4. Next Best Actions

Avoid generic observations.
Be specific.

Output JSON only.

Format:
{
  "findings": [
    {"metric": "open rate", "value": "25%", "insight": "what this means"}
  ],
  "recommendations": [
    "specific recommendation 1",
    "specific recommendation 2"
  ],
  "next_actions": [
    "action 1",
    "action 2"
  ]
}"""
    
    def __init__(self, db: Session):
        self.db = db
        self.ai_service = AIService()
    
    async def generate(self, state: AgentState) -> AgentState:
        """
        Generate insights from analytics
        """
        context = state.get("context", {})
        
        try:
            # Get analytics data
            overview = context.get("overview", {})
            channel_perf = context.get("channel_performance", [])
            top_segments = context.get("top_segments", [])
            
            # Build analytics summary
            analytics_summary = f"""
Overview:
- Total customers: {overview.get('total_customers', 0)}
- Active campaigns: {overview.get('active_campaigns', 0)}
- Messages sent: {overview.get('messages_sent', 0)}
- Revenue: ₹{overview.get('revenue_attributed', 0)}

Channel Performance:
{json.dumps(channel_perf, indent=2)}

Top Segments:
{json.dumps(top_segments[:3], indent=2)}
"""
            
            prompt = f"""Analyze this analytics data and provide insights:

{analytics_summary}"""
            
            response = self.ai_service.chat(
                message=prompt,
                context={"system_prompt": self.SYSTEM_PROMPT}
            )
            
            # Parse JSON response
            try:
                result = json.loads(response)
            except:
                # Fallback insights
                result = self._fallback_insights(overview, channel_perf)
            
            state["insights"] = result
            state["current_step"] = "insights_generated"
            
        except Exception as e:
            state["error"] = f"Insight generation failed: {str(e)}"
        
        return state
    
    def _fallback_insights(self, overview: Dict, channel_perf: List) -> Dict[str, List]:
        """
        Fallback insight generation
        """
        insights = {
            "findings": [],
            "recommendations": [],
            "next_actions": []
        }
        
        # Add basic findings
        if overview.get("messages_sent", 0) > 0:
            insights["findings"].append({
                "metric": "Message Volume",
                "value": str(overview.get("messages_sent", 0)),
                "insight": "Campaign messaging is active"
            })
        
        if overview.get("revenue_attributed", 0) > 0:
            insights["findings"].append({
                "metric": "Revenue",
                "value": f"₹{overview.get('revenue_attributed', 0):.2f}",
                "insight": "Campaigns are generating revenue"
            })
        
        # Channel recommendations
        if channel_perf:
            best_channel = max(channel_perf, key=lambda x: x.get("open_rate", 0))
            insights["recommendations"].append(
                f"Focus on {best_channel.get('channel', 'email')} - highest open rate"
            )
        
        insights["next_actions"].append("Review underperforming campaigns")
        insights["next_actions"].append("Test new message variants")
        
        return insights
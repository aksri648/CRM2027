"""
Segment Generator Node

Per CLAUDE.md:
- Create audiences from natural language
- Output: {segment_name, reasoning, filter_rules, expected_size}
"""

from typing import Dict, Any, List
import json
from sqlalchemy.orm import Session

from app.agent.state import AgentState
from app.agent.tools.segment_tools import SegmentTools
from app.services.ai_service import AIService


class SegmentGenerator:
    """
    Generates segment definitions from user goals
    """
    
    SYSTEM_PROMPT = """You are a Senior CRM Audience Strategist.

Your responsibility is selecting the best audience.

You think like a lifecycle marketer.

You consider:
- Recency
- Frequency
- Monetary Value
- Lifecycle Stage
- Category Affinity

You must generate:
- segment_name
- reasoning
- filter_rules
- expected_size

You never write copy.
You never recommend channels.
You never launch campaigns.

Output JSON only.

Format:
{
  "segment_name": "Name of segment",
  "reasoning": "Why this segment is valuable",
  "filter_rules": [
    {"field": "field_name", "operator": "operator", "value": "value"}
  ],
  "expected_size": 1000
}

Supported fields:
- total_orders, total_spent, average_order_value, days_since_last_order (order-based)
- email, phone, city, state, country, gender, engagement_score, is_unsubscribed (customer-based)

Supported operators:
- equals, not_equals, greater_than, less_than, contains, in, is_null, is_not_null"""
    
    def __init__(self, db: Session):
        self.db = db
        self.segment_tools = SegmentTools(db)
        self.ai_service = AIService()
    
    async def generate(self, state: AgentState) -> AgentState:
        """
        Generate segment based on user request
        """
        # Get the user message
        latest_message = ""
        for msg in reversed(state["messages"]):
            if msg["role"] == "user":
                latest_message = msg["content"]
                break
        
        if not latest_message:
            state["error"] = "No user message found"
            return state
        
        brand_id = state["brand_id"]
        context = state.get("context", {})
        
        try:
            # Build context for AI
            customer_data = context.get("brand_stats", {})
            segments = context.get("segments", [])
            
            prompt = f"""Based on this marketing goal: {latest_message}

Customer data summary:
- Total customers: {customer_data.get('total_customers', 0)}
- Average LTV: ₹{customer_data.get('average_ltv', 0)}
- Top cities: {[c[0] for c in customer_data.get('top_cities', [])[:5]]}

Existing segments: {[s['name'] for s in segments[:5]]}

Generate a segment definition."""
            
            response = self.ai_service.chat(
                message=prompt,
                context={"system_prompt": self.SYSTEM_PROMPT}
            )
            
            # Parse JSON response
            try:
                result = json.loads(response)
            except:
                # Fallback if JSON parsing fails
                result = self._fallback_segment(latest_message)
            
            # Preview the segment
            rules = result.get("filter_rules", [])
            preview = self.segment_tools.preview_segment(brand_id, rules, limit=10)
            
            segment_proposal = {
                "name": result.get("segment_name", "New Segment"),
                "reasoning": result.get("reasoning", ""),
                "rules": rules,
                "expected_size": preview["customer_count"],
                "sample_customers": preview["sample_customers"],
            }
            
            state["pending_segment"] = segment_proposal
            state["current_step"] = "segment_proposed"
            
        except Exception as e:
            state["error"] = f"Segment generation failed: {str(e)}"
        
        return state
    
    def _fallback_segment(self, message: str) -> Dict[str, Any]:
        """
        Fallback segment generation using keywords
        """
        message_lower = message.lower()
        
        # Detect "inactive" or "lapsed" customers
        if "inactive" in message_lower or "lapsed" in message_lower or "hasn't purchased" in message_lower:
            return {
                "segment_name": "Inactive Customers",
                "reasoning": "Customers who haven't purchased recently",
                "filter_rules": [
                    {"field": "days_since_last_order", "operator": "greater_than", "value": "60"}
                ],
                "expected_size": 1000
            }
        
        # Detect high-value customers
        if "high value" in message_lower or "vip" in message_lower or "premium" in message_lower:
            return {
                "segment_name": "High Value Customers",
                "reasoning": "Customers with high lifetime value",
                "filter_rules": [
                    {"field": "total_spent", "operator": "greater_than", "value": "5000"}
                ],
                "expected_size": 500
            }
        
        # Default segment
        return {
            "segment_name": "Active Customers",
            "reasoning": "Customers with recent activity",
            "filter_rules": [
                {"field": "engagement_score", "operator": "greater_than", "value": "50"}
            ],
            "expected_size": 1000
        }
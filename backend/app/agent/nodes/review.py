"""
Review Node

Per CLAUDE.md:
- Create final campaign proposal
- This is the final planning step before human approval
"""

from typing import Dict, Any
import json
from sqlalchemy.orm import Session

from app.agent.state import AgentState
from app.services.ai_service import AIService


class ReviewNode:
    """
    Creates the final campaign proposal for human review
    """
    
    SYSTEM_PROMPT = """You are a Campaign Director.

Your responsibility is creating final campaign proposals.

Combine:
- audience
- messaging
- channel recommendation

Generate:
- campaign title
- audience summary
- expected outcome
- risk assessment

Do not launch campaigns.
Do not change strategy.
Summarize only.

Output JSON only.

Format:
{
  "campaign_name": "Name",
  "summary": "What this campaign is about",
  "audience_summary": "Who will receive it",
  "expected_outcome": "What we expect to achieve",
  "risks": "Potential risks or concerns"
}"""
    
    def __init__(self, db: Session):
        self.db = db
        self.ai_service = AIService()
    
    async def review(self, state: AgentState) -> AgentState:
        """
        Create final campaign proposal
        """
        segment = state.get("pending_segment", {})
        messages = state.get("pending_messages", {})
        channel_rec = state.get("channel_recommendation", {})
        context = state.get("context", {})
        
        try:
            # Get latest user message as campaign goal
            latest_message = ""
            for msg in reversed(state["messages"]):
                if msg["role"] == "user":
                    latest_message = msg["content"]
                    break
            
            prompt = f"""Create a campaign proposal summary.

Campaign goal: {latest_message}

Audience:
- Name: {segment.get('name', 'Target Audience')}
- Size: {segment.get('expected_size', 0)} customers
- Reasoning: {segment.get('reasoning', '')}

Channel: {channel_rec.get('recommended_channel', 'email')} (confidence: {channel_rec.get('confidence', 0)})

Messages prepared for: {list(messages.keys())}"""
            
            response = self.ai_service.chat(
                message=prompt,
                context={"system_prompt": self.SYSTEM_PROMPT}
            )
            
            # Parse JSON response
            try:
                result = json.loads(response)
            except:
                # Fallback proposal
                result = self._fallback_proposal(segment, channel_rec)
            
            # Create pending campaign
            campaign_proposal = {
                "name": result.get("campaign_name", "New Campaign"),
                "summary": result.get("summary", ""),
                "audience_summary": result.get("audience_summary", ""),
                "expected_outcome": result.get("expected_outcome", ""),
                "risks": result.get("risks", ""),
                "segment": segment,
                "messages": messages,
                "channel": channel_rec.get("recommended_channel", "email"),
                "confidence": channel_rec.get("confidence", 0.5),
            }
            
            state["pending_campaign"] = campaign_proposal
            state["current_step"] = "pending_approval"
            
        except Exception as e:
            state["error"] = f"Review failed: {str(e)}"
        
        return state
    
    def _fallback_proposal(self, segment: Dict, channel_rec: Dict) -> Dict[str, str]:
        """
        Fallback proposal generation
        """
        return {
            "campaign_name": f"Campaign for {segment.get('name', 'Target Audience')}",
            "summary": f"Target {segment.get('expected_size', 0)} customers via {channel_rec.get('recommended_channel', 'email')}",
            "audience_summary": segment.get('reasoning', 'Target audience segment'),
            "expected_outcome": "Engagement and conversions",
            "risks": "Monitor delivery rates and opt-out requests"
        }
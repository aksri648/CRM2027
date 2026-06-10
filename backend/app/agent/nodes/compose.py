"""
Message Composer Node

Per CLAUDE.md:
- Generate campaign copy for all channels
- Output: {whatsapp: [...], sms: [...], email: [...]}
"""

from typing import Dict, Any, List
import json
from sqlalchemy.orm import Session

from app.agent.state import AgentState
from app.services.ai_service import AIService


class MessageComposer:
    """
    Generates message variants for different channels
    """
    
    SYSTEM_PROMPT = """You are a Senior Lifecycle Marketing Copywriter.

Your objective is maximizing engagement.

Generate:
- WhatsApp messages
- SMS messages
- Email messages (subject + body)

Generate two variants per channel.

Messages should:
- feel human
- feel personalized
- avoid spam
- include CTA

Output JSON only.

Format:
{
  "whatsapp": ["message1 (under 160 chars)", "message2"],
  "sms": ["message1 (under 160 chars)", "message2"],
  "email": [
    {"subject": "subject line", "body": "email body"},
    {"subject": "subject line 2", "body": "email body 2"}
  ]
}

Never create segments.
Never recommend channels.
Never launch campaigns."""
    
    def __init__(self, db: Session):
        self.db = db
        self.ai_service = AIService()
    
    async def compose(self, state: AgentState) -> AgentState:
        """
        Generate message variants based on segment and goal
        """
        # Get user goal and segment info
        latest_message = ""
        for msg in reversed(state["messages"]):
            if msg["role"] == "user":
                latest_message = msg["content"]
                break
        
        segment = state.get("pending_segment", {})
        segment_name = segment.get("name", "Target Audience")
        expected_size = segment.get("expected_size", 0)
        
        try:
            prompt = f"""Generate message variants for a marketing campaign.

Campaign goal: {latest_message}
Target audience: {segment_name} ({expected_size} customers)

Generate engaging, personalized messages for each channel."""
            
            response = self.ai_service.chat(
                message=prompt,
                context={"system_prompt": self.SYSTEM_PROMPT}
            )
            
            # Parse JSON response
            try:
                result = json.loads(response)
            except:
                # Fallback messages
                result = self._fallback_messages(latest_message)
            
            state["pending_messages"] = result
            state["current_step"] = "messages_composed"
            
        except Exception as e:
            state["error"] = f"Message composition failed: {str(e)}"
        
        return state
    
    def _fallback_messages(self, goal: str) -> Dict[str, List]:
        """
        Fallback message generation
        """
        return {
            "whatsapp": [
                f"Hi {{name}}! Check out our latest offers just for you!",
                f"Hi {{name}}, we miss you! Here's an exclusive deal.",
            ],
            "sms": [
                "Special offer just for you! Shop now and save 20%.",
                "We have something special waiting for you. Check it out!",
            ],
            "email": [
                {
                    "subject": "Exclusive Offer Just For You",
                    "body": f"Hi {{name}},\n\nWe noticed you haven't visited us lately. Here's 20% off your next order!\n\nShop Now"
                },
                {
                    "subject": "We Miss You!",
                    "body": f"Hi {{name}},\n\nIt's been a while! Come back and see what's new.\n\nExclusive discount inside."
                }
            ]
        }
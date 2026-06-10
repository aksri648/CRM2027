"""
Intent Classifier Node

Per CLAUDE.md:
- Determine user intent
- Allowed intents: segment_request, campaign_request, analytics_request, opportunity_request, system_request, general_request
"""

from typing import Dict, Any
from app.agent.state import AgentState
from app.services.ai_service import AIService


class IntentClassifier:
    """
    Classifies user message intent using AI
    """
    
    SYSTEM_PROMPT = """You are the Intent Classification Agent.

Your responsibility is identifying the user's intent.

You do not answer questions.
You do not generate campaigns.
You do not generate messages.
You do not generate segments.

You only classify intent.

Return valid JSON only.

Format:
{"intent": "segment_request"}

Allowed intents:
- segment_request: User wants to create, modify, or analyze an audience segment
- campaign_request: User wants to create, launch, or analyze a campaign
- analytics_request: User wants to see metrics, stats, or performance data
- opportunity_request: User wants to discover revenue opportunities
- system_request: User wants system status or help
- general_request: General conversation or questions

Never return prose.
Never explain reasoning."""
    
    def __init__(self):
        self.ai_service = AIService()
    
    async def classify(self, state: AgentState) -> AgentState:
        """
        Classify the user's intent from their message
        """
        # Get the latest user message
        latest_message = ""
        for msg in reversed(state["messages"]):
            if msg["role"] == "user":
                latest_message = msg["content"]
                break
        
        if not latest_message:
            state["intent"] = "general_request"
            return state
        
        try:
            # Use AI to classify intent
            response = self.ai_service.chat(
                message=f"Classify the intent of this message: {latest_message}",
                context={"system_prompt": self.SYSTEM_PROMPT}
            )
            
            # Parse JSON response
            import json
            try:
                result = json.loads(response)
                intent = result.get("intent", "general_request")
            except:
                # Fallback: keyword-based classification
                intent = self._keyword_classify(latest_message)
            
            state["intent"] = intent
            state["current_step"] = f"intent_{intent}"
            
        except Exception as e:
            # Fallback to keyword-based
            state["intent"] = self._keyword_classify(latest_message)
            state["current_step"] = f"intent_{state['intent']}"
        
        return state
    
    def _keyword_classify(self, message: str) -> str:
        """
        Fallback keyword-based intent classification
        """
        message_lower = message.lower()
        
        # Segment keywords
        segment_keywords = ["segment", "audience", "customers who", "target", "group", "filter"]
        if any(kw in message_lower for kw in segment_keywords):
            return "segment_request"
        
        # Campaign keywords
        campaign_keywords = ["campaign", "send", "launch", "message", "email", "sms", "whatsapp"]
        if any(kw in message_lower for kw in campaign_keywords):
            return "campaign_request"
        
        # Analytics keywords
        analytics_keywords = ["analytics", "metrics", "stats", "performance", "report", "dashboard"]
        if any(kw in message_lower for kw in analytics_keywords):
            return "analytics_request"
        
        # Opportunity keywords
        opportunity_keywords = ["opportunity", "find", "discover", "potential", "revenue"]
        if any(kw in message_lower for kw in opportunity_keywords):
            return "opportunity_request"
        
        # System keywords
        system_keywords = ["status", "help", "system", "how do i", "what is"]
        if any(kw in message_lower for kw in system_keywords):
            return "system_request"
        
        return "general_request"
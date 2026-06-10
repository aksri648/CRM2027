"""
Agent State Definition

Per CLAUDE.md:
- The state is the single source of truth
- Every node must: read_state(), modify_state(), return_state()
"""

from typing import TypedDict, List, Dict, Any, Optional, Callable
from datetime import datetime


class AgentState(TypedDict):
    """Main agent state for LangGraph workflow"""
    
    # Session info
    session_id: str
    brand_id: int
    
    # Conversation
    messages: List[Dict[str, str]]  # [{"role": "user/assistant", "content": "...}]
    
    # Intent classification
    intent: str  # segment_request, campaign_request, analytics_request, etc.
    
    # Context data (fetched from CRM)
    context: Dict[str, Any]  # {customers: [], segments: [], campaigns: [], etc.}
    
    # Pending actions (for human-in-the-loop)
    pending_segment: Optional[Dict[str, Any]] = None
    pending_messages: Optional[Dict[str, Any]] = None
    pending_campaign: Optional[Dict[str, Any]] = None
    
    # Current workflow step
    current_step: str  # intent_classification, data_fetch, segment_generation, etc.
    
    # Results
    results: Dict[str, Any]  # Final output to return
    
    # Stream callback for SSE
    stream_callback: Optional[Callable] = None
    
    # Error handling
    error: Optional[str] = None


def create_initial_state(
    session_id: str,
    brand_id: int,
    message: str,
    stream_callback: Optional[Callable] = None
) -> AgentState:
    """Create initial state for a new agent session"""
    return AgentState(
        session_id=session_id,
        brand_id=brand_id,
        messages=[{"role": "user", "content": message}],
        intent="",
        context={},
        pending_segment=None,
        pending_messages=None,
        pending_campaign=None,
        current_step="start",
        results={},
        stream_callback=stream_callback,
        error=None,
    )


def add_message(state: AgentState, role: str, content: str) -> AgentState:
    """Add a message to the conversation history"""
    state["messages"].append({"role": role, "content": content})
    return state


def set_intent(state: AgentState, intent: str) -> AgentState:
    """Set the classified intent"""
    state["intent"] = intent
    state["current_step"] = f"intent_{intent}"
    return state


def set_context(state: AgentState, context: Dict[str, Any]) -> AgentState:
    """Set the CRM context data"""
    state["context"] = context
    return state


def set_pending_segment(state: AgentState, segment: Dict[str, Any]) -> AgentState:
    """Set pending segment for approval"""
    state["pending_segment"] = segment
    state["current_step"] = "pending_approval"
    return state


def set_pending_messages(state: AgentState, messages: Dict[str, Any]) -> AgentState:
    """Set pending messages for approval"""
    state["pending_messages"] = messages
    state["current_step"] = "pending_approval"
    return state


def set_pending_campaign(state: AgentState, campaign: Dict[str, Any]) -> AgentState:
    """Set pending campaign for approval"""
    state["pending_campaign"] = campaign
    state["current_step"] = "pending_approval"
    return state


def set_results(state: AgentState, results: Dict[str, Any]) -> AgentState:
    """Set final results"""
    state["results"] = results
    state["current_step"] = "complete"
    return state


def set_error(state: AgentState, error: str) -> AgentState:
    """Set error state"""
    state["error"] = error
    state["current_step"] = "error"
    return state


def get_latest_message(state: AgentState) -> str:
    """Get the latest user message"""
    for msg in reversed(state["messages"]):
        if msg["role"] == "user":
            return msg["content"]
    return ""
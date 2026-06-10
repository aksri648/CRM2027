"""
Agent Router

Per CLAUDE.md:
- POST /api/agent/chat - SSE streaming endpoint for agent chat
- Real LangGraph integration with SSE streaming
"""

from fastapi import APIRouter, Depends, BackgroundTasks
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, Dict, Any
import asyncio
import json
import uuid

from app.core.database import get_db, SessionLocal
from app.core.security import get_current_user
from app.models import User
from app.agent.graph import CampaignAgentGraph

router = APIRouter(prefix="/agent", tags=["agent"])


class ChatRequest(BaseModel):
    session_id: str
    message: str


class ConfirmRequest(BaseModel):
    session_id: str
    action: str  # "launch_campaign" | "create_segment"
    data: dict


@router.post("/chat")
async def chat(
    request: ChatRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user)
):
    """
    SSE streaming endpoint for agent chat
    
    Per CLAUDE.md: All AI interactions use text/event-stream
    """
    session_id = request.session_id or str(uuid.uuid4())
    
    async def generate():
        """Generate SSE events from the agent"""
        # Create agent with database session
        db = SessionLocal()
        try:
            agent = CampaignAgentGraph(db)
            
            # Stream events
            async for event in agent.stream_events(
                session_id=session_id,
                brand_id=current_user.brand_id,
                message=request.message
            ):
                yield event
                # Small delay for visual effect
                await asyncio.sleep(0.3)
        finally:
            db.close()
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )


@router.post("/chat/sync")
async def chat_sync(
    request: ChatRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Synchronous chat endpoint (non-streaming)
    
    Returns the final result after agent processing
    """
    session_id = request.session_id or str(uuid.uuid4())
    
    db = SessionLocal()
    try:
        agent = CampaignAgentGraph(db)
        state = await agent.process_message(
            session_id=session_id,
            brand_id=current_user.brand_id,
            message=request.message
        )
        
        return {
            "session_id": session_id,
            "intent": state.get("intent"),
            "current_step": state.get("current_step"),
            "results": state.get("results"),
            "pending_segment": state.get("pending_segment"),
            "pending_messages": state.get("pending_messages"),
            "pending_campaign": state.get("pending_campaign"),
            "opportunities": state.get("opportunities"),
            "insights": state.get("insights"),
            "error": state.get("error"),
        }
    finally:
        db.close()


@router.post("/confirm")
async def confirm_action(
    request: ConfirmRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Confirm a pending agent action
    
    Per CLAUDE.md: Human in the loop - no campaign may launch automatically
    """
    db = SessionLocal()
    try:
        agent = CampaignAgentGraph(db)
        
        if request.action == "launch_campaign":
            # Create a minimal state with the pending campaign
            from app.agent.state import create_initial_state
            state = create_initial_state(
                session_id=request.session_id,
                brand_id=current_user.brand_id,
                message="Approved campaign launch"
            )
            state["pending_campaign"] = request.data
            
            # Execute dispatch
            state = await agent.execute_dispatch(state)
            
            return {
                "success": True,
                "message": "Campaign launched successfully",
                "campaign_id": state.get("results", {}).get("campaign_id"),
            }
        
        elif request.action == "create_segment":
            # Create the segment
            from app.agent.tools.segment_tools import SegmentTools
            segment_tools = SegmentTools(db)
            
            segment_data = request.data.get("segment", {})
            rules = segment_data.get("rules", [])
            
            result = segment_tools.create_segment(
                brand_id=current_user.brand_id,
                name=segment_data.get("name", "AI Generated Segment"),
                rules=rules,
                description=segment_data.get("reasoning", "")
            )
            
            return {
                "success": True,
                "message": "Segment created successfully",
                "segment_id": result.get("id"),
            }
        
        return {"message": "Action confirmed"}
    finally:
        db.close()


@router.get("/system-status")
def get_system_status(
    current_user: User = Depends(get_current_user)
):
    """Get agent system status"""
    return {
        "worker_status": "Healthy",
        "model": "llama-3.3-70b-versatile",
        "provider": "Groq",
    }


@router.get("/sessions/{session_id}")
def get_session_status(
    session_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get status of an agent session"""
    # In a production system, we'd store session state in Redis
    # For now, return a placeholder
    return {
        "session_id": session_id,
        "status": "active",
        "message": "Session tracking not yet implemented"
    }
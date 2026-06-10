from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel

from app.core.database import get_db
from app.core.security import get_current_user
from app.models import AgentProposal, ProposalStatus, User

router = APIRouter(prefix="/proposals", tags=["proposals"])


class ProposalResponse(BaseModel):
    id: str
    title: str
    segment_id: str = None
    segment_name: str = None
    channel: str
    message_template: str
    confidence_score: float
    ai_reasoning: str = None
    status: str
    created_at: str = None


@router.get("", response_model=List[ProposalResponse])
def list_proposals(
    status: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all proposals for this brand, optionally filtered by status"""
    query = db.query(AgentProposal).filter(AgentProposal.brand_id == current_user.brand_id)
    if status:
        query = query.filter(AgentProposal.status == status)
    else:
        query = query.filter(AgentProposal.status == ProposalStatus.PENDING.value)
    
    proposals = query.all()
    return [prop.to_dict() for prop in proposals]


@router.get("/{proposal_id}", response_model=ProposalResponse)
def get_proposal(
    proposal_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific proposal"""
    proposal = db.query(AgentProposal).filter(
        AgentProposal.id == proposal_id,
        AgentProposal.brand_id == current_user.brand_id
    ).first()
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found")
    return proposal.to_dict()


@router.patch("/{proposal_id}/approve")
def approve_proposal(
    proposal_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Approve a proposal and launch campaign"""
    proposal = db.query(AgentProposal).filter(
        AgentProposal.id == proposal_id,
        AgentProposal.brand_id == current_user.brand_id
    ).first()
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found")
    
    proposal.status = ProposalStatus.APPROVED.value
    db.commit()
    
    return {"message": "Proposal approved and campaign launched", "proposal_id": proposal_id}


@router.patch("/{proposal_id}/reject")
def reject_proposal(
    proposal_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Reject a proposal"""
    proposal = db.query(AgentProposal).filter(
        AgentProposal.id == proposal_id,
        AgentProposal.brand_id == current_user.brand_id
    ).first()
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found")
    
    proposal.status = ProposalStatus.REJECTED.value
    db.commit()
    
    return {"message": "Proposal rejected", "proposal_id": proposal_id}
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel

from app.core.database import get_db
from app.core.security import get_current_user
from app.models import Opportunity, OpportunityStatus, User

router = APIRouter(prefix="/opportunities", tags=["opportunities"])


class OpportunityCreate(BaseModel):
    title: str
    description: str
    audience_description: str = None
    expected_revenue: float = 0
    ai_reasoning: str = None


class OpportunityResponse(BaseModel):
    id: str
    title: str
    description: str
    audience_description: str = None
    expected_revenue: float
    ai_reasoning: str = None
    status: str
    created_at: str = None


@router.get("", response_model=List[OpportunityResponse])
def list_opportunities(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all active opportunities"""
    opportunities = db.query(Opportunity).filter(
        Opportunity.status == OpportunityStatus.ACTIVE.value
    ).all()
    return [opp.to_dict() for opp in opportunities]


@router.post("", response_model=OpportunityResponse)
def create_opportunity(
    opportunity_data: OpportunityCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new opportunity"""
    opportunity = Opportunity(
        title=opportunity_data.title,
        description=opportunity_data.description,
        audience_description=opportunity_data.audience_description,
        expected_revenue=opportunity_data.expected_revenue,
        ai_reasoning=opportunity_data.ai_reasoning,
    )
    db.add(opportunity)
    db.commit()
    db.refresh(opportunity)
    return opportunity.to_dict()


@router.post("/scan")
def scan_opportunities(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Trigger AI scan for new opportunities"""
    # In production, this would trigger a background task
    # For now, return mock data
    return {"message": "Scan triggered", "opportunities_found": 3}


@router.patch("/{opportunity_id}/dismiss")
def dismiss_opportunity(
    opportunity_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Dismiss an opportunity"""
    opportunity = db.query(Opportunity).filter(Opportunity.id == opportunity_id).first()
    if not opportunity:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    
    opportunity.status = OpportunityStatus.DISMISSED.value
    db.commit()
    return {"message": "Opportunity dismissed"}


@router.post("/{opportunity_id}/generate-campaign")
def generate_campaign_from_opportunity(
    opportunity_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate a campaign proposal from an opportunity"""
    opportunity = db.query(Opportunity).filter(Opportunity.id == opportunity_id).first()
    if not opportunity:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    
    # Mark opportunity as converted
    opportunity.status = OpportunityStatus.CONVERTED.value
    db.commit()
    
    return {"message": "Campaign proposal generated", "proposal_id": opportunity_id}
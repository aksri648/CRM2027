from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel

from app.core.database import get_db
from app.core.security import get_current_user
from app.models import ABTest, ABTestStatus, User

router = APIRouter(prefix="/ab-tests", tags=["ab_tests"])


class ABTestResponse(BaseModel):
    id: str
    name: str
    campaign_a_id: str = None
    campaign_b_id: str = None
    status: str
    winner_campaign_id: str = None
    created_at: str = None


@router.get("", response_model=List[ABTestResponse])
def list_ab_tests(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all A/B tests"""
    tests = db.query(ABTest).all()
    return [test.to_dict() for test in tests]


@router.post("", response_model=ABTestResponse)
def create_ab_test(
    name: str,
    campaign_a_id: str = None,
    campaign_b_id: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new A/B test"""
    test = ABTest(
        name=name,
        campaign_a_id=campaign_a_id,
        campaign_b_id=campaign_b_id,
    )
    db.add(test)
    db.commit()
    db.refresh(test)
    return test.to_dict()


@router.get("/{test_id}", response_model=ABTestResponse)
def get_ab_test(
    test_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific A/B test"""
    test = db.query(ABTest).filter(ABTest.id == test_id).first()
    if not test:
        raise HTTPException(status_code=404, detail="A/B test not found")
    return test.to_dict()


@router.patch("/{test_id}/winner")
def declare_winner(
    test_id: str,
    winner_campaign_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Declare winner of an A/B test"""
    test = db.query(ABTest).filter(ABTest.id == test_id).first()
    if not test:
        raise HTTPException(status_code=404, detail="A/B test not found")
    
    test.winner_campaign_id = winner_campaign_id
    test.status = ABTestStatus.COMPLETED.value
    db.commit()
    
    return {"message": "Winner declared", "test_id": test_id}
"""
Proposal Service - Business logic for campaign proposals

Per CLAUDE.md responsibilities:
- Create Proposal
- Approve Proposal
- Reject Proposal
- Convert Proposal To Campaign

Approval Flow:
    AI Agent → Proposal → Approve → Campaign → Launch

AI never bypasses proposal stage.
"""

from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
from datetime import datetime

from app.models.agent_proposal import AgentProposal, ProposalStatus
from app.models.campaign import Campaign, CampaignStatus, CampaignChannel
from app.models.segment import Segment
from app.schemas.campaign import CampaignCreate


class ProposalService:
    
    @staticmethod
    def create_proposal(
        db: Session,
        brand_id: int,
        title: str,
        segment_id: Optional[int] = None,
        channel: str = "email",
        message_template: str = "",
        confidence_score: float = 0.5,
        ai_reasoning: str = ""
    ) -> AgentProposal:
        """
        Create a new proposal
        
        Per CLAUDE.md: AI never bypasses proposal stage
        """
        proposal = AgentProposal(
            title=title,
            segment_id=segment_id,
            channel=channel,
            message_template=message_template,
            confidence_score=confidence_score,
            ai_reasoning=ai_reasoning,
            status=ProposalStatus.PENDING,
        )
        db.add(proposal)
        db.commit()
        db.refresh(proposal)
        return proposal
    
    @staticmethod
    def get_proposal(db: Session, proposal_id: int) -> Optional[AgentProposal]:
        """Get proposal by ID"""
        return db.query(AgentProposal).filter(AgentProposal.id == proposal_id).first()
    
    @staticmethod
    def list_proposals(
        db: Session,
        brand_id: int,
        status: Optional[ProposalStatus] = None,
        skip: int = 0,
        limit: int = 50
    ) -> List[AgentProposal]:
        """
        List proposals
        
        If status is None, returns PENDING proposals by default
        """
        query = db.query(AgentProposal)
        
        if status:
            query = query.filter(AgentProposal.status == status)
        else:
            query = query.filter(AgentProposal.status == ProposalStatus.PENDING)
        
        return query.order_by(AgentProposal.created_at.desc()).offset(skip).limit(limit).all()
    
    @staticmethod
    def approve_proposal(db: Session, proposal_id: int) -> Dict[str, Any]:
        """
        Approve a proposal and launch campaign
        
        Per CLAUDE.md: Approval Flow - Approve → Campaign → Launch
        """
        proposal = db.query(AgentProposal).filter(AgentProposal.id == proposal_id).first()
        if not proposal:
            raise ValueError(f"Proposal {proposal_id} not found")
        
        if proposal.status != ProposalStatus.PENDING:
            raise ValueError(f"Proposal {proposal_id} is not pending")
        
        # Get segment if specified
        segment = None
        if proposal.segment_id:
            segment = db.query(Segment).filter(Segment.id == proposal.segment_id).first()
        
        # Create campaign from proposal
        campaign = Campaign(
            brand_id=proposal.segment_id,  # This needs proper brand_id handling
            name=proposal.title,
            channel=CampaignChannel(proposal.channel) if hasattr(CampaignChannel, proposal.channel.upper()) else CampaignChannel.EMAIL,
            status=CampaignStatus.DRAFT,
            message_content=proposal.message_template,
            segment_id=proposal.segment_id,
        )
        db.add(campaign)
        db.flush()
        
        # Update proposal status
        proposal.status = ProposalStatus.APPROVED
        proposal.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(campaign)
        db.refresh(proposal)
        
        return {
            "proposal_id": proposal_id,
            "campaign_id": campaign.id,
            "status": "approved",
            "message": "Proposal approved and campaign created",
        }
    
    @staticmethod
    def reject_proposal(db: Session, proposal_id: int) -> bool:
        """Reject a proposal"""
        proposal = db.query(AgentProposal).filter(AgentProposal.id == proposal_id).first()
        if not proposal:
            return False
        
        proposal.status = ProposalStatus.REJECTED
        proposal.updated_at = datetime.utcnow()
        db.commit()
        return True
    
    @staticmethod
    def update_proposal(
        db: Session,
        proposal_id: int,
        title: Optional[str] = None,
        segment_id: Optional[int] = None,
        channel: Optional[str] = None,
        message_template: Optional[str] = None,
        confidence_score: Optional[float] = None,
        ai_reasoning: Optional[str] = None
    ) -> Optional[AgentProposal]:
        """Update a proposal"""
        proposal = db.query(AgentProposal).filter(AgentProposal.id == proposal_id).first()
        if not proposal:
            return None
        
        if title is not None:
            proposal.title = title
        if segment_id is not None:
            proposal.segment_id = segment_id
        if channel is not None:
            proposal.channel = channel
        if message_template is not None:
            proposal.message_template = message_template
        if confidence_score is not None:
            proposal.confidence_score = confidence_score
        if ai_reasoning is not None:
            proposal.ai_reasoning = ai_reasoning
        
        proposal.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(proposal)
        return proposal
    
    @staticmethod
    def get_proposal_audience(db: Session, proposal_id: int) -> Dict[str, Any]:
        """Get target audience details for a proposal"""
        proposal = db.query(AgentProposal).filter(AgentProposal.id == proposal_id).first()
        if not proposal:
            return {}
        
        if not proposal.segment_id:
            return {
                "proposal_id": proposal_id,
                "segment_id": None,
                "segment_name": None,
                "customer_count": 0,
            }
        
        segment = db.query(Segment).filter(Segment.id == proposal.segment_id).first()
        if not segment:
            return {
                "proposal_id": proposal_id,
                "segment_id": proposal.segment_id,
                "segment_name": "Unknown",
                "customer_count": 0,
            }
        
        return {
            "proposal_id": proposal_id,
            "segment_id": segment.id,
            "segment_name": segment.name,
            "segment_description": segment.description,
            "customer_count": segment.customer_count,
        }
    
    @staticmethod
    def score_proposal_confidence(
        db: Session,
        segment_id: int,
        channel: str,
        message_template: str
    ) -> float:
        """
        Calculate confidence score for a proposal
        
        Factors:
        - Segment size (too small or too large reduces confidence)
        - Channel appropriateness
        - Message template quality
        """
        score = 0.5  # Base score
        
        # Segment size factor
        segment = db.query(Segment).filter(Segment.id == segment_id).first()
        if segment:
            customer_count = segment.customer_count
            if 100 <= customer_count <= 5000:
                score += 0.2  # Ideal segment size
            elif customer_count < 50:
                score -= 0.2  # Too small
            elif customer_count > 20000:
                score -= 0.1  # Very large, less targeted
        
        # Channel factor
        if channel in ["whatsapp", "email"]:
            score += 0.1  # High-performing channels
        
        # Message template factor
        if len(message_template) > 50:
            score += 0.1  # Substantial message
        if "{" in message_template and "}" in message_template:
            score += 0.1  # Personalized
        
        return min(max(score, 0.0), 1.0)  # Clamp between 0 and 1
    
    @staticmethod
    def get_proposal_stats(db: Session, brand_id: int) -> Dict[str, Any]:
        """Get aggregate proposal statistics"""
        total = db.query(AgentProposal).count()
        
        by_status = {}
        for status in ProposalStatus:
            count = db.query(AgentProposal).filter(
                AgentProposal.status == status
            ).count()
            by_status[status.value] = count
        
        avg_confidence = db.query(func.avg(AgentProposal.confidence_score)).filter(
            AgentProposal.status == ProposalStatus.PENDING
        ).scalar() or 0
        
        return {
            "total_proposals": total,
            "by_status": by_status,
            "average_confidence": float(avg_confidence),
        }


# Import func for avg
from sqlalchemy import func
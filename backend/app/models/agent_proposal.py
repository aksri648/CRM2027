import uuid
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey, Enum
import enum

from app.core.database import Base


class ProposalStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class AgentProposal(Base):
    __tablename__ = "agent_proposals"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    segment_id = Column(Integer, ForeignKey("segments.id"), nullable=True)
    channel = Column(String(50), nullable=False)  # whatsapp, sms, email, rcs
    message_template = Column(Text, nullable=False)
    confidence_score = Column(Float, default=0.5)  # 0.0 - 1.0
    ai_reasoning = Column(Text, nullable=True)
    status = Column(String(50), default=ProposalStatus.PENDING.value)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            "id": str(self.id),
            "title": self.title,
            "segment_id": str(self.segment_id) if self.segment_id else None,
            "channel": self.channel,
            "message_template": self.message_template,
            "confidence_score": self.confidence_score,
            "ai_reasoning": self.ai_reasoning,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
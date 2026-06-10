import uuid
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
import enum

from app.core.database import Base


class ABTestStatus(str, enum.Enum):
    DRAFT = "draft"
    RUNNING = "running"
    COMPLETED = "completed"


class ABTest(Base):
    __tablename__ = "ab_tests"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    campaign_a_id = Column(Integer, ForeignKey("campaigns.id"), nullable=True)
    campaign_b_id = Column(Integer, ForeignKey("campaigns.id"), nullable=True)
    status = Column(String(50), default=ABTestStatus.DRAFT.value)
    winner_campaign_id = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            "id": str(self.id),
            "name": self.name,
            "campaign_a_id": str(self.campaign_a_id) if self.campaign_a_id else None,
            "campaign_b_id": str(self.campaign_b_id) if self.campaign_b_id else None,
            "status": self.status,
            "winner_campaign_id": str(self.winner_campaign_id) if self.winner_campaign_id else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
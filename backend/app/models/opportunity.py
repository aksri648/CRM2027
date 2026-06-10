import uuid
import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Text, DateTime

from app.core.database import Base


class OpportunityStatus(str, enum.Enum):
    ACTIVE = "active"
    DISMISSED = "dismissed"
    CONVERTED = "converted"


class Opportunity(Base):
    __tablename__ = "opportunities"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    audience_description = Column(Text, nullable=True)
    expected_revenue = Column(Float, default=0)
    ai_reasoning = Column(Text, nullable=True)
    status = Column(String(50), default=OpportunityStatus.ACTIVE.value)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            "id": str(self.id),
            "title": self.title,
            "description": self.description,
            "audience_description": self.audience_description,
            "expected_revenue": self.expected_revenue,
            "ai_reasoning": self.ai_reasoning,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
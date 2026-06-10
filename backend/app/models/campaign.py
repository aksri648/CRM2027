from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text, Float, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.core.database import Base


class CampaignStatus(str, enum.Enum):
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    SENDING = "sending"
    SENT = "sent"
    CANCELLED = "cancelled"


class CampaignChannel(str, enum.Enum):
    EMAIL = "email"
    SMS = "sms"
    WHATSAPP = "whatsapp"
    RCS = "rcs"
    ALL = "all"


class Campaign(Base):
    __tablename__ = "campaigns"

    id = Column(Integer, primary_key=True, index=True)
    brand_id = Column(Integer, ForeignKey("brands.id"), nullable=False, index=True)
    
    name = Column(String(255), nullable=False)
    subject = Column(String(500), nullable=True)  # For email
    channel = Column(Enum(CampaignChannel), default=CampaignChannel.EMAIL)
    status = Column(Enum(CampaignStatus), default=CampaignStatus.DRAFT)
    
    # Content
    template_id = Column(Integer, ForeignKey("campaign_templates.id"), nullable=True)
    message_content = Column(Text, nullable=True)
    personalisation_tokens = Column(Text, nullable=True)  # JSON
    
    # Audience
    segment_id = Column(Integer, ForeignKey("segments.id"), nullable=True)
    target_count = Column(Integer, default=0)
    
    # Scheduling
    scheduled_at = Column(DateTime, nullable=True)
    sent_at = Column(DateTime, nullable=True)
    
    # Stats (cached)
    sent_count = Column(Integer, default=0)
    delivered_count = Column(Integer, default=0)
    opened_count = Column(Integer, default=0)
    clicked_count = Column(Integer, default=0)
    converted_count = Column(Integer, default=0)
    failed_count = Column(Integer, default=0)
    revenue = Column(Float, default=0)
    
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    brand = relationship("Brand", back_populates="campaigns")
    segment = relationship("Segment")
    template = relationship("CampaignTemplate")
    creator = relationship("User")
    communications = relationship("Communication", back_populates="campaign", cascade="all, delete-orphan")
    attributed_orders = relationship("Order", back_populates="campaign")


class CampaignTemplate(Base):
    __tablename__ = "campaign_templates"

    id = Column(Integer, primary_key=True, index=True)
    brand_id = Column(Integer, ForeignKey("brands.id"), nullable=False, index=True)
    
    name = Column(String(255), nullable=False)
    channel = Column(Enum(CampaignChannel), default=CampaignChannel.EMAIL)
    subject = Column(String(500), nullable=True)
    content = Column(Text, nullable=False)
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
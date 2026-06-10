from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.core.database import Base


class CommunicationStatus(str, enum.Enum):
    QUEUED = "queued"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    BOUNCED = "bounced"
    UNSUBSCRIBED = "unsubscribed"


class CommunicationEventType(str, enum.Enum):
    QUEUED = "queued"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    OPENED = "opened"
    READ = "read"
    CLICKED = "clicked"
    UNSUBSCRIBED = "unsubscribed"
    BOUNCED = "bounced"


class Communication(Base):
    __tablename__ = "communications"

    id = Column(Integer, primary_key=True, index=True)
    brand_id = Column(Integer, ForeignKey("brands.id"), nullable=False, index=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), nullable=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False, index=True)
    
    channel = Column(String(20), nullable=False)  # email, sms, whatsapp, rcs
    status = Column(Enum(CommunicationStatus), default=CommunicationStatus.QUEUED)
    
    # Content
    recipient = Column(String(255), nullable=False)  # email or phone
    subject = Column(String(500), nullable=True)
    content = Column(Text, nullable=False)
    
    # External tracking
    external_id = Column(String(255), nullable=True, index=True)  # ID from channel service
    provider_response = Column(Text, nullable=True)  # Raw response from channel
    
    # Timestamps
    queued_at = Column(DateTime, default=datetime.utcnow)
    sent_at = Column(DateTime, nullable=True)
    delivered_at = Column(DateTime, nullable=True)
    opened_at = Column(DateTime, nullable=True)
    clicked_at = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    brand = relationship("Brand")
    campaign = relationship("Campaign", back_populates="communications")
    customer = relationship("Customer", back_populates="communications")
    events = relationship("CommunicationEvent", back_populates="communication", cascade="all, delete-orphan")


class CommunicationEvent(Base):
    __tablename__ = "communication_events"

    id = Column(Integer, primary_key=True, index=True)
    communication_id = Column(Integer, ForeignKey("communications.id"), nullable=False, index=True)
    
    event_type = Column(Enum(CommunicationEventType), nullable=False)
    extra_data = Column(Text, nullable=True)  # JSON for additional data (e.g., click URL)
    
    occurred_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    communication = relationship("Communication", back_populates="events")
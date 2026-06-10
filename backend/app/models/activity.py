from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.core.database import Base


class ActivityType(str, enum.Enum):
    ORDER_PLACED = "order_placed"
    ORDER_COMPLETED = "order_completed"
    ORDER_CANCELLED = "order_cancelled"
    CAMPAIGN_SENT = "campaign_sent"
    CAMPAIGN_OPENED = "campaign_opened"
    CAMPAIGN_CLICKED = "campaign_clicked"
    SEGMENT_JOINED = "segment_joined"
    SEGMENT_LEFT = "segment_left"
    TAG_ADDED = "tag_added"
    TAG_REMOVED = "tag_removed"
    PROFILE_UPDATED = "profile_updated"
    SUBSCRIBED = "subscribed"
    UNSUBSCRIBED = "unsubscribed"


class Activity(Base):
    __tablename__ = "activities"

    id = Column(Integer, primary_key=True, index=True)
    brand_id = Column(Integer, ForeignKey("brands.id"), nullable=False, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False, index=True)
    
    activity_type = Column(Enum(ActivityType), nullable=False)
    
    # Reference to related entity
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), nullable=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=True)
    segment_id = Column(Integer, ForeignKey("segments.id"), nullable=True)
    
    # Details
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    extra_data = Column(Text, nullable=True)  # JSON for additional data
    
    occurred_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    brand = relationship("Brand")
    customer = relationship("Customer", back_populates="activities")
    campaign = relationship("Campaign")
    order = relationship("Order")
    segment = relationship("Segment")
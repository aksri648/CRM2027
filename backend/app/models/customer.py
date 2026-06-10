from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text, Float, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.core.database import Base


class CustomerChannel(str, enum.Enum):
    EMAIL = "email"
    SMS = "sms"
    WHATSAPP = "whatsapp"
    RCS = "rcs"


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    brand_id = Column(Integer, ForeignKey("brands.id"), nullable=False, index=True)
    
    # Basic info
    email = Column(String(255), nullable=True, index=True)
    phone = Column(String(50), nullable=True, index=True)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    
    # Demographics
    gender = Column(String(20), nullable=True)
    date_of_birth = Column(DateTime, nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    country = Column(String(100), nullable=True, default="India")
    postal_code = Column(String(20), nullable=True)
    
    # Preferences
    preferred_channel = Column(Enum(CustomerChannel), default=CustomerChannel.EMAIL)
    is_unsubscribed = Column(Boolean, default=False)
    unsubscribed_at = Column(DateTime, nullable=True)
    
    # Metadata
    tags = Column(Text, nullable=True)  # JSON array of tag names
    extra_data = Column(Text, nullable=True)  # JSON for additional fields
    
    # Engagement scoring
    engagement_score = Column(Integer, default=0)
    last_engaged_at = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    brand = relationship("Brand", back_populates="customers")
    orders = relationship("Order", back_populates="customer", cascade="all, delete-orphan")
    communications = relationship("Communication", back_populates="customer", cascade="all, delete-orphan")
    activities = relationship("Activity", back_populates="customer", cascade="all, delete-orphan")
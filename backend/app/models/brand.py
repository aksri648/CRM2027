from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class Brand(Base):
    __tablename__ = "brands"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), nullable=False)
    phone = Column(String(50), nullable=True)
    address = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    users = relationship("User", back_populates="brand", cascade="all, delete-orphan")
    customers = relationship("Customer", back_populates="brand", cascade="all, delete-orphan")
    products = relationship("Product", back_populates="brand", cascade="all, delete-orphan")
    segments = relationship("Segment", back_populates="brand", cascade="all, delete-orphan")
    campaigns = relationship("Campaign", back_populates="brand", cascade="all, delete-orphan")
    tags = relationship("Tag", back_populates="brand", cascade="all, delete-orphan")
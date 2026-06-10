from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    brand_id = Column(Integer, ForeignKey("brands.id"), nullable=False, index=True)
    
    name = Column(String(100), nullable=False)
    slug = Column(String(100), nullable=False)
    color = Column(String(20), nullable=True)  # hex color
    description = Column(String(500), nullable=True)
    
    is_system = Column(Boolean, default=False)  # system tags can't be deleted
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    brand = relationship("Brand", back_populates="tags")
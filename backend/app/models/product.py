from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Float, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    brand_id = Column(Integer, ForeignKey("brands.id"), nullable=False, index=True)
    
    name = Column(String(255), nullable=False)
    sku = Column(String(100), nullable=True, index=True)
    description = Column(Text, nullable=True)
    category = Column(String(100), nullable=True)
    price = Column(Float, nullable=False)
    cost = Column(Float, nullable=True)
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    brand = relationship("Brand", back_populates="products")
    order_items = relationship("OrderItem", back_populates="product")
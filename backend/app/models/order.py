from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Float, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    brand_id = Column(Integer, ForeignKey("brands.id"), nullable=False, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False, index=True)
    
    order_number = Column(String(100), unique=True, nullable=False, index=True)
    status = Column(String(50), default="completed")  # pending, completed, cancelled, refunded
    
    # Totals
    subtotal = Column(Float, nullable=False)
    discount = Column(Float, default=0)
    tax = Column(Float, default=0)
    total = Column(Float, nullable=False)
    
    # Source
    channel = Column(String(50), nullable=True)  # online, offline, app
    source = Column(String(100), nullable=True)  # website, instagram, referral
    
    # Attribution
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), nullable=True)
    
    # Timestamps
    order_date = Column(DateTime, default=datetime.utcnow, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    brand = relationship("Brand")
    customer = relationship("Customer", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    campaign = relationship("Campaign", back_populates="attributed_orders")


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    
    quantity = Column(Integer, nullable=False, default=1)
    unit_price = Column(Float, nullable=False)
    discount = Column(Float, default=0)
    total = Column(Float, nullable=False)

    # Relationships
    order = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="order_items")
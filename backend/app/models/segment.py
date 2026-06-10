from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.core.database import Base


class SegmentRuleOperator(str, enum.Enum):
    EQUALS = "equals"
    NOT_EQUALS = "not_equals"
    CONTAINS = "contains"
    NOT_CONTAINS = "not_contains"
    GREATER_THAN = "greater_than"
    LESS_THAN = "less_than"
    BETWEEN = "between"
    IN = "in"
    NOT_IN = "not_in"
    IS_NULL = "is_null"
    IS_NOT_NULL = "is_not_null"


class SegmentRuleField(str, enum.Enum):
    # Customer fields
    EMAIL = "email"
    PHONE = "phone"
    CITY = "city"
    STATE = "state"
    COUNTRY = "country"
    GENDER = "gender"
    DATE_OF_BIRTH = "date_of_birth"
    TAGS = "tags"
    ENGAGEMENT_SCORE = "engagement_score"
    IS_UNSUBSCRIBED = "is_unsubscribed"
    
    # Order fields
    TOTAL_ORDERS = "total_orders"
    TOTAL_SPENT = "total_spent"
    AVERAGE_ORDER_VALUE = "average_order_value"
    LAST_ORDER_DATE = "last_order_date"
    DAYS_SINCE_LAST_ORDER = "days_since_last_order"
    FIRST_ORDER_DATE = "first_order_date"


class Segment(Base):
    __tablename__ = "segments"

    id = Column(Integer, primary_key=True, index=True)
    brand_id = Column(Integer, ForeignKey("brands.id"), nullable=False, index=True)
    
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    rules = Column(Text, nullable=False)  # JSON array of rules
    is_active = Column(Boolean, default=True)
    
    # Stats (cached)
    customer_count = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    brand = relationship("Brand", back_populates="segments")
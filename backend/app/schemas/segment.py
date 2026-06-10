from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class SegmentRuleBase(BaseModel):
    field: str
    operator: str
    value: Optional[str] = None  # JSON encoded value


class SegmentRuleCreate(SegmentRuleBase):
    pass


class SegmentBase(BaseModel):
    name: str
    description: Optional[str] = None
    rules: str  # JSON array of rules
    is_active: bool = True


class SegmentCreate(SegmentBase):
    pass


class SegmentUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    rules: Optional[str] = None
    is_active: Optional[bool] = None


class SegmentResponse(SegmentBase):
    id: int
    brand_id: int
    customer_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SegmentWithCustomers(SegmentResponse):
    pass  # Customers are fetched separately


class SegmentPreviewRequest(BaseModel):
    rules: str  # JSON array of rules


class SegmentPreviewResponse(BaseModel):
    customer_count: int
    sample_customers: List[dict]  # First 10 customers
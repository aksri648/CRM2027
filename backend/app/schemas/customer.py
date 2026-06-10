from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from app.models.customer import CustomerChannel


class CustomerBase(BaseModel):
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    gender: Optional[str] = None
    date_of_birth: Optional[datetime] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    postal_code: Optional[str] = None
    preferred_channel: Optional[CustomerChannel] = CustomerChannel.EMAIL


class CustomerCreate(CustomerBase):
    pass


class CustomerUpdate(BaseModel):
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    gender: Optional[str] = None
    date_of_birth: Optional[datetime] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    postal_code: Optional[str] = None
    preferred_channel: Optional[CustomerChannel] = None
    tags: Optional[str] = None
    extra_data: Optional[str] = None


class CustomerResponse(CustomerBase):
    id: int
    brand_id: int
    is_unsubscribed: bool
    unsubscribed_at: Optional[datetime]
    tags: Optional[str]
    extra_data: Optional[str]
    engagement_score: int
    last_engaged_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CustomerWithStats(CustomerResponse):
    total_orders: int = 0
    total_spent: float = 0
    average_order_value: float = 0
    last_order_date: Optional[datetime] = None


class CustomerImportRequest(BaseModel):
    customers: List[CustomerCreate]
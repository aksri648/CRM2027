from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class OrderItemBase(BaseModel):
    product_id: int
    quantity: int = 1
    unit_price: float
    discount: float = 0


class OrderItemCreate(OrderItemBase):
    pass


class OrderItemResponse(OrderItemBase):
    id: int
    order_id: int
    total: float

    class Config:
        from_attributes = True


class OrderBase(BaseModel):
    order_number: str
    customer_id: int
    status: str = "completed"
    subtotal: float
    discount: float = 0
    tax: float = 0
    total: float
    channel: Optional[str] = None
    source: Optional[str] = None
    campaign_id: Optional[int] = None
    order_date: Optional[datetime] = None


class OrderCreate(OrderBase):
    items: List[OrderItemCreate]


class OrderUpdate(BaseModel):
    status: Optional[str] = None
    subtotal: Optional[float] = None
    discount: Optional[float] = None
    tax: Optional[float] = None
    total: Optional[float] = None


class OrderResponse(OrderBase):
    id: int
    brand_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class OrderWithItems(OrderResponse):
    items: List[OrderItemResponse]
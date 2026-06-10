from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.models.communication import CommunicationStatus, CommunicationEventType


class CommunicationBase(BaseModel):
    channel: str
    recipient: str
    subject: Optional[str] = None
    content: str


class CommunicationCreate(CommunicationBase):
    customer_id: int
    campaign_id: Optional[int] = None


class CommunicationResponse(CommunicationBase):
    id: int
    brand_id: int
    campaign_id: Optional[int]
    customer_id: int
    status: CommunicationStatus
    external_id: Optional[str]
    queued_at: datetime
    sent_at: Optional[datetime]
    delivered_at: Optional[datetime]
    opened_at: Optional[datetime]
    clicked_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CommunicationEventResponse(BaseModel):
    id: int
    communication_id: int
    event_type: CommunicationEventType
    extra_data: Optional[str]
    occurred_at: datetime

    class Config:
        from_attributes = True


class CallbackRequest(BaseModel):
    external_id: str
    event_type: str
    extra_data: Optional[str] = None
    occurred_at: Optional[datetime] = None


class CallbackResponse(BaseModel):
    success: bool
    message: str
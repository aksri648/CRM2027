from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.models.campaign import CampaignStatus, CampaignChannel


class CampaignBase(BaseModel):
    name: str
    subject: Optional[str] = None
    channel: CampaignChannel = CampaignChannel.EMAIL
    message_content: Optional[str] = None
    personalisation_tokens: Optional[str] = None
    segment_id: Optional[int] = None
    scheduled_at: Optional[datetime] = None


class CampaignCreate(CampaignBase):
    pass


class CampaignUpdate(BaseModel):
    name: Optional[str] = None
    subject: Optional[str] = None
    channel: Optional[CampaignChannel] = None
    message_content: Optional[str] = None
    personalisation_tokens: Optional[str] = None
    segment_id: Optional[int] = None
    scheduled_at: Optional[datetime] = None
    status: Optional[CampaignStatus] = None


class CampaignResponse(CampaignBase):
    id: int
    brand_id: int
    status: CampaignStatus
    template_id: Optional[int]
    target_count: int
    sent_at: Optional[datetime]
    sent_count: int
    delivered_count: int
    opened_count: int
    clicked_count: int
    converted_count: int
    failed_count: int
    revenue: float
    created_by: Optional[int]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CampaignStats(BaseModel):
    campaign_id: int
    sent_count: int
    delivered_count: int
    delivered_rate: float
    opened_count: int
    opened_rate: float
    clicked_count: int
    clicked_rate: float
    converted_count: int
    converted_rate: float
    failed_count: int
    failed_rate: float
    revenue: float


class CampaignSendRequest(BaseModel):
    segment_id: Optional[int] = None
    customer_ids: Optional[List[int]] = None  # Override segment if provided


class CampaignTemplateBase(BaseModel):
    name: str
    channel: CampaignChannel = CampaignChannel.EMAIL
    subject: Optional[str] = None
    content: str


class CampaignTemplateCreate(CampaignTemplateBase):
    pass


class CampaignTemplateResponse(CampaignTemplateBase):
    id: int
    brand_id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
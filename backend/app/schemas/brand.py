from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class BrandBase(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None
    address: Optional[str] = None


class BrandCreate(BrandBase):
    pass


class BrandUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    is_active: Optional[bool] = None


class BrandResponse(BrandBase):
    id: int
    slug: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
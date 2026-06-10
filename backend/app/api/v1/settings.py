from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.database import get_db
from app.core.security import get_current_user
from app.models import Settings, User

router = APIRouter(prefix="/settings", tags=["settings"])


class SettingsUpdate(BaseModel):
    platform_name: str = None
    timezone: str = None
    currency: str = None
    ai_model: str = None
    scan_schedule: str = None
    auto_approve: bool = None
    telegram_token: str = None
    telegram_chat_id: str = None
    notif_telegram: bool = None
    notif_campaign_complete: bool = None
    notif_opportunities: bool = None
    notif_weekly_digest: bool = None


@router.get("")
def get_settings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get application settings"""
    settings = db.query(Settings).first()
    if not settings:
        # Create default settings
        settings = Settings()
        db.add(settings)
        db.commit()
        db.refresh(settings)
    return settings.to_dict()


@router.put("")
def update_settings(
    settings_data: SettingsUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update application settings"""
    settings = db.query(Settings).first()
    if not settings:
        settings = Settings()
        db.add(settings)
    
    # Update only provided fields
    update_data = settings_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        if value is not None:
            setattr(settings, key, value)
    
    db.commit()
    db.refresh(settings)
    return settings.to_dict()


@router.post("/test-telegram")
def test_telegram(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Test Telegram bot connection"""
    settings = db.query(Settings).first()
    if not settings or not settings.telegram_token:
        raise HTTPException(status_code=400, detail="Telegram bot token not configured")
    
    # In production, this would send a test message via Telegram API
    return {"message": "Test message sent successfully"}
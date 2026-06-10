from sqlalchemy import Column, Integer, String, Boolean, Text
from app.core.database import Base


class Settings(Base):
    __tablename__ = "settings"

    id = Column(Integer, primary_key=True, default=1)
    platform_name = Column(String(255), default="Xeno AI Campaign Studio")
    timezone = Column(String(100), default="Asia/Kolkata")
    currency = Column(String(10), default="INR")
    ai_model = Column(String(100), default="GPT-5")
    scan_schedule = Column(String(100), default="Daily at 6:00 AM")
    auto_approve = Column(Boolean, default=False)
    telegram_token = Column(Text, nullable=True)
    telegram_chat_id = Column(Text, nullable=True)
    notif_telegram = Column(Boolean, default=True)
    notif_campaign_complete = Column(Boolean, default=True)
    notif_opportunities = Column(Boolean, default=True)
    notif_weekly_digest = Column(Boolean, default=False)

    def to_dict(self):
        return {
            "platform_name": self.platform_name,
            "timezone": self.timezone,
            "currency": self.currency,
            "ai_model": self.ai_model,
            "scan_schedule": self.scan_schedule,
            "auto_approve": self.auto_approve,
            "telegram_token": self.telegram_token,
            "telegram_chat_id": self.telegram_chat_id,
            "notif_telegram": self.notif_telegram,
            "notif_campaign_complete": self.notif_campaign_complete,
            "notif_opportunities": self.notif_opportunities,
            "notif_weekly_digest": self.notif_weekly_digest,
        }
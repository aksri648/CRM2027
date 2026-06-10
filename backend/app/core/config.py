from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "Xeno Mini CRM"
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"
    
    # Database
    DATABASE_URL: str = "sqlite:///./xeno_crm.db"
    
    # JWT
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Channel Service
    CHANNEL_SERVICE_URL: str = "http://localhost:8001"
    CHANNEL_SERVICE_API_KEY: str = "channel-service-api-key"
    
    # AI (kimchi.dev)
    KIMCHI_BASE_URL: str = "https://api.kimchi.dev/v1"
    KIMCHI_API_KEY: Optional[str] = None
    AI_MODEL: str = "gpt-4o-mini"
    
    # CRM Callback URL (for channel service to call back)
    CRM_CALLBACK_URL: str = "http://localhost:8000/api/v1/callbacks"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
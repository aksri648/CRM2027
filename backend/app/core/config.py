from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "Xeno Mini CRM"
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"
    
    # Database
    DATABASE_URL: str = "sqlite:///./xeno_crm.db"
    
    # JWT - SECRET_KEY must be set via environment variable in production
    SECRET_KEY: str = ""  # Must be set via CLERK_SECRET_KEY or SECRET_KEY env var
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Clerk Authentication
    CLERK_PUBLISHABLE_KEY: Optional[str] = None
    CLERK_SECRET_KEY: Optional[str] = None
    CLERK_JWKS_URL: str = "https://api.clerk.dev/v1/jwks"
    CLERK_ISSUER: str = "https://clerk.example.com"  # Update with actual issuer
    CLERK_AUDIENCE: Optional[str] = None
    
    # Channel Service
    CHANNEL_SERVICE_URL: str = "http://localhost:8001"
    CHANNEL_SERVICE_API_KEY: str = "channel-service-api-key"
    
    # AI (kimchi.dev)
    KIMCHI_BASE_URL: str = "https://api.kimchi.dev/v1"
    KIMCHI_API_KEY: Optional[str] = None
    AI_MODEL: str = "gpt-4o-mini"
    
    # CRM Callback URL (for channel service to call back)
    CRM_CALLBACK_URL: str = "http://localhost:8000/api/v1/callbacks"
    
    # CORS - Allowed origins (comma-separated in env)
    ALLOWED_ORIGINS: str = "http://localhost:5173,http://localhost:3000"
    
    class Config:
        env_file = ".env"
        case_sensitive = True
    
    def get_allowed_origins(self) -> list:
        """Parse ALLOWED_ORIGINS string into list"""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",") if origin.strip()]


settings = Settings()
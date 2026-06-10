from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import engine, Base, SessionLocal
from app.core.security import get_password_hash
from app.models.user import User
from app.models.brand import Brand
from app.api.v1 import api_router

# Initialize OpenTelemetry instrumentation (isolated from business logic)
# This will not block or modify any existing functionality
try:
    from telemetry import init_telemetry
    telemetry_status = init_telemetry()
    print(f"Telemetry status: {telemetry_status}")
except Exception as e:
    print(f"Telemetry initialization skipped: {e}")

# Create database tables
Base.metadata.create_all(bind=engine)

# Create default user on startup
def create_default_user():
    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.email == "admin@example.com").first()
        if not existing:
            brand = Brand(name="Demo Store", slug="demo-store", email="admin@example.com")
            db.add(brand)
            db.flush()
            
            user = User(
                email="admin@example.com",
                hashed_password=get_password_hash("admin123"),
                full_name="Admin User",
                brand_id=brand.id
            )
            db.add(user)
            db.commit()
            print("Default user created: admin@example.com / admin123")
    finally:
        db.close()

create_default_user()

app = FastAPI(
    title=settings.APP_NAME,
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
    docs_url=f"{settings.API_V1_PREFIX}/docs",
    redoc_url=f"{settings.API_V1_PREFIX}/redoc"
)

# CORS middleware - use specific origins instead of "*" when credentials are enabled
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_allowed_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix=settings.API_V1_PREFIX)


@app.get("/")
def root():
    return {
        "name": settings.APP_NAME,
        "version": "1.0.0",
        "docs": f"{settings.API_V1_PREFIX}/docs"
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.get("/me")
def get_me(current_user: User = Depends(get_current_user)):
    """Get current authenticated user"""
    return {
        "id": current_user.id,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "role": current_user.role.value,
        "brand_id": current_user.brand_id,
        "is_active": current_user.is_active
    }


@router.get("/verify")
def verify_auth(current_user: User = Depends(get_current_user)):
    """Verify authentication is working"""
    return {
        "authenticated": True,
        "user_id": current_user.id,
        "email": current_user.email
    }
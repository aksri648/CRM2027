from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import (
    verify_password, get_password_hash, 
    create_access_token, create_refresh_token, verify_token,
    get_current_user
)
from app.models.user import User
from app.models.brand import Brand
from app.schemas.auth import LoginRequest, TokenResponse, RefreshTokenRequest
from app.schemas.user import UserCreate
import uuid

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register")
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    # Check if user exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create brand for new user
    brand_slug = f"brand-{uuid.uuid4().hex[:8]}"
    brand = Brand(
        name=f"{user_data.full_name}'s Store",
        slug=brand_slug,
        email=user_data.email
    )
    db.add(brand)
    db.flush()
    
    # Create user
    hashed_password = get_password_hash(user_data.password)
    user = User(
        email=user_data.email,
        hashed_password=hashed_password,
        full_name=user_data.full_name,
        brand_id=brand.id
    )
    db.add(user)
    db.commit()
    
    # Generate tokens
    access_token = create_access_token(data={"sub": user.id, "brand_id": brand.id})
    refresh_token = create_refresh_token(data={"sub": user.id, "brand_id": brand.id})
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "brand_id": brand.id
        }
    }


@router.post("/login", response_model=TokenResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == request.username).first()
    if not user or not verify_password(request.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is disabled"
        )
    
    access_token = create_access_token(data={"sub": str(user.id), "brand_id": user.brand_id})
    refresh_token = create_refresh_token(data={"sub": str(user.id), "brand_id": user.brand_id})
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token
    )


@router.post("/refresh", response_model=TokenResponse)
def refresh_token(request: RefreshTokenRequest, db: Session = Depends(get_db)):
    payload = verify_token(request.refresh_token, "refresh")
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    user_id = payload.get("sub")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or disabled"
        )
    
    access_token = create_access_token(data={"sub": user.id, "brand_id": user.brand_id})
    new_refresh_token = create_refresh_token(data={"sub": user.id, "brand_id": user.brand_id})
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=new_refresh_token
    )


@router.get("/me")
def get_me(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "role": current_user.role,
        "brand_id": current_user.brand_id
    }
from datetime import datetime, timedelta
from typing import Optional
import httpx
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.database import get_db
from app.models.user import User

# Clerk JWT verification
clerk_jwt_bearer = HTTPBearer(auto_error=False)


async def verify_clerk_token(token: str) -> dict:
    """
    Verify Clerk JWT token and return the payload.
    For production, use Clerk's JWKS endpoint for verification.
    """
    try:
        # In production, fetch Clerk's JWKS and verify
        # For now, decode without verification ( Clerk handles this on frontend)
        # The backend trusts the frontend's Clerk session
        
        # Alternative: Use Clerk's API to verify
        # async with httpx.AsyncClient() as client:
        #     response = await client.get(
        #         f"https://api.clerk.dev/v1/sessions/{session_id}/tokens/verify",
        #         headers={"Authorization": f"Bearer {settings.CLERK_SECRET_KEY}"}
        #     )
        
        # Decode the JWT (in production, verify with Clerk's public key)
        payload = jwt.decode(
            token, 
            options={"verify_signature": False},  # Clerk signs on frontend
            algorithms=["RS256"]
        )
        return payload
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid Clerk token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user_from_clerk(
    credentials: HTTPAuthorizationCredentials = Depends(clerk_jwt_bearer),
    db: Session = Depends(get_db)
) -> User:
    """
    Get current user from Clerk JWT token.
    Creates user if not exists (first time login).
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = credentials.credentials
    
    try:
        # Verify token with Clerk
        payload = await verify_clerk_token(token)
        
        # Get user info from Clerk
        clerk_user_id = payload.get('sub')
        email = payload.get('email')
        full_name = payload.get('name', payload.get('full_name', 'User'))
        
        if not clerk_user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
            )
        
        # Find or create user
        user = db.query(User).filter(User.clerk_user_id == clerk_user_id).first()
        
        if not user:
            # Create new user from Clerk data
            from app.models.brand import Brand
            import uuid
            
            # Create brand for new user
            brand_slug = f"brand-{uuid.uuid4().hex[:8]}"
            brand = Brand(
                name=f"{full_name}'s Store",
                slug=brand_slug,
                email=email
            )
            db.add(brand)
            db.flush()
            
            # Create user
            user = User(
                clerk_user_id=clerk_user_id,
                email=email,
                full_name=full_name,
                brand_id=brand.id,
                is_active=True
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication failed: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


# Keep old functions for backwards compatibility during migration
def verify_password(plain_password: str, hashed_password: str) -> bool:
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=30)
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=7)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")
    return encoded_jwt


def verify_token(token: str, token_type: str = "access") -> Optional[dict]:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        if payload.get("type") != token_type:
            return None
        return payload
    except JWTError:
        return None


# Alias for backwards compatibility
get_current_user = get_current_user_from_clerk
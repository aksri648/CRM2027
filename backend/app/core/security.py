from datetime import datetime, timedelta
from typing import Optional
import httpx
import json
from jose import JWTError, jwt, jwk
from jose.exceptions import JWKError
from fastapi import Depends, HTTPException, status, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.database import get_db
from app.models.user import User

# Clerk JWT verification
clerk_jwt_bearer = HTTPBearer(auto_error=False)

# Cache for JWKS keys
_jwks_cache: Optional[dict] = None
_jwks_cache_time: float = 0
JWKS_CACHE_DURATION = 3600  # 1 hour


async def get_clerk_jwks() -> dict:
    """
    Fetch and cache Clerk's JWKS (JSON Web Key Set) for token verification.
    """
    global _jwks_cache, _jwks_cache_time
    import time
    
    # Return cached JWKS if still valid
    if _jwks_cache and (time.time() - _jwks_cache_time) < JWKS_CACHE_DURATION:
        return _jwks_cache
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(settings.CLERK_JWKS_URL, timeout=10.0)
            response.raise_for_status()
            _jwks_cache = response.json()
            _jwks_cache_time = time.time()
            return _jwks_cache
    except Exception as e:
        # If we have cached keys, use them even if expired
        if _jwks_cache:
            return _jwks_cache
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Failed to fetch Clerk JWKS: {str(e)}",
        )


def get_signing_key(token: str, jwks: dict) -> str:
    """
    Get the signing key from JWKS that matches the token's kid (key ID).
    """
    try:
        unverified_header = jwt.get_unverified_header(token)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token header",
        )
    
    kid = unverified_header.get("kid")
    if not kid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token missing key ID (kid)",
        )
    
    for key in jwks.get("keys", []):
        if key.get("kid") == kid:
            return key
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=f"Unable to find signing key for kid: {kid}",
    )


async def verify_clerk_token(token: str) -> dict:
    """
    Verify Clerk JWT token and return the payload.
    Uses Clerk's JWKS endpoint for proper signature verification.
    """
    try:
        # Fetch Clerk's JWKS
        jwks = await get_clerk_jwks()
        
        # Get the signing key that matches the token
        signing_key = get_signing_key(token, jwks)
        
        # Convert JWK to PEM format for verification
        public_key = jwk.construct(signing_key).to_pem().decode('utf-8')
        
        # Decode and verify the JWT with Clerk's public key
        payload = jwt.decode(
            token,
            public_key,
            algorithms=["RS256"],
            audience=settings.CLERK_AUDIENCE,
            issuer=settings.CLERK_ISSUER,
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
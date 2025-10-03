"""
Authentication and authorization system using API keys and JWT tokens.

Security Features:
- API key-based authentication for scraper endpoint
- JWT tokens for user sessions (future expansion)
- Password hashing with bcrypt
- Configurable via environment variables
"""
from __future__ import annotations

import os
import secrets
from datetime import datetime, timedelta
from typing import Optional

from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader, HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

# Configuration from environment
SECRET_KEY = os.getenv("SECRET_KEY", secrets.token_urlsafe(32))
API_KEY = os.getenv("API_KEY", "your-api-key-here-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Security schemes
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)
bearer_scheme = HTTPBearer(auto_error=False)


def verify_api_key(api_key: str = Security(api_key_header)) -> str:
    """
    Verify API key for protected endpoints.

    Raises:
        HTTPException: If API key is invalid or missing.
    """
    if api_key != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    return api_key


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> dict:
    """Verify JWT token and return payload."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def generate_api_key() -> str:
    """Generate a secure random API key."""
    return secrets.token_urlsafe(32)

"""Pydantic schemas for authentication."""
from typing import Any, Dict, Optional
from pydantic import BaseModel

class Token(BaseModel):
    """Schema for JWT token response."""
    access_token: str
    token_type: str = "bearer"
    user: Dict[str, Any]

class UserCreate(BaseModel):
    """Schema for user creation."""
    email: str
    password: str
    user_metadata: Optional[Dict[str, Any]] = None

class UserLogin(BaseModel):
    """Schema for user login."""
    email: str
    password: str

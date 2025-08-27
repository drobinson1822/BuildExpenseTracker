"""Centralized authentication dependencies for the API."""
from typing import Dict, Any
import logging
from fastapi import HTTPException, status, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from api.core.supabase import supabase

# Security configuration
security = HTTPBearer()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def get_current_active_user(authorization: HTTPAuthorizationCredentials = Security(security)) -> Dict[str, Any]:
    """
    Centralized dependency to get the current authenticated user using Supabase JWT.
    
    This function:
    1. Extracts the JWT token from the Authorization header
    2. Validates it with Supabase auth
    3. Returns user info including id, email, role
    
    Used by all protected endpoints to ensure consistent authentication.
    """
    try:
        token = authorization.credentials
        user = supabase.auth.get_user(token)
        
        if not user.user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return {
            'id': user.user.id,
            'email': user.user.email,
            'role': user.user.role or 'user',
            'token': token
        }
    except Exception as e:
        logger.error(f"Authentication error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

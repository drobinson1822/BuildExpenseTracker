from supabase import create_client, Client
import os
from dotenv import load_dotenv
from typing import Optional, Dict, Any, Union
from fastapi import HTTPException, status, Header
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

class SupabaseService:
    """
    Service class for Supabase operations using the secret key.
    This should be used for all server-side operations.
    """
    _instance: Optional[Client] = None
    
    @classmethod
    def get_client(cls) -> Client:
        """Get the Supabase client with secret key"""
        if cls._instance is None:
            url = os.getenv("SUPABASE_URL")
            secret_key = os.getenv("SUPABASE_SECRET_KEY")
            if not url or not secret_key:
                raise ValueError("SUPABASE_URL and SUPABASE_SECRET_KEY must be set in .env")
            cls._instance = create_client(url, secret_key)
        return cls._instance

# Create singleton instance
supabase = SupabaseService.get_client()

# Alias for backward compatibility
supabase_admin = supabase

async def get_current_user(authorization: str = Header(...)) -> Dict[str, Any]:
    """
    Verify and get the current user from the JWT token.
    This should be used as a dependency in protected routes.
    """
    try:
        # Extract token from Authorization header
        if not authorization.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication scheme"
            )
        
        token = authorization.split(" ")[1]
        
        # Verify the token using the Supabase client
        try:
            # This will verify the token and get the user
            user = supabase.auth.get_user(token)
            if not user or not user.user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authentication token"
                )
            return user.user.dict()
            
        except Exception as e:
            logger.error(f"Error verifying token: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials"
            )
            
    except Exception as e:
        logger.error(f"Authentication error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )

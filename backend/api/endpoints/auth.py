"""Authentication endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from typing import Dict, Any
import logging
from api.core.supabase import get_current_user, supabase, supabase_admin
from api.schemas.auth import Token, UserCreate, UserLogin

# Security configuration
security = HTTPBearer()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

async def get_current_user_http(authorization: HTTPAuthorizationCredentials = Security(security)) -> Dict[str, Any]:
    """
    Get current user from Authorization header using Supabase's JWT
    """
    try:
        token = authorization.credentials
        # Use Supabase's built-in JWT verification
        user = supabase.auth.get_user(token)
        return {
            'id': user.user.id,
            'email': user.user.email,
            'role': user.user.role,
            'token': token
        }
    except Exception as e:
        logging.error(f"Authentication error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_current_active_user(authorization: HTTPAuthorizationCredentials = Security(security)) -> Dict[str, Any]:
    """Dependency to get the current authenticated user using Supabase JWT"""
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

@router.post("/register", response_model=Dict[str, Any])
async def register(user: UserCreate):
    """Register a new user"""
    logger.info(f"Attempting to register user with email: {user.email}")
    
    try:
        # Check if user already exists in Supabase
        existing_user = supabase.auth.admin.get_user_by_email(user.email)
        if existing_user.user:
            logger.warning(f"Registration failed - User already exists: {user.email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
            
        # Create user in Supabase
        auth_response = supabase.auth.admin.create_user({
            "email": user.email,
            "password": user.password,
            "email_confirm": True,  # Skip email confirmation for POC
            "user_metadata": user.user_metadata or {}
        })
        
        logger.info(f"User created in Supabase: {user.email}")
        return {"message": "User created successfully", "email": user.email}
    except Exception as e:
        error_msg = f"Registration error: {str(e)}"
        logger.error(error_msg, exc_info=True)  # Include full traceback
        
        # Extract more detailed error message if available
        detail = str(e)
        if hasattr(e, 'message') and e.message:
            detail = e.message
        elif hasattr(e, 'args') and e.args:
            detail = e.args[0] if isinstance(e.args[0], str) else str(e)
            
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail or "Registration failed. Please check your input and try again."
        )

@router.post("/login", response_model=Dict[str, Any])
async def login(credentials: UserLogin):
    """Login user and return access token"""
    logger.info(f"Login attempt for user: {credentials.email}")
    
    try:
        # Authenticate with Supabase
        auth_response = supabase.auth.sign_in_with_password({
            "email": credentials.email,
            "password": credentials.password
        })
        
        if not auth_response.user:
            logger.warning(f"Login failed for user: {credentials.email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        logger.info(f"User logged in successfully: {credentials.email}")
        return {
            "access_token": auth_response.session.access_token,
            "token_type": "bearer",
            "refresh_token": auth_response.session.refresh_token,
            "user": {
                "id": auth_response.user.id,
                "email": auth_response.user.email,
                "role": auth_response.user.role or "user"
            }
        }
    except Exception as e:
        error_msg = f"Login error for {credentials.email}: {str(e)}"
        logger.error(error_msg, exc_info=True)
        
        # Extract more detailed error message if available
        detail = str(e)
        if hasattr(e, 'message') and e.message:
            detail = e.message
        elif hasattr(e, 'args') and e.args:
            detail = e.args[0] if isinstance(e.args[0], str) else str(e)
            
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail or "Login failed. Please check your credentials."
        )

@router.post("/refresh", response_model=Dict[str, Any])
async def refresh_token(refresh_token: str):
    """Refresh access token"""
    logger.info("Token refresh attempt")
    
    try:
        # Refresh token with Supabase
        auth_response = supabase.auth.refresh_session(refresh_token)
        
        if not auth_response.session:
            logger.warning("Token refresh failed - invalid refresh token")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        logger.info("Token refreshed successfully")
        return {
            "access_token": auth_response.session.access_token,
            "token_type": "bearer",
            "refresh_token": auth_response.session.refresh_token
        }
    except Exception as e:
        error_msg = f"Token refresh error: {str(e)}"
        logger.error(error_msg, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Failed to refresh token"
        )

@router.post("/logout")
async def logout():
    """Logout user"""
    logger.info("User logout")
    
    try:
        # Sign out from Supabase
        supabase.auth.sign_out()
        logger.info("User logged out successfully")
        return {"message": "Successfully logged out"}
    except Exception as e:
        error_msg = f"Logout error: {str(e)}"
        logger.error(error_msg, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout failed"
        )

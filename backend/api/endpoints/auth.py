"""Authentication endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status, Header
from typing import Dict, Any, Optional
import logging
from api.core.supabase import supabase, supabase_admin
from api.schemas.auth import Token, UserCreate, UserLogin

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/register", response_model=Dict[str, Any])
async def register(user: UserCreate):
    """Register a new user and return tokens (auto-login)."""
    logger.info(f"Attempting to register user with email: {user.email}")

    try:
        # Use public sign_up to avoid admin privileges requirement
        metadata = user.user_metadata or {}
        if user.full_name:
            metadata["full_name"] = user.full_name
            
        supabase.auth.sign_up({
            "email": user.email,
            "password": user.password,
            "options": {
                "data": metadata
            }
        })

        # Immediately sign in to return tokens for MVP UX
        auth_response = supabase.auth.sign_in_with_password({
            "email": user.email,
            "password": user.password
        })

        if not auth_response.user or not auth_response.session:
            logger.warning(f"Auto login after register failed for: {user.email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Registration succeeded but auto login failed"
            )

        logger.info(f"User registered and logged in: {user.email}")
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

@router.get("/me", response_model=Dict[str, Any])
async def get_current_user(authorization: Optional[str] = Header(None)):
    """Get current user information from JWT token"""
    logger.info("Get current user request")
    
    if not authorization or not authorization.startswith("Bearer "):
        logger.warning("No authorization header found")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header required"
        )
    
    try:
        # Extract JWT token from Authorization header
        jwt_token = authorization.split(" ")[1]
        
        # Verify JWT token with Supabase
        user_response = supabase.auth.get_user(jwt_token)
        
        if not user_response or not user_response.user:
            logger.warning("Invalid or expired token")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token"
            )
        
        logger.info(f"Current user retrieved: {user_response.user.email}")
        return {
            "id": user_response.user.id,
            "email": user_response.user.email,
            "role": getattr(user_response.user, 'role', 'user')
        }
    except Exception as e:
        error_msg = f"Get current user error: {str(e)}"
        logger.error(error_msg, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Failed to authenticate user"
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

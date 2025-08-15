"""Draw tracker endpoints for the Construction Cost Tracker API."""
from typing import List, Dict, Any
import logging

from fastapi import APIRouter, Depends, HTTPException, status, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from api.core.database import get_db
from api.models.draw import DrawTracker
from api.schemas.draw import DrawTrackerCreate, DrawTrackerOut
from api.core.supabase import supabase

# Security configuration
security = HTTPBearer()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

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

@router.post("/", response_model=DrawTrackerOut)
def create_draw(
    draw: DrawTrackerCreate, 
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """Create a new draw tracker"""
    try:
        db_draw = DrawTracker(**draw.model_dump())
        db.add(db_draw)
        db.commit()
        db.refresh(db_draw)
        return db_draw
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating draw: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create draw"
        )

@router.get("/", response_model=List[DrawTrackerOut])
def list_draws(
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """List all draw trackers"""
    try:
        return db.query(DrawTracker).all()
    except Exception as e:
        logger.error(f"Error listing draws: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve draws"
        )

@router.get("/{draw_id}", response_model=DrawTrackerOut)
def get_draw(
    draw_id: int, 
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """Get a specific draw tracker by ID"""
    try:
        draw = db.query(DrawTracker).filter(DrawTracker.id == draw_id).first()
        if not draw:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Draw not found"
            )
        return draw
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting draw: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve draw"
        )

@router.put("/{draw_id}", response_model=DrawTrackerOut)
def update_draw(
    draw_id: int, 
    draw: DrawTrackerCreate, 
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """Update a draw tracker"""
    try:
        db_draw = db.query(DrawTracker).filter(DrawTracker.id == draw_id).first()
        if not db_draw:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Draw not found"
            )
        
        for key, value in draw.model_dump().items():
            setattr(db_draw, key, value)
        
        db.commit()
        db.refresh(db_draw)
        return db_draw
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating draw: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update draw"
        )

@router.delete("/{draw_id}")
def delete_draw(
    draw_id: int, 
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """Delete a draw tracker"""
    try:
        db_draw = db.query(DrawTracker).filter(DrawTracker.id == draw_id).first()
        if not db_draw:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Draw not found"
            )
        
        db.delete(db_draw)
        db.commit()
        return {"deleted": True}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting draw: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete draw"
        )

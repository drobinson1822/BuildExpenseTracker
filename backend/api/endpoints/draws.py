"""Draw tracker endpoints for the Construction Cost Tracker API."""
from typing import List, Dict, Any
import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from api.core.database import get_db
from api.models.draw import DrawTracker
from api.schemas.draw import DrawTrackerCreate, DrawTrackerOut
from api.core.supabase import supabase
from api.core.auth import get_current_active_user

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/", response_model=DrawTrackerOut)
def create_draw(
    draw: DrawTrackerCreate, 
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """Create a new draw tracker"""
    try:
        draw_data = draw.model_dump()
        draw_data['user_id'] = current_user['id']
        
        # Convert date to string for Supabase
        if 'last_draw_date' in draw_data and draw_data['last_draw_date']:
            draw_data['last_draw_date'] = str(draw_data['last_draw_date'])
        
        response = supabase.table('draw_tracker').insert(draw_data).execute()
        if not response.data:
            raise Exception("Failed to create draw in Supabase")
        
        return response.data[0]
    except Exception as e:
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
        response = supabase.table('draw_tracker')\
            .select('*')\
            .eq('user_id', current_user['id'])\
            .execute()
        
        return response.data
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
        response = supabase.table('draw_tracker')\
            .select('*')\
            .eq('id', draw_id)\
            .eq('user_id', current_user['id'])\
            .execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Draw not found"
            )
        
        return response.data[0]
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
        # First check if draw exists and belongs to user
        existing = supabase.table('draw_tracker')\
            .select('id')\
            .eq('id', draw_id)\
            .eq('user_id', current_user['id'])\
            .execute()
        
        if not existing.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Draw not found"
            )
        
        # Update the draw
        draw_data = draw.model_dump()
        response = supabase.table('draw_tracker')\
            .update(draw_data)\
            .eq('id', draw_id)\
            .eq('user_id', current_user['id'])\
            .execute()
        
        if not response.data:
            raise Exception("Failed to update draw")
        
        return response.data[0]
    except HTTPException:
        raise
    except Exception as e:
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
        # First check if draw exists and belongs to user
        existing = supabase.table('draw_tracker')\
            .select('id')\
            .eq('id', draw_id)\
            .eq('user_id', current_user['id'])\
            .execute()
        
        if not existing.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Draw not found"
            )
        
        # Delete the draw
        response = supabase.table('draw_tracker')\
            .delete()\
            .eq('id', draw_id)\
            .eq('user_id', current_user['id'])\
            .execute()
        
        return {"deleted": True}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting draw: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete draw"
        )

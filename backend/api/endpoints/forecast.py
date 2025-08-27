"""Forecast line item endpoints for the Construction Cost Tracker API."""
from typing import List, Dict, Any
import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from api.core.database import get_db
from api.models.forecast import ForecastLineItem
from api.schemas.forecast import ForecastLineItemCreate, ForecastLineItemOut
from api.core.supabase import supabase
from api.core.auth import get_current_active_user

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/", response_model=ForecastLineItemOut)
def create_forecast_item(
    item: ForecastLineItemCreate, 
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """Create a new forecast line item"""
    try:
        item_data = item.model_dump()
        item_data['user_id'] = current_user['id']
        
        response = supabase.table('forecast_line_items').insert(item_data).execute()
        if not response.data:
            raise Exception("Failed to create forecast item in Supabase")
        
        return response.data[0]
    except Exception as e:
        logger.error(f"Error creating forecast item: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create forecast item"
        )

@router.get("/", response_model=List[ForecastLineItemOut])
def list_forecast_items(
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """List all forecast line items"""
    try:
        response = supabase.table('forecast_line_items')\
            .select('*')\
            .eq('user_id', current_user['id'])\
            .execute()
        
        return response.data
    except Exception as e:
        logger.error(f"Error listing forecast items: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve forecast items"
        )

@router.get("/{item_id}", response_model=ForecastLineItemOut)
def get_forecast_item(
    item_id: int, 
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """Get a specific forecast line item by ID"""
    try:
        response = supabase.table('forecast_line_items')\
            .select('*')\
            .eq('id', item_id)\
            .eq('user_id', current_user['id'])\
            .execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Forecast item not found"
            )
        
        return response.data[0]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting forecast item: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve forecast item"
        )

@router.put("/{item_id}", response_model=ForecastLineItemOut)
def update_forecast_item(
    item_id: int, 
    item: ForecastLineItemCreate, 
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """Update a forecast line item"""
    try:
        # First check if item exists and belongs to user
        existing = supabase.table('forecast_line_items')\
            .select('id')\
            .eq('id', item_id)\
            .eq('user_id', current_user['id'])\
            .execute()
        
        if not existing.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Forecast item not found"
            )
        
        # Update the item
        item_data = item.model_dump()
        response = supabase.table('forecast_line_items')\
            .update(item_data)\
            .eq('id', item_id)\
            .eq('user_id', current_user['id'])\
            .execute()
        
        if not response.data:
            raise Exception("Failed to update forecast item")
        
        return response.data[0]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating forecast item: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update forecast item"
        )

@router.delete("/{item_id}")
def delete_forecast_item(
    item_id: int, 
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """Delete a forecast line item"""
    try:
        # First check if item exists and belongs to user
        existing = supabase.table('forecast_line_items')\
            .select('id')\
            .eq('id', item_id)\
            .eq('user_id', current_user['id'])\
            .execute()
        
        if not existing.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Forecast item not found"
            )
        
        # Delete the item
        response = supabase.table('forecast_line_items')\
            .delete()\
            .eq('id', item_id)\
            .eq('user_id', current_user['id'])\
            .execute()
        
        return {"deleted": True}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting forecast item: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete forecast item"
        )

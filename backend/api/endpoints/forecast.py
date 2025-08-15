"""Forecast line item endpoints for the Construction Cost Tracker API."""
from typing import List, Dict, Any
import logging

from fastapi import APIRouter, Depends, HTTPException, status, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from api.core.database import get_db
from api.models.forecast import ForecastLineItem
from api.schemas.forecast import ForecastLineItemCreate, ForecastLineItemOut
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

@router.post("/", response_model=ForecastLineItemOut)
def create_forecast_item(
    item: ForecastLineItemCreate, 
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """Create a new forecast line item"""
    try:
        db_item = ForecastLineItem(**item.model_dump())
        db.add(db_item)
        db.commit()
        db.refresh(db_item)
        return db_item
    except Exception as e:
        db.rollback()
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
        return db.query(ForecastLineItem).all()
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
        item = db.query(ForecastLineItem).filter(ForecastLineItem.id == item_id).first()
        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Forecast item not found"
            )
        return item
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
        db_item = db.query(ForecastLineItem).filter(ForecastLineItem.id == item_id).first()
        if not db_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Forecast item not found"
            )
        
        for key, value in item.model_dump().items():
            setattr(db_item, key, value)
        
        db.commit()
        db.refresh(db_item)
        return db_item
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
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
        db_item = db.query(ForecastLineItem).filter(ForecastLineItem.id == item_id).first()
        if not db_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Forecast item not found"
            )
        
        db.delete(db_item)
        db.commit()
        return {"deleted": True}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting forecast item: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete forecast item"
        )

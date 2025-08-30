"""Pydantic schemas for forecast line items."""
from typing import Optional
from pydantic import BaseModel

class ForecastLineItemBase(BaseModel):
    """Base forecast line item schema."""
    project_id: int
    category: str
    description: Optional[str] = None
    estimated_cost: float
    actual_cost: Optional[float] = 0.0
    unit: Optional[str] = None
    notes: Optional[str] = None
    progress_percent: int = 0
    status: Optional[str] = "not_started"

class ForecastLineItemCreate(ForecastLineItemBase):
    """Schema for creating a new forecast line item."""
    
    class Config:
        # Allow extra fields to be ignored if they don't exist in DB yet
        extra = "ignore"

class ForecastLineItemOut(ForecastLineItemBase):
    """Schema for forecast line item responses."""
    id: int

    class Config:
        from_attributes = True

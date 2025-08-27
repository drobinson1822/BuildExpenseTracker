"""Pydantic schemas for forecast line items."""
from typing import Optional
from pydantic import BaseModel

class ForecastLineItemBase(BaseModel):
    """Base forecast line item schema."""
    project_id: int
    category: str
    estimated_cost: float
    unit: Optional[str] = None
    notes: Optional[str] = None
    progress_percent: int = 0
    status: Optional[str] = "not_started"

class ForecastLineItemCreate(ForecastLineItemBase):
    """Schema for creating a new forecast line item."""
    pass

class ForecastLineItemOut(ForecastLineItemBase):
    """Schema for forecast line item responses."""
    id: int

    class Config:
        from_attributes = True

"""Pydantic schemas for actual expenses."""
from datetime import date
from typing import Optional
from pydantic import BaseModel

class ActualExpenseBase(BaseModel):
    """Base actual expense schema."""
    project_id: int
    forecast_line_item_id: Optional[int] = None
    vendor: Optional[str] = None
    amount_spent: float
    date: date
    receipt_url: Optional[str] = None

class ActualExpenseCreate(ActualExpenseBase):
    """Schema for creating a new actual expense."""
    pass

class ActualExpenseOut(ActualExpenseBase):
    """Schema for actual expense responses."""
    id: int

    class Config:
        from_attributes = True

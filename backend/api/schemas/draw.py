"""Pydantic schemas for draw tracker."""
from datetime import date
from typing import Optional
from pydantic import BaseModel

class DrawTrackerBase(BaseModel):
    """Base draw tracker schema."""
    project_id: int
    cash_on_hand: float
    last_draw_date: Optional[date] = None
    draw_triggered: Optional[bool] = False
    notes: Optional[str] = None

class DrawTrackerCreate(DrawTrackerBase):
    """Schema for creating a new draw tracker."""
    pass

class DrawTrackerOut(DrawTrackerBase):
    """Schema for draw tracker responses."""
    id: int

    class Config:
        from_attributes = True

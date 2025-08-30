"""Pydantic schemas for projects."""
from datetime import date
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator
from decimal import Decimal
from enum import Enum

class ProjectStatusEnum(str, Enum):
    not_started = "not_started"
    in_progress = "in_progress"
    completed = "completed"

class ProjectBase(BaseModel):
    """Base project schema."""
    name: str
    address: Optional[str] = None
    start_date: Optional[date] = None
    target_completion_date: Optional[date] = None
    status: Optional[ProjectStatusEnum] = ProjectStatusEnum.not_started
    total_sqft: Optional[int] = None
    total_budget: Optional[Decimal] = None

class ProjectCreate(ProjectBase):
    """Schema for creating a new project."""
    pass

class ProjectUpdate(BaseModel):
    """Schema for updating a project (all fields are optional)."""
    name: Optional[str] = None
    address: Optional[str] = None
    start_date: Optional[date] = None
    target_completion_date: Optional[date] = None
    status: Optional[ProjectStatusEnum] = None
    total_sqft: Optional[int] = None
    total_budget: Optional[Decimal] = None

class ProjectOut(ProjectBase):
    """Schema for project responses."""
    id: int

    class Config:
        from_attributes = True

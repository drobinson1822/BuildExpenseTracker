"""Forecast line item model and related enums."""

from sqlalchemy import Column, Integer, String, Float, ForeignKey, Enum, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum
from .base import Base

class ForecastStatusEnum(str, enum.Enum):
    """Enumeration for forecast line item status values."""
    not_started = "Not Started"
    in_progress = "In Progress"
    complete = "Complete"

class ForecastLineItem(Base):
    """Forecast line item model representing budget items for a project."""
    __tablename__ = "forecast_line_items"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    category = Column(String, nullable=False)
    description = Column(Text)  # Brief description of the line item
    estimated_cost = Column(Float, nullable=False)
    actual_cost = Column(Float, default=0.0)
    unit = Column(String)
    notes = Column(Text)  # Additional notes/comments
    progress_percent = Column(Integer, default=0)
    status = Column(Enum(ForecastStatusEnum), default=ForecastStatusEnum.not_started)
    
    # Relationships
    project = relationship("Project", back_populates="forecast_items")
    expenses = relationship("ActualExpense", back_populates="forecast_item")

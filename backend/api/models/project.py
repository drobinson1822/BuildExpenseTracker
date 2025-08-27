"""Project model and related enums."""

from sqlalchemy import Column, Integer, String, Date, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum
from .base import Base

class ProjectStatusEnum(str, enum.Enum):
    """Enumeration for project status values."""
    not_started = "not_started"
    in_progress = "in_progress"
    completed = "completed"

class Project(Base):
    """Project model representing a construction project."""
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    name = Column(String, nullable=False)
    address = Column(String)
    start_date = Column(Date)
    target_completion_date = Column(Date)
    status = Column(Enum(ProjectStatusEnum), default=ProjectStatusEnum.not_started)
    total_sqft = Column(Integer)
    
    # Relationships
    forecast_items = relationship("ForecastLineItem", back_populates="project")
    expenses = relationship("ActualExpense", back_populates="project")
    draws = relationship("DrawTracker", back_populates="project")

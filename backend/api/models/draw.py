"""Draw tracker model."""

from sqlalchemy import Column, Integer, Float, Date, ForeignKey, Boolean, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .base import Base

class DrawTracker(Base):
    """Draw tracker model for managing construction draws and cash flow."""
    __tablename__ = "draw_tracker"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    cash_on_hand = Column(Float, nullable=False)
    last_draw_date = Column(Date)
    draw_triggered = Column(Boolean, default=False)
    notes = Column(Text)
    
    # Relationships
    project = relationship("Project", back_populates="draws")

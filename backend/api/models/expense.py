"""Actual expense model."""

from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base

class ActualExpense(Base):
    """Actual expense model representing real expenses for a project."""
    __tablename__ = "actual_expenses"
    
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    forecast_line_item_id = Column(Integer, ForeignKey("forecast_line_items.id"), nullable=True)
    vendor = Column(String)
    amount_spent = Column(Float, nullable=False)
    date = Column(Date)
    receipt_url = Column(String)
    
    # Relationships
    project = relationship("Project", back_populates="expenses")
    forecast_item = relationship("ForecastLineItem", back_populates="expenses")

from sqlalchemy import Column, Integer, String, Date, Float, ForeignKey, Enum, Boolean, Text
from sqlalchemy.orm import declarative_base, relationship
import enum

Base = declarative_base()

class ProjectStatusEnum(str, enum.Enum):
    not_started = "not_started"
    in_progress = "in_progress"
    completed = "completed"

class Project(Base):
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    address = Column(String)
    start_date = Column(Date)
    target_completion_date = Column(Date)
    status = Column(Enum(ProjectStatusEnum), default=ProjectStatusEnum.not_started)
    total_sqft = Column(Integer)
    forecast_items = relationship("ForecastLineItem", back_populates="project")
    expenses = relationship("ActualExpense", back_populates="project")
    draws = relationship("DrawTracker", back_populates="project")

class ForecastStatusEnum(str, enum.Enum):
    not_started = "Not Started"
    in_progress = "In Progress"
    complete = "Complete"

class ForecastLineItem(Base):
    __tablename__ = "forecast_line_items"
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    category = Column(String, nullable=False)
    estimated_cost = Column(Float, nullable=False)
    unit = Column(String)
    notes = Column(Text)
    progress_percent = Column(Integer, default=0)
    status = Column(Enum(ForecastStatusEnum), default=ForecastStatusEnum.not_started)
    project = relationship("Project", back_populates="forecast_items")
    expenses = relationship("ActualExpense", back_populates="forecast_item")

class ActualExpense(Base):
    __tablename__ = "actual_expenses"
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    forecast_line_item_id = Column(Integer, ForeignKey("forecast_line_items.id"), nullable=True)
    vendor = Column(String)
    amount_spent = Column(Float, nullable=False)
    date = Column(Date)
    receipt_url = Column(String)
    project = relationship("Project", back_populates="expenses")
    forecast_item = relationship("ForecastLineItem", back_populates="expenses")

class DrawTracker(Base):
    __tablename__ = "draw_tracker"
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    cash_on_hand = Column(Float, nullable=False)
    last_draw_date = Column(Date)
    draw_triggered = Column(Boolean, default=False)
    notes = Column(Text)
    project = relationship("Project", back_populates="draws")

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Project, ForecastLineItem, ActualExpense, DrawTracker, Base
from pydantic import BaseModel
from typing import List, Optional
from datetime import date

# Dependency

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

router = APIRouter(prefix="/api")

# --- Pydantic Schemas ---
class ProjectBase(BaseModel):
    name: str
    address: Optional[str] = None
    start_date: Optional[date] = None
    target_completion_date: Optional[date] = None
    status: Optional[str] = "Planned"
    total_sqft: Optional[int] = None

class ProjectCreate(ProjectBase):
    pass

class ProjectOut(ProjectBase):
    id: int
    model_config = {
        "from_attributes": True
    }

class ForecastLineItemBase(BaseModel):
    project_id: int
    category: str
    estimated_cost: float
    unit: Optional[str] = None
    notes: Optional[str] = None
    progress_percent: int = 0
    status: Optional[str] = "Not Started"

class ForecastLineItemCreate(ForecastLineItemBase):
    pass

class ForecastLineItemOut(ForecastLineItemBase):
    id: int
    model_config = {
        "from_attributes": True
    }

class ActualExpenseBase(BaseModel):
    project_id: int
    forecast_line_item_id: Optional[int] = None
    vendor: Optional[str] = None
    amount_spent: float
    date: date
    receipt_url: Optional[str] = None

class ActualExpenseCreate(ActualExpenseBase):
    pass

class ActualExpenseOut(ActualExpenseBase):
    id: int
    model_config = {
        "from_attributes": True
    }

class DrawTrackerBase(BaseModel):
    project_id: int
    cash_on_hand: float
    last_draw_date: Optional[date] = None
    draw_triggered: Optional[bool] = False
    notes: Optional[str] = None

class DrawTrackerCreate(DrawTrackerBase):
    pass

class DrawTrackerOut(DrawTrackerBase):
    id: int
    model_config = {
        "from_attributes": True
    }

# --- Project CRUD ---
@router.post("/projects/", response_model=ProjectOut)
def create_project(project: ProjectCreate, db: Session = Depends(get_db)):
    db_project = Project(**project.model_dump())
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project

@router.get("/projects/", response_model=List[ProjectOut])
def list_projects(db: Session = Depends(get_db)):
    return db.query(Project).all()

@router.get("/projects/{project_id}", response_model=ProjectOut)
def get_project(project_id: int, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@router.put("/projects/{project_id}", response_model=ProjectOut)
def update_project(project_id: int, project: ProjectCreate, db: Session = Depends(get_db)):
    db_project = db.query(Project).filter(Project.id == project_id).first()
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
    for key, value in project.model_dump().items():
        setattr(db_project, key, value)
    db.commit()
    db.refresh(db_project)
    return db_project

@router.delete("/projects/{project_id}")
def delete_project(project_id: int, db: Session = Depends(get_db)):
    db_project = db.query(Project).filter(Project.id == project_id).first()
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
    db.delete(db_project)
    db.commit()
    return {"deleted": True}

# --- ForecastLineItem CRUD ---
@router.post("/forecast-items/", response_model=ForecastLineItemOut)
def create_forecast_item(item: ForecastLineItemCreate, db: Session = Depends(get_db)):
    db_item = ForecastLineItem(**item.model_dump())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@router.get("/forecast-items/", response_model=List[ForecastLineItemOut])
def list_forecast_items(db: Session = Depends(get_db)):
    return db.query(ForecastLineItem).all()

@router.get("/forecast-items/{item_id}", response_model=ForecastLineItemOut)
def get_forecast_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(ForecastLineItem).filter(ForecastLineItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Forecast item not found")
    return item

@router.put("/forecast-items/{item_id}", response_model=ForecastLineItemOut)
def update_forecast_item(item_id: int, item: ForecastLineItemCreate, db: Session = Depends(get_db)):
    db_item = db.query(ForecastLineItem).filter(ForecastLineItem.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Forecast item not found")
    for key, value in item.model_dump().items():
        setattr(db_item, key, value)
    db.commit()
    db.refresh(db_item)
    return db_item

@router.delete("/forecast-items/{item_id}")
def delete_forecast_item(item_id: int, db: Session = Depends(get_db)):
    db_item = db.query(ForecastLineItem).filter(ForecastLineItem.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Forecast item not found")
    db.delete(db_item)
    db.commit()
    return {"deleted": True}

# --- ActualExpense CRUD ---
@router.post("/expenses/", response_model=ActualExpenseOut)
def create_expense(expense: ActualExpenseCreate, db: Session = Depends(get_db)):
    db_expense = ActualExpense(**expense.model_dump())
    db.add(db_expense)
    db.commit()
    db.refresh(db_expense)
    return db_expense

@router.get("/expenses/", response_model=List[ActualExpenseOut])
def list_expenses(db: Session = Depends(get_db)):
    return db.query(ActualExpense).all()

@router.get("/expenses/{expense_id}", response_model=ActualExpenseOut)
def get_expense(expense_id: int, db: Session = Depends(get_db)):
    expense = db.query(ActualExpense).filter(ActualExpense.id == expense_id).first()
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    return expense

@router.put("/expenses/{expense_id}", response_model=ActualExpenseOut)
def update_expense(expense_id: int, expense: ActualExpenseCreate, db: Session = Depends(get_db)):
    db_expense = db.query(ActualExpense).filter(ActualExpense.id == expense_id).first()
    if not db_expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    for key, value in expense.model_dump().items():
        setattr(db_expense, key, value)
    db.commit()
    db.refresh(db_expense)
    return db_expense

@router.delete("/expenses/{expense_id}")
def delete_expense(expense_id: int, db: Session = Depends(get_db)):
    db_expense = db.query(ActualExpense).filter(ActualExpense.id == expense_id).first()
    if not db_expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    db.delete(db_expense)
    db.commit()
    return {"deleted": True}

# --- DrawTracker CRUD ---
@router.post("/draws/", response_model=DrawTrackerOut)
def create_draw(draw: DrawTrackerCreate, db: Session = Depends(get_db)):
    db_draw = DrawTracker(**draw.model_dump())
    db.add(db_draw)
    db.commit()
    db.refresh(db_draw)
    return db_draw

@router.get("/draws/", response_model=List[DrawTrackerOut])
def list_draws(db: Session = Depends(get_db)):
    return db.query(DrawTracker).all()

@router.get("/draws/{draw_id}", response_model=DrawTrackerOut)
def get_draw(draw_id: int, db: Session = Depends(get_db)):
    draw = db.query(DrawTracker).filter(DrawTracker.id == draw_id).first()
    if not draw:
        raise HTTPException(status_code=404, detail="Draw not found")
    return draw

@router.put("/draws/{draw_id}", response_model=DrawTrackerOut)
def update_draw(draw_id: int, draw: DrawTrackerCreate, db: Session = Depends(get_db)):
    db_draw = db.query(DrawTracker).filter(DrawTracker.id == draw_id).first()
    if not db_draw:
        raise HTTPException(status_code=404, detail="Draw not found")
    for key, value in draw.model_dump().items():
        setattr(db_draw, key, value)
    db.commit()
    db.refresh(db_draw)
    return db_draw

@router.delete("/draws/{draw_id}")
def delete_draw(draw_id: int, db: Session = Depends(get_db)):
    db_draw = db.query(DrawTracker).filter(DrawTracker.id == draw_id).first()
    if not db_draw:
        raise HTTPException(status_code=404, detail="Draw not found")
    db.delete(db_draw)
    db.commit()
    return {"deleted": True}

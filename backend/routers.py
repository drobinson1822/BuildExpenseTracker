from fastapi import APIRouter, Depends, HTTPException, status, Header, Request, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from database import get_db, Base, SessionLocal
from models import Project, ForecastLineItem, ActualExpense, DrawTracker, ProjectStatusEnum, ForecastStatusEnum
from pydantic import BaseModel, Field, validator, ConfigDict
from typing import List, Optional, Any, Dict
from datetime import date, datetime
import logging
from supabase_client import get_current_user, supabase, supabase_admin
import os

# Security configuration
security = HTTPBearer()

async def get_current_user_http(authorization: HTTPAuthorizationCredentials = Security(security)) -> Dict[str, Any]:
    """
    Get current user from Authorization header using Supabase's JWT
    """
    try:
        token = authorization.credentials
        # Use Supabase's built-in JWT verification
        user = supabase.auth.get_user(token)
        return {
            'id': user.user.id,
            'email': user.user.email,
            'role': user.user.role,
            'token': token
        }
    except Exception as e:
        logging.error(f"Authentication error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize router with tags for better API documentation
router = APIRouter(
    tags=["api"],
    responses={
        401: {"description": "Unauthorized"},
        404: {"description": "Not found"},
        500: {"description": "Internal server error"}
    },
)

# Pydantic models for authentication
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: Dict[str, Any]

class UserCreate(BaseModel):
    email: str  # Changed from EmailStr to str to remove validation
    password: str
    user_metadata: Optional[Dict[str, Any]] = None

class UserLogin(BaseModel):
    email: str  # Changed from EmailStr to str to remove validation
    password: str

# Auth endpoints
@router.post("/auth/register", response_model=Dict[str, Any])
async def register(user: UserCreate):
    """Register a new user"""
    logger.info(f"Attempting to register user with email: {user.email}")
    
    try:
        # Check if user already exists in Supabase
        existing_user = supabase.auth.admin.get_user_by_email(user.email)
        if existing_user.user:
            logger.warning(f"Registration failed - User already exists: {user.email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
            
        # Create user in Supabase
        auth_response = supabase.auth.admin.create_user({
            "email": user.email,
            "password": user.password,
            "email_confirm": True,  # Skip email confirmation for POC
            "user_metadata": user.user_metadata or {}
        })
        
        logger.info(f"User created in Supabase: {user.email}")
        return {"message": "User created successfully", "email": user.email}
    except Exception as e:
        error_msg = f"Registration error: {str(e)}"
        logger.error(error_msg, exc_info=True)  # Include full traceback
        
        # Extract more detailed error message if available
        detail = str(e)
        if hasattr(e, 'message') and e.message:
            detail = e.message
        elif hasattr(e, 'args') and e.args:
            detail = e.args[0] if isinstance(e.args[0], str) else str(e)
            
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail or "Registration failed. Please check your input and try again."
        )

@router.post("/auth/login", response_model=Dict[str, Any])
async def login(credentials: UserLogin):
    """Login user and return access token"""
    try:
        # Authenticate with Supabase
        auth_response = supabase.auth.sign_in_with_password({
            "email": credentials.email,
            "password": credentials.password
        })
        
        if not auth_response.user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
        
        # Get the session
        session = supabase.auth.get_session()
        
        return {
            "access_token": session.access_token,
            "refresh_token": session.refresh_token,
            "token_type": "bearer",
            "user": {
                "id": auth_response.user.id,
                "email": auth_response.user.email,
                "role": auth_response.user.role
            }
        }
        
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )

@router.post("/auth/refresh")
async def refresh_token(refresh_token: str):
    """Refresh access token"""
    try:
        session = supabase.auth.refresh_session(refresh_token)
        return {
            "access_token": session.access_token,
            "refresh_token": session.refresh_token,
            "token_type": "bearer"
        }
    except Exception as e:
        logger.error(f"Token refresh error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

@router.post("/auth/logout")
async def logout():
    """Logout user"""
    try:
        supabase.auth.sign_out()
        return {"message": "Successfully logged out"}
    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Logout failed"
        )

# Dependency to get current user from token
async def get_current_active_user(authorization: HTTPAuthorizationCredentials = Security(security)) -> Dict[str, Any]:
    """Dependency to get the current authenticated user using Supabase JWT"""
    try:
        token = authorization.credentials
        # Use Supabase's built-in JWT verification
        user = supabase.auth.get_user(token)
        return {
            'id': user.user.id,
            'email': user.user.email,
            'role': user.user.role,
            'token': token
        }
    except Exception as e:
        logger.error(f"Authentication error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

# Error handling middleware moved to main.py

# --- Pydantic Schemas ---
class ProjectBase(BaseModel):
    name: str
    address: Optional[str] = None
    start_date: Optional[date] = None
    target_completion_date: Optional[date] = None
    status: Optional[str] = "not_started"
    total_sqft: Optional[int] = None

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(BaseModel):
    """Schema for updating a project (all fields are optional)"""
    name: Optional[str] = None
    address: Optional[str] = None
    start_date: Optional[date] = None
    target_completion_date: Optional[date] = None
    status: Optional[str] = None
    total_sqft: Optional[int] = None

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
    status: Optional[str] = "not_started"

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
@router.get("/projects/{project_id}", 
            response_model=ProjectOut)
async def get_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """Get a specific project by ID"""
    try:
        # First try to get from Supabase
        try:
            response = supabase.table('projects')\
                .select('*')\
                .eq('id', project_id)\
                .eq('user_id', current_user['id'])\
                .execute()
            
            if not response.data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Project not found"
                )
                
            project_data = response.data[0]
            
            # Update or add to local database
            existing_project = db.query(Project).filter(Project.id == project_id).first()
            if existing_project:
                # Update existing project
                for key, value in project_data.items():
                    setattr(existing_project, key, value)
                db.commit()
                db.refresh(existing_project)
                return existing_project
            else:
                # Add new project to local database
                db_project = Project(**project_data)
                db.add(db_project)
                db.commit()
                db.refresh(db_project)
                return db_project
                
        except HTTPException:
            raise
            
        except Exception as e:
            logger.error(f"Supabase error, falling back to local database: {str(e)}")
            # Fallback to local database
            db_project = db.query(Project).filter(
                Project.id == project_id,
                Project.user_id == current_user['id']
            ).first()
            
            if not db_project:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Project not found"
                )
                
            return db_project
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting project: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve project"
        )

@router.get("/projects/", 
            response_model=List[ProjectOut])
async def list_projects(
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """List all projects for the current user"""
    try:
        # Get projects from Supabase
        try:
            response = supabase.table('projects')\
                .select('*')\
                .eq('user_id', current_user['id'])\
                .execute()
            
            projects_data = response.data if response.data else []
            
            # Sync with local database
            if projects_data:
                # Get existing project IDs from the database
                existing_ids = {p.id for p in db.query(Project).filter(Project.user_id == current_user['id']).all()}
                
                # Add or update projects in the local database
                for project_data in projects_data:
                    if project_data['id'] in existing_ids:
                        # Update existing project
                        db.query(Project)\
                            .filter(Project.id == project_data['id'])\
                            .update(project_data)
                    else:
                        # Add new project
                        db_project = Project(**project_data)
                        db.add(db_project)
                
                db.commit()
            
            # Return projects from Supabase
            return projects_data
            
        except Exception as e:
            logger.error(f"Supabase error: {str(e)}")
            # Fallback to local database if Supabase fails
            return db.query(Project)\
                .filter(Project.user_id == current_user['id'])\
                .all()
        
    except Exception as e:
        logger.error(f"Error listing projects: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve projects"
        )

@router.get("/projects/{project_id}", 
           response_model=ProjectOut,
           dependencies=[Depends(get_current_active_user)])
async def get_project(
    project_id: int, 
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """Get a specific project by ID (must be owned by the current user)"""
    try:
        project = db.query(Project)\
            .filter(
                Project.id == project_id,
                Project.user_id == current_user.id
            )\
            .first()
            
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found or access denied"
            )
            
        return project
        
    except Exception as e:
        logger.error(f"Error getting project {project_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve project"
        )

@router.put("/projects/{project_id}", 
            response_model=ProjectOut)
async def update_project(
    project_id: int,
    project: ProjectUpdate,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """Update a project"""
    try:
        # First update in Supabase
        update_data = project.dict(exclude_unset=True)
        
        try:
            # Check if project exists and belongs to user
            response = supabase.table('projects')\
                .select('id')\
                .eq('id', project_id)\
                .eq('user_id', current_user['id'])\
                .execute()
                
            if not response.data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Project not found"
                )
                
            # Update in Supabase
            supabase_response = supabase.table('projects')\
                .update(update_data)\
                .eq('id', project_id)\
                .eq('user_id', current_user['id'])\
                .execute()
                
            if not supabase_response.data:
                raise Exception("Failed to update project in Supabase")
                
            # Get updated project data
            updated_project = supabase_response.data[0]
            
            # Update in local database
            db_project = db.query(Project).filter(Project.id == project_id).first()
            if db_project:
                for key, value in updated_project.items():
                    setattr(db_project, key, value)
                db.commit()
                db.refresh(db_project)
            else:
                # If not in local DB, add it
                db_project = Project(**updated_project)
                db.add(db_project)
                db.commit()
                db.refresh(db_project)
                
            return db_project
            
        except HTTPException:
            raise
            
        except Exception as e:
            logger.error(f"Supabase error: {str(e)}")
            # Fallback to local database
            db_project = db.query(Project).filter(
                Project.id == project_id,
                Project.user_id == current_user['id']
            ).first()
            
            if not db_project:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Project not found"
                )
                
            # Update in local database
            for field, value in update_data.items():
                setattr(db_project, field, value)
                
            db.commit()
            db.refresh(db_project)
            return db_project
            
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating project: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update project"
        )

@router.delete("/projects/{project_id}",
             status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """Delete a project"""
    try:
        # First try to delete from Supabase
        try:
            # Check if project exists and belongs to user
            response = supabase.table('projects')\
                .select('id')\
                .eq('id', project_id)\
                .eq('user_id', current_user['id'])\
                .execute()
                
            if not response.data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Project not found"
                )
                
            # Delete from Supabase
            supabase.table('projects')\
                .delete()\
                .eq('id', project_id)\
                .eq('user_id', current_user['id'])\
                .execute()
                
        except HTTPException:
            raise
            
        except Exception as e:
            logger.error(f"Supabase error: {str(e)}")
            # Continue with local deletion even if Supabase fails
            
        # Delete from local database
        db_project = db.query(Project).filter(
            Project.id == project_id,
            Project.user_id == current_user['id']
        ).first()
        
        if db_project:
            db.delete(db_project)
            db.commit()
            
        return Response(status_code=status.HTTP_204_NO_CONTENT)
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting project: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete project"
        )

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

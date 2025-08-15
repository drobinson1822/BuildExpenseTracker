"""Actual expense endpoints for the Construction Cost Tracker API."""
from typing import List, Dict, Any
import logging

from fastapi import APIRouter, Depends, HTTPException, status, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from api.core.database import get_db
from api.models.expense import ActualExpense
from api.schemas.expense import ActualExpenseCreate, ActualExpenseOut
from api.core.supabase import supabase

# Security configuration
security = HTTPBearer()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

async def get_current_active_user(authorization: HTTPAuthorizationCredentials = Security(security)) -> Dict[str, Any]:
    """Dependency to get the current authenticated user using Supabase JWT"""
    try:
        token = authorization.credentials
        user = supabase.auth.get_user(token)
        
        if not user.user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return {
            'id': user.user.id,
            'email': user.user.email,
            'role': user.user.role or 'user',
            'token': token
        }
    except Exception as e:
        logger.error(f"Authentication error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

@router.post("/", response_model=ActualExpenseOut)
def create_expense(
    expense: ActualExpenseCreate, 
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """Create a new actual expense"""
    try:
        db_expense = ActualExpense(**expense.model_dump())
        db.add(db_expense)
        db.commit()
        db.refresh(db_expense)
        return db_expense
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating expense: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create expense"
        )

@router.get("/", response_model=List[ActualExpenseOut])
def list_expenses(
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """List all actual expenses"""
    try:
        return db.query(ActualExpense).all()
    except Exception as e:
        logger.error(f"Error listing expenses: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve expenses"
        )

@router.get("/{expense_id}", response_model=ActualExpenseOut)
def get_expense(
    expense_id: int, 
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """Get a specific actual expense by ID"""
    try:
        expense = db.query(ActualExpense).filter(ActualExpense.id == expense_id).first()
        if not expense:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Expense not found"
            )
        return expense
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting expense: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve expense"
        )

@router.put("/{expense_id}", response_model=ActualExpenseOut)
def update_expense(
    expense_id: int, 
    expense: ActualExpenseCreate, 
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """Update an actual expense"""
    try:
        db_expense = db.query(ActualExpense).filter(ActualExpense.id == expense_id).first()
        if not db_expense:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Expense not found"
            )
        
        for key, value in expense.model_dump().items():
            setattr(db_expense, key, value)
        
        db.commit()
        db.refresh(db_expense)
        return db_expense
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating expense: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update expense"
        )

@router.delete("/{expense_id}")
def delete_expense(
    expense_id: int, 
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """Delete an actual expense"""
    try:
        db_expense = db.query(ActualExpense).filter(ActualExpense.id == expense_id).first()
        if not db_expense:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Expense not found"
            )
        
        db.delete(db_expense)
        db.commit()
        return {"deleted": True}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting expense: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete expense"
        )

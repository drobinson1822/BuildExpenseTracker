"""Actual expense endpoints for the Construction Cost Tracker API."""
from typing import List, Dict, Any
import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from api.core.database import get_db
from api.models.expense import ActualExpense
from api.schemas.expense import ActualExpenseCreate, ActualExpenseOut
from api.core.supabase import supabase
from api.core.auth import get_current_active_user

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/", response_model=ActualExpenseOut)
def create_expense(
    expense: ActualExpenseCreate, 
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """Create a new actual expense"""
    try:
        expense_data = expense.model_dump()
        expense_data['user_id'] = current_user['id']
        
        # Convert date to string for Supabase
        if 'date' in expense_data and expense_data['date']:
            expense_data['date'] = str(expense_data['date'])
        
        response = supabase.table('actual_expenses').insert(expense_data).execute()
        if not response.data:
            logger.error(f"Supabase response: {response}")
            raise Exception("Failed to create expense in Supabase")
        
        return response.data[0]
    except Exception as e:
        logger.error(f"Error creating expense: {str(e)}")
        logger.error(f"Expense data: {expense_data}")
        logger.error(f"Current user: {current_user}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create expense: {str(e)}"
        )

@router.get("/", response_model=List[ActualExpenseOut])
def list_expenses(
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """List all actual expenses"""
    try:
        response = supabase.table('actual_expenses')\
            .select('*')\
            .eq('user_id', current_user['id'])\
            .execute()
        
        return response.data
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
        response = supabase.table('actual_expenses')\
            .select('*')\
            .eq('id', expense_id)\
            .eq('user_id', current_user['id'])\
            .execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Expense not found"
            )
        
        return response.data[0]
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
        # First check if expense exists and belongs to user
        existing = supabase.table('actual_expenses')\
            .select('id')\
            .eq('id', expense_id)\
            .eq('user_id', current_user['id'])\
            .execute()
        
        if not existing.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Expense not found"
            )
        
        # Update the expense
        expense_data = expense.model_dump()
        response = supabase.table('actual_expenses')\
            .update(expense_data)\
            .eq('id', expense_id)\
            .eq('user_id', current_user['id'])\
            .execute()
        
        if not response.data:
            raise Exception("Failed to update expense")
        
        return response.data[0]
    except HTTPException:
        raise
    except Exception as e:
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
        # First check if expense exists and belongs to user
        existing = supabase.table('actual_expenses')\
            .select('id')\
            .eq('id', expense_id)\
            .eq('user_id', current_user['id'])\
            .execute()
        
        if not existing.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Expense not found"
            )
        
        # Delete the expense
        response = supabase.table('actual_expenses')\
            .delete()\
            .eq('id', expense_id)\
            .eq('user_id', current_user['id'])\
            .execute()
        
        return {"deleted": True}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting expense: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete expense"
        )

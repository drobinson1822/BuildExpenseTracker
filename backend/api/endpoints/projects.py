"""Project endpoints for the Construction Cost Tracker API."""
from typing import List, Dict, Any
import logging

from fastapi import APIRouter, Depends, HTTPException, status, Response, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from api.core.database import get_db
from api.models.project import Project
from api.schemas.project import ProjectCreate, ProjectUpdate, ProjectOut
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

@router.get("/", response_model=List[ProjectOut])
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

@router.get("/{project_id}", response_model=ProjectOut)
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

@router.post("/", response_model=ProjectOut, status_code=status.HTTP_201_CREATED)
async def create_project(
    project: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """Create a new project."""
    try:
        # Add user_id to project data
        project_data = project.dict()
        project_data['user_id'] = current_user['id']
        
        # First try to create in Supabase
        try:
            response = supabase.table('projects')\
                .insert(project_data)\
                .execute()
            
            if not response.data:
                raise Exception("Failed to create project in Supabase")
                
            created_project = response.data[0]
            
            # Also create in local database
            db_project = Project(**created_project)
            db.add(db_project)
            db.commit()
            db.refresh(db_project)
            
            return db_project
            
        except Exception as e:
            logger.error(f"Supabase error: {str(e)}")
            # Fallback to local database only
            db_project = Project(**project_data)
            db.add(db_project)
            db.commit()
            db.refresh(db_project)
            return db_project
            
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating project: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create project"
        )

@router.put("/{project_id}", response_model=ProjectOut)
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

@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
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

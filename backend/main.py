import os
from dotenv import load_dotenv
from fastapi import FastAPI, Depends, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text
from typing import Generator
import logging

# Load environment variables based on ENV or default to development
env = os.getenv('ENV', 'development')
load_dotenv(f'.env.{env}')

# Verify required environment variables
required_vars = [
    'SUPABASE_URL',
    'SUPABASE_SERVICE_ROLE_KEY',
    'DATABASE_URL'
]

missing_vars = [var for var in required_vars if not os.getenv(var)]
if missing_vars:
    raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")

# Import database and models
from api.core.database import engine, Base, get_db
from api.models import *  # Import all models to ensure they're registered with SQLAlchemy

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="Construction Cost Tracker API",
    description="API for managing construction projects and expenses",
    version="1.0.0",
    openapi_url="/api/v1/openapi.json"
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv('ALLOWED_ORIGINS', '*').split(','),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
from api.api import api_router
app.include_router(api_router, prefix="/api/v1")

# Error handling middleware
@app.middleware("http")
async def error_middleware(request: Request, call_next):
    try:
        return await call_next(request)
    except SQLAlchemyError as e:
        logging.error(f"Database error: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"detail": "Database error occurred"}
        )
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "An unexpected error occurred"}
        )

# Health check endpoint
@app.get("/health")
async def health_check():
    try:
        # Test database connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            result.fetchone()
        db_status = "connected"
    except Exception as e:
        logging.error(f"Database connection check failed: {str(e)}")
        db_status = "disconnected"
        
    return {
        "status": "healthy" if db_status == "connected" else "degraded",
        "environment": env,
        "database": db_status
    }

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Welcome to the Construction Cost Tracker API",
        "environment": env,
        "status": "running",
        "docs": "/docs",
        "redoc": "/redoc"
    }

# Dependency to get DB session
@app.middleware("http")
async def db_session_middleware(request, call_next):
    response = None
    try:
        response = await call_next(request)
    finally:
        # Ensure connections are returned to the pool
        pass
    return response

import os
import subprocess
from datetime import datetime
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

# Log environment configuration (without sensitive values)
logging.info(f"🔧 Environment: {env}")
logging.info(f"🔗 Supabase URL configured: {bool(os.getenv('SUPABASE_URL'))}")
logging.info(f"🔑 Service role key configured: {bool(os.getenv('SUPABASE_SERVICE_ROLE_KEY'))}")
logging.info(f"💾 Database URL configured: {bool(os.getenv('DATABASE_URL'))}")
if os.getenv('SUPABASE_URL'):
    logging.info(f"🌐 Supabase URL domain: {os.getenv('SUPABASE_URL').split('//')[1].split('.')[0] if '//' in os.getenv('SUPABASE_URL') else 'unknown'}")

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
allowed_origins = os.getenv('ALLOWED_ORIGINS', 'http://localhost:3000,http://localhost:5173,http://localhost:5174,http://localhost:8000').split(',')
logging.info(f"🌍 CORS allowed origins: {allowed_origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
from api.api import api_router
app.include_router(api_router, prefix="/api/v1")

# Request/Response logging middleware
@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    start_time = datetime.now()
    
    # Log incoming request
    logging.info(f"🌐 {request.method} {request.url.path} - Client: {request.client.host if request.client else 'unknown'}")
    
    # Log request headers (excluding sensitive ones)
    headers_to_log = {k: v for k, v in request.headers.items() 
                     if k.lower() not in ['authorization', 'cookie']}
    logging.info(f"📋 Request headers: {headers_to_log}")
    
    # For auth endpoints, log additional details
    if "/auth/" in str(request.url.path):
        logging.info(f"🔐 Auth endpoint accessed: {request.url.path}")
        logging.info(f"🌍 Origin: {request.headers.get('origin', 'not set')}")
        logging.info(f"🔗 Referer: {request.headers.get('referer', 'not set')}")
    
    response = await call_next(request)
    
    # Calculate response time
    process_time = (datetime.now() - start_time).total_seconds()
    
    # Log response
    logging.info(f"📤 Response: {response.status_code} - {process_time:.3f}s")
    
    return response

# Error handling middleware
@app.middleware("http")
async def error_middleware(request: Request, call_next):
    try:
        return await call_next(request)
    except SQLAlchemyError as e:
        logging.error(f"💾 Database error: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"detail": "Database error occurred"}
        )
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"💥 Unexpected error: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "An unexpected error occurred"}
        )

# Health check endpoint (as specified in deployment guide)
@app.get("/healthz")
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
        "status": "ok" if db_status == "connected" else "degraded",
        "environment": env,
        "database": db_status
    }


# Version endpoint (as specified in deployment guide)
@app.get("/version")
async def version_info():
    try:
        # Get git SHA
        git_sha = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], 
            cwd=os.path.dirname(__file__),
            stderr=subprocess.DEVNULL
        ).decode().strip()[:8]
    except:
        git_sha = "unknown"
    
    return {
        "version": "1.0.0",
        "git_sha": git_sha,
        "build_timestamp": datetime.now().isoformat(),
        "environment": env
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

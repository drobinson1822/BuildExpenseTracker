"""Main API router that includes all endpoint routes."""
from fastapi import APIRouter

from api.endpoints import auth, projects, forecast, expenses, draws

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(projects.router, prefix="/projects", tags=["projects"])
api_router.include_router(forecast.router, prefix="/forecast-items", tags=["forecast"])
api_router.include_router(expenses.router, prefix="/expenses", tags=["expenses"])
api_router.include_router(draws.router, prefix="/draws", tags=["draws"])

import os
import sys
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from typing import Generator

# Set up test environment variables before any imports
os.environ["ENV"] = "test"
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["SUPABASE_URL"] = "https://mock-supabase-url.supabase.co"
os.environ["SUPABASE_SECRET_KEY"] = "mock-supabase-secret-key"
os.environ["ALLOWED_ORIGINS"] = "http://localhost:3000,http://localhost:8000"

# Add the parent directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import required modules
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from database import Base, get_db
from models import Project, ForecastLineItem, ActualExpense, DrawTracker, ProjectStatusEnum, ForecastStatusEnum
from datetime import date, datetime

# Create test database engine
TEST_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables
Base.metadata.create_all(bind=engine)

# Mock Supabase client
@pytest.fixture(autouse=True)
def mock_supabase():
    """Mock Supabase client for all tests"""
    # Create mock objects
    mock_user = Mock()
    mock_user.user.id = "test-user-id"
    mock_user.user.email = "test@example.com"
    mock_user.user.role = "authenticated"
    
    mock_supabase = Mock()
    mock_supabase.auth.get_user.return_value = mock_user
    mock_supabase.auth.admin.get_user_by_email.return_value = Mock(user=None)
    mock_supabase.auth.admin.create_user.return_value = Mock(user=mock_user.user)
    mock_supabase.auth.sign_in_with_password.return_value = Mock(
        user=mock_user.user,
        session=Mock(access_token="mock-token", refresh_token="mock-refresh-token")
    )
    
    # Use sys.modules to replace the imports
    import sys
    sys.modules['supabase_client'] = Mock()
    sys.modules['supabase_client'].supabase = mock_supabase
    sys.modules['supabase_client'].supabase_admin = mock_supabase
    sys.modules['supabase_client'].get_current_user = Mock(return_value={
        'id': 'test-user-id',
        'email': 'test@example.com',
        'role': 'authenticated'
    })
    
    # Also inject into the actual module used by endpoints
    try:
        import api.core.supabase as core_supabase
        core_supabase.supabase = mock_supabase
        core_supabase.supabase_admin = mock_supabase
    except Exception:
        pass

    yield mock_supabase

# Database session fixture
@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test"""
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    # Create tables for this test
    Base.metadata.create_all(bind=connection)
    
    yield session
    
    # Cleanup
    session.close()
    transaction.rollback()
    connection.close()

# Override get_db dependency
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

# Test client fixture
@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with database override"""
    from main import app
    
    def get_test_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = get_test_db
    
    # Create test client without context manager to avoid initialization issues
    test_client = TestClient(app)
    yield test_client
    
    # Clean up overrides
    app.dependency_overrides.clear()

# Mock authentication dependency
@pytest.fixture
def mock_current_user():
    """Mock current user for authenticated endpoints"""
    return {
        'id': 'test-user-id',
        'email': 'test@example.com',
        'role': 'authenticated',
        'token': 'mock-token'
    }

@pytest.fixture
def mock_auth_dependency(mock_current_user):
    """Mock the authentication dependency"""
    with patch('routers.get_current_active_user') as mock_auth:
        mock_auth.return_value = mock_current_user
        yield mock_auth

# Simple test data creation functions (no Factory Boy)
def create_test_project(db_session, **kwargs):
    """Create a test project with default or custom values"""
    defaults = {
        "name": "Test Project",
        "address": "123 Test St",
        "start_date": date(2024, 1, 1),
        "target_completion_date": date(2024, 12, 31),
        "status": ProjectStatusEnum.not_started,
        "total_sqft": 2000
    }
    defaults.update(kwargs)
    
    project = Project(**defaults)
    db_session.add(project)
    db_session.commit()
    db_session.refresh(project)
    return project

def create_test_forecast_item(db_session, project_id, **kwargs):
    """Create a test forecast line item with default or custom values"""
    defaults = {
        "project_id": project_id,
        "category": "Materials",
        "estimated_cost": 5000.00,
        "unit": "sqft",
        "notes": "Test forecast item",
        "progress_percent": 0,
        "status": ForecastStatusEnum.not_started
    }
    defaults.update(kwargs)
    
    item = ForecastLineItem(**defaults)
    db_session.add(item)
    db_session.commit()
    db_session.refresh(item)
    return item

def create_test_expense(db_session, project_id, forecast_line_item_id=None, **kwargs):
    """Create a test expense with default or custom values"""
    defaults = {
        "project_id": project_id,
        "forecast_line_item_id": forecast_line_item_id,
        "vendor": "Test Vendor",
        "amount_spent": 1500.00,
        "date": date(2024, 1, 15),
        "receipt_url": "https://example.com/receipt.pdf"
    }
    defaults.update(kwargs)
    
    expense = ActualExpense(**defaults)
    db_session.add(expense)
    db_session.commit()
    db_session.refresh(expense)
    return expense

def create_test_draw(db_session, project_id, **kwargs):
    """Create a test draw tracker with default or custom values"""
    defaults = {
        "project_id": project_id,
        "cash_on_hand": 50000.00,
        "last_draw_date": date(2024, 1, 1),
        "draw_triggered": False,
        "notes": "Test draw tracker"
    }
    defaults.update(kwargs)
    
    draw = DrawTracker(**defaults)
    db_session.add(draw)
    db_session.commit()
    db_session.refresh(draw)
    return draw

# Test data fixtures
@pytest.fixture
def test_project(db_session):
    """Create a test project"""
    project = Project(
        name="Test Project",
        address="123 Test St",
        start_date=date(2024, 1, 1),
        target_completion_date=date(2024, 12, 31),
        status=ProjectStatusEnum.not_started,
        total_sqft=2000
    )
    db_session.add(project)
    db_session.commit()
    db_session.refresh(project)
    return project

@pytest.fixture
def test_forecast_item(db_session, test_project):
    """Create a test forecast line item"""
    item = ForecastLineItem(
        project_id=test_project.id,
        category="Materials",
        estimated_cost=5000.00,
        unit="sqft",
        notes="Test forecast item",
        progress_percent=0,
        status=ForecastStatusEnum.not_started
    )
    db_session.add(item)
    db_session.commit()
    db_session.refresh(item)
    return item

@pytest.fixture
def test_expense(db_session, test_project, test_forecast_item):
    """Create a test expense"""
    expense = ActualExpense(
        project_id=test_project.id,
        forecast_line_item_id=test_forecast_item.id,
        vendor="Test Vendor",
        amount_spent=1500.00,
        date=date(2024, 1, 15),
        receipt_url="https://example.com/receipt.pdf"
    )
    db_session.add(expense)
    db_session.commit()
    db_session.refresh(expense)
    return expense

@pytest.fixture
def test_draw(db_session, test_project):
    """Create a test draw tracker"""
    draw = DrawTracker(
        project_id=test_project.id,
        cash_on_hand=50000.00,
        last_draw_date=date(2024, 1, 1),
        draw_triggered=False,
        notes="Test draw tracker"
    )
    db_session.add(draw)
    db_session.commit()
    db_session.refresh(draw)
    return draw

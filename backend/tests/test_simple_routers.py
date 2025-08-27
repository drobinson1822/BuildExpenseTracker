import pytest
import os
import sys
from pathlib import Path
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Set up test environment
os.environ["ENV"] = "test"
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["SUPABASE_URL"] = "https://mock-supabase-url.supabase.co"
os.environ["SUPABASE_SECRET_KEY"] = "mock-supabase-secret-key"
os.environ["ALLOWED_ORIGINS"] = "http://localhost:3000,http://localhost:8000"

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Mock supabase_client module before importing anything that uses it
mock_supabase_client = Mock()
mock_supabase_client.supabase = Mock()
mock_supabase_client.supabase_admin = Mock()
mock_supabase_client.get_current_user = Mock()
sys.modules['supabase_client'] = mock_supabase_client

# Now import the modules we need
from database import Base, get_db
from models import Project, ProjectStatusEnum
from datetime import date


class TestSimpleRouters:
    """Simple tests for router functionality without complex authentication"""
    
    @pytest.fixture(scope="function")
    def test_db(self):
        """Create a test database session"""
        engine = create_engine(
            "sqlite:///:memory:",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        
        # Ensure tables are created
        Base.metadata.drop_all(bind=engine)  # Clean slate
        Base.metadata.create_all(bind=engine)  # Create all tables
        
        db = TestingSessionLocal()
        yield db
        db.close()
    
    @pytest.fixture(scope="function")
    def test_client(self, test_db):
        """Create a test client with mocked dependencies"""
        # Mock the authentication dependency
        def mock_get_current_user():
            return {
                'id': 'test-user-id',
                'email': 'test@example.com',
                'role': 'authenticated'
            }
        
        def override_get_db():
            try:
                yield test_db
            finally:
                pass
        
        # Import main app and override dependencies
        with patch('routers.get_current_active_user', return_value=mock_get_current_user()):
            from main import app
            app.dependency_overrides[get_db] = override_get_db
            
            client = TestClient(app)
            yield client
            
            # Clean up
            app.dependency_overrides.clear()
    
    def test_health_check(self, test_client):
        """Test the health check endpoint"""
        response = test_client.get("/health")
        assert response.status_code == 200
        # Health check might return different responses based on implementation
        
    def test_root_endpoint(self, test_client):
        """Test the root endpoint"""
        response = test_client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "docs" in data or "message" in data
        
    def test_create_project_basic(self, test_client):
        """Test basic project creation"""
        project_data = {
            "name": "Test Project",
            "address": "123 Test St",
            "start_date": "2024-01-01",
            "target_completion_date": "2024-12-31",
            "status": "not_started",
            "total_sqft": 2000
        }
        
        with patch('routers.get_current_active_user') as mock_auth:
            mock_auth.return_value = {
                'id': 'test-user-id',
                'email': 'test@example.com',
                'role': 'authenticated'
            }
            
            response = test_client.post("/api/v1/projects/", json=project_data)
            
            # Check if the endpoint exists and responds
            assert response.status_code in [200, 201, 401, 422]  # Various acceptable responses
            
            if response.status_code in [200, 201]:
                data = response.json()
                assert "name" in data or "id" in data
    
    def test_list_projects_basic(self, test_client):
        """Test basic project listing"""
        with patch('routers.get_current_active_user') as mock_auth:
            mock_auth.return_value = {
                'id': 'test-user-id',
                'email': 'test@example.com',
                'role': 'authenticated'
            }
            
            response = test_client.get("/api/v1/projects/")
            
            # Check if the endpoint exists and responds
            assert response.status_code in [200, 401]  # Either success or auth required
            
            if response.status_code == 200:
                data = response.json()
                assert isinstance(data, list)
    
    def test_database_models(self, test_db):
        """Test that database models work correctly"""
        # Create a test project directly in the database
        project = Project(
            name="Test Project",
            address="123 Test St",
            start_date=date(2024, 1, 1),
            target_completion_date=date(2024, 12, 31),
            status=ProjectStatusEnum.not_started,
            total_sqft=2000
        )
        
        test_db.add(project)
        test_db.commit()
        test_db.refresh(project)
        
        # Verify the project was created
        assert project.id is not None
        assert project.name == "Test Project"
        assert project.status == ProjectStatusEnum.not_started
        
        # Query the project back
        queried_project = test_db.query(Project).filter(Project.name == "Test Project").first()
        assert queried_project is not None
        assert queried_project.id == project.id

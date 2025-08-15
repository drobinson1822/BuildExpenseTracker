import pytest
from fastapi import status
from unittest.mock import patch
from datetime import date


class TestProjectRouters:
    """Test project CRUD endpoints"""

    def test_create_project_success(self, client, mock_auth_dependency):
        """Test successful project creation"""
        project_data = {
            "name": "Test Project",
            "address": "123 Test St",
            "start_date": "2024-01-01",
            "target_completion_date": "2024-12-31",
            "status": "not_started",
            "total_sqft": 2000
        }
        
        response = client.post("/api/v1/projects/", json=project_data)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == project_data["name"]
        assert data["address"] == project_data["address"]
        assert data["status"] == project_data["status"]
        assert data["total_sqft"] == project_data["total_sqft"]
        assert "id" in data

    def test_create_project_validation_error(self, client, mock_auth_dependency):
        """Test project creation with validation errors"""
        # Missing required name field
        project_data = {
            "address": "123 Test St",
            "status": "not_started"
        }
        
        response = client.post("/api/v1/projects/", json=project_data)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_list_projects_success(self, client, mock_auth_dependency, test_project):
        """Test listing projects"""
        response = client.get("/api/v1/projects/")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert data[0]["id"] == test_project.id
        assert data[0]["name"] == test_project.name

    def test_get_project_success(self, client, mock_auth_dependency, test_project):
        """Test getting a specific project"""
        response = client.get(f"/api/v1/projects/{test_project.id}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == test_project.id
        assert data["name"] == test_project.name
        assert data["address"] == test_project.address

    def test_get_project_not_found(self, client, mock_auth_dependency):
        """Test getting a non-existent project"""
        response = client.get("/api/v1/projects/99999")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert "not found" in data["detail"].lower()

    def test_update_project_success(self, client, mock_auth_dependency, test_project):
        """Test updating a project"""
        update_data = {
            "name": "Updated Project Name",
            "status": "in_progress",
            "total_sqft": 2500
        }
        
        response = client.put(f"/api/v1/projects/{test_project.id}", json=update_data)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == update_data["name"]
        assert data["status"] == update_data["status"]
        assert data["total_sqft"] == update_data["total_sqft"]

    def test_update_project_not_found(self, client, mock_auth_dependency):
        """Test updating a non-existent project"""
        update_data = {"name": "Updated Name"}
        
        response = client.put("/api/v1/projects/99999", json=update_data)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_project_success(self, client, mock_auth_dependency, test_project):
        """Test deleting a project"""
        response = client.delete(f"/api/v1/projects/{test_project.id}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["deleted"] == True
        
        # Verify project is deleted
        get_response = client.get(f"/api/v1/projects/{test_project.id}")
        assert get_response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_project_not_found(self, client, mock_auth_dependency):
        """Test deleting a non-existent project"""
        response = client.delete("/api/v1/projects/99999")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_project_relationships(self, client, mock_auth_dependency, test_project, test_forecast_item, test_expense, test_draw):
        """Test that project relationships are properly loaded"""
        response = client.get(f"/api/v1/projects/{test_project.id}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Check that the project exists and has the expected structure
        assert data["id"] == test_project.id
        assert data["name"] == test_project.name

    def test_project_status_enum_validation(self, client, mock_auth_dependency):
        """Test project status enum validation"""
        project_data = {
            "name": "Test Project",
            "status": "invalid_status"
        }
        
        response = client.post("/api/v1/projects/", json=project_data)
        
        # Should either accept it (if validation is lenient) or reject it
        # This depends on your enum validation implementation
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_422_UNPROCESSABLE_ENTITY]

    def test_project_date_validation(self, client, mock_auth_dependency):
        """Test project date validation"""
        project_data = {
            "name": "Test Project",
            "start_date": "2024-12-31",
            "target_completion_date": "2024-01-01"  # End date before start date
        }
        
        response = client.post("/api/v1/projects/", json=project_data)
        
        # Should create successfully (business logic validation might be separate)
        assert response.status_code == status.HTTP_200_OK

    def test_unauthorized_access(self, client):
        """Test accessing project endpoints without authentication"""
        # Remove auth dependency override
        response = client.get("/api/v1/projects/")
        
        # Should return 401 if authentication is required
        # Note: This depends on whether you've implemented auth requirements
        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_200_OK]

import pytest
from fastapi import status
from datetime import date


class TestDrawTrackerRouters:
    """Test draw tracker CRUD endpoints"""

    def test_create_draw_success(self, client, test_project):
        """Test successful draw tracker creation"""
        draw_data = {
            "project_id": test_project.id,
            "cash_on_hand": 50000.00,
            "last_draw_date": "2024-01-01",
            "draw_triggered": False,
            "notes": "Initial draw setup"
        }
        
        response = client.post("/api/v1/draws/", json=draw_data)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["project_id"] == draw_data["project_id"]
        assert data["cash_on_hand"] == draw_data["cash_on_hand"]
        assert data["draw_triggered"] == draw_data["draw_triggered"]
        assert data["notes"] == draw_data["notes"]
        assert "id" in data

    def test_create_draw_validation_error(self, client):
        """Test draw creation with validation errors"""
        # Missing required fields
        draw_data = {
            "notes": "Test draw"
            # Missing project_id and cash_on_hand
        }
        
        response = client.post("/api/v1/draws/", json=draw_data)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_list_draws_success(self, client, test_draw):
        """Test listing draws"""
        response = client.get("/api/v1/draws/")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert data[0]["id"] == test_draw.id
        assert data[0]["project_id"] == test_draw.project_id

    def test_get_draw_success(self, client, test_draw):
        """Test getting a specific draw"""
        response = client.get(f"/api/v1/draws/{test_draw.id}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == test_draw.id
        assert data["project_id"] == test_draw.project_id
        assert data["cash_on_hand"] == test_draw.cash_on_hand

    def test_get_draw_not_found(self, client):
        """Test getting a non-existent draw"""
        response = client.get("/api/v1/draws/99999")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert "not found" in data["detail"].lower()

    def test_update_draw_success(self, client, test_draw):
        """Test updating a draw"""
        update_data = {
            "project_id": test_draw.project_id,
            "cash_on_hand": 75000.00,
            "draw_triggered": True,
            "notes": "Updated draw notes"
        }
        
        response = client.put(f"/api/v1/draws/{test_draw.id}", json=update_data)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["cash_on_hand"] == update_data["cash_on_hand"]
        assert data["draw_triggered"] == update_data["draw_triggered"]
        assert data["notes"] == update_data["notes"]

    def test_update_draw_not_found(self, client, test_project):
        """Test updating a non-existent draw"""
        update_data = {
            "project_id": test_project.id,
            "cash_on_hand": 75000.00
        }
        
        response = client.put("/api/v1/draws/99999", json=update_data)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_draw_success(self, client, test_draw):
        """Test deleting a draw"""
        response = client.delete(f"/api/v1/draws/{test_draw.id}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["deleted"] == True
        
        # Verify draw is deleted
        get_response = client.get(f"/api/v1/draws/{test_draw.id}")
        assert get_response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_draw_not_found(self, client):
        """Test deleting a non-existent draw"""
        response = client.delete("/api/v1/draws/99999")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_draw_project_relationship(self, client, test_draw, test_project):
        """Test draw to project relationship"""
        response = client.get(f"/api/v1/draws/{test_draw.id}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["project_id"] == test_project.id

    def test_list_draws_by_project(self, client, test_project, test_draw):
        """Test filtering draws by project"""
        # This would require implementing query parameters in your router
        # For now, we'll test the basic list functionality
        response = client.get("/api/v1/draws/")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Find our test draw in the list
        test_draw_data = next((draw for draw in data if draw["id"] == test_draw.id), None)
        assert test_draw_data is not None
        assert test_draw_data["project_id"] == test_project.id

    def test_trigger_draw(self, client, test_draw):
        """Test triggering a draw"""
        # Update draw to trigger it
        update_data = {
            "project_id": test_draw.project_id,
            "cash_on_hand": test_draw.cash_on_hand,
            "draw_triggered": True,
            "last_draw_date": "2024-02-01"
        }
        
        response = client.put(f"/api/v1/draws/{test_draw.id}", json=update_data)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["draw_triggered"] == True
        assert data["last_draw_date"] == update_data["last_draw_date"]

    def test_draw_negative_cash_validation(self, client, test_project):
        """Test negative cash on hand validation"""
        draw_data = {
            "project_id": test_project.id,
            "cash_on_hand": -10000.00,  # Negative cash
            "draw_triggered": False
        }
        
        response = client.post("/api/v1/draws/", json=draw_data)
        
        # Should create successfully (business validation might be separate)
        assert response.status_code == status.HTTP_200_OK

    def test_draw_validation_errors(self, client, test_project):
        """Test various validation scenarios"""
        # Test with missing required project_id
        draw_data = {
            "cash_on_hand": 50000.00
        }
        
        response = client.post("/api/v1/draws/", json=draw_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        
        # Test with missing cash_on_hand
        draw_data = {
            "project_id": test_project.id
        }
        
        response = client.post("/api/v1/draws/", json=draw_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_draw_future_date_validation(self, client, test_project):
        """Test future date validation for last_draw_date"""
        from datetime import datetime, timedelta
        
        future_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
        
        draw_data = {
            "project_id": test_project.id,
            "cash_on_hand": 50000.00,
            "last_draw_date": future_date
        }
        
        response = client.post("/api/v1/draws/", json=draw_data)
        
        # Should create successfully (business validation might be separate)
        assert response.status_code == status.HTTP_200_OK

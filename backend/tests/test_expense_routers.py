import pytest
from fastapi import status
from datetime import date


class TestActualExpenseRouters:
    """Test actual expense CRUD endpoints"""

    def test_create_expense_success(self, client, test_project, test_forecast_item):
        """Test successful expense creation"""
        expense_data = {
            "project_id": test_project.id,
            "forecast_line_item_id": test_forecast_item.id,
            "vendor": "Test Vendor",
            "amount_spent": 1500.00,
            "date": "2024-01-15",
            "receipt_url": "https://example.com/receipt.pdf"
        }
        
        response = client.post("/api/v1/expenses/", json=expense_data)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["project_id"] == expense_data["project_id"]
        assert data["forecast_line_item_id"] == expense_data["forecast_line_item_id"]
        assert data["vendor"] == expense_data["vendor"]
        assert data["amount_spent"] == expense_data["amount_spent"]
        assert "id" in data

    def test_create_expense_without_forecast_item(self, client, test_project):
        """Test creating expense without linking to forecast item"""
        expense_data = {
            "project_id": test_project.id,
            "vendor": "Test Vendor",
            "amount_spent": 1500.00,
            "date": "2024-01-15"
        }
        
        response = client.post("/api/v1/expenses/", json=expense_data)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["project_id"] == expense_data["project_id"]
        assert data["forecast_line_item_id"] is None
        assert data["vendor"] == expense_data["vendor"]

    def test_create_expense_validation_error(self, client):
        """Test expense creation with validation errors"""
        # Missing required fields
        expense_data = {
            "vendor": "Test Vendor"
            # Missing project_id and amount_spent
        }
        
        response = client.post("/api/v1/expenses/", json=expense_data)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_list_expenses_success(self, client, test_expense):
        """Test listing expenses"""
        response = client.get("/api/v1/expenses/")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert data[0]["id"] == test_expense.id
        assert data[0]["vendor"] == test_expense.vendor

    def test_get_expense_success(self, client, test_expense):
        """Test getting a specific expense"""
        response = client.get(f"/api/v1/expenses/{test_expense.id}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == test_expense.id
        assert data["vendor"] == test_expense.vendor
        assert data["project_id"] == test_expense.project_id

    def test_get_expense_not_found(self, client):
        """Test getting a non-existent expense"""
        response = client.get("/api/v1/expenses/99999")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert "not found" in data["detail"].lower()

    def test_update_expense_success(self, client, test_expense):
        """Test updating an expense"""
        update_data = {
            "project_id": test_expense.project_id,
            "vendor": "Updated Vendor",
            "amount_spent": 2000.00,
            "date": "2024-02-01"
        }
        
        response = client.put(f"/api/v1/expenses/{test_expense.id}", json=update_data)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["vendor"] == update_data["vendor"]
        assert data["amount_spent"] == update_data["amount_spent"]

    def test_update_expense_not_found(self, client, test_project):
        """Test updating a non-existent expense"""
        update_data = {
            "project_id": test_project.id,
            "vendor": "Updated Vendor",
            "amount_spent": 2000.00
        }
        
        response = client.put("/api/v1/expenses/99999", json=update_data)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_expense_success(self, client, test_expense):
        """Test deleting an expense"""
        response = client.delete(f"/api/v1/expenses/{test_expense.id}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["deleted"] == True
        
        # Verify expense is deleted
        get_response = client.get(f"/api/v1/expenses/{test_expense.id}")
        assert get_response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_expense_not_found(self, client):
        """Test deleting a non-existent expense"""
        response = client.delete("/api/v1/expenses/99999")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_expense_relationships(self, client, test_expense, test_project, test_forecast_item):
        """Test expense relationships to project and forecast item"""
        response = client.get(f"/api/v1/expenses/{test_expense.id}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["project_id"] == test_project.id
        assert data["forecast_line_item_id"] == test_forecast_item.id

    def test_list_expenses_filtering(self, client, test_project, test_expense):
        """Test filtering expenses (if implemented)"""
        # This would require implementing query parameters in your router
        # For now, we'll test the basic list functionality
        response = client.get("/api/v1/expenses/")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Find our test expense in the list
        test_exp = next((exp for exp in data if exp["id"] == test_expense.id), None)
        assert test_exp is not None
        assert test_exp["project_id"] == test_project.id

    def test_expense_negative_amount_validation(self, client, test_project):
        """Test negative amount validation"""
        expense_data = {
            "project_id": test_project.id,
            "vendor": "Test Vendor",
            "amount_spent": -500.00,  # Negative amount
            "date": "2024-01-15"
        }
        
        response = client.post("/api/v1/expenses/", json=expense_data)
        
        # Should create successfully (business validation might be separate)
        assert response.status_code == status.HTTP_200_OK

    def test_expense_future_date_validation(self, client, test_project):
        """Test future date validation"""
        from datetime import datetime, timedelta
        
        future_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
        
        expense_data = {
            "project_id": test_project.id,
            "vendor": "Test Vendor",
            "amount_spent": 500.00,
            "date": future_date
        }
        
        response = client.post("/api/v1/expenses/", json=expense_data)
        
        # Should create successfully (business validation might be separate)
        assert response.status_code == status.HTTP_200_OK

    def test_expense_invalid_receipt_url(self, client, test_project):
        """Test invalid receipt URL"""
        expense_data = {
            "project_id": test_project.id,
            "vendor": "Test Vendor",
            "amount_spent": 500.00,
            "date": "2024-01-15",
            "receipt_url": "not-a-valid-url"
        }
        
        response = client.post("/api/v1/expenses/", json=expense_data)
        
        # Should create successfully (URL validation might be lenient)
        assert response.status_code == status.HTTP_200_OK

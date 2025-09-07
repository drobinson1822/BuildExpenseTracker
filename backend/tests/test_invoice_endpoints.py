"""Tests for invoice management endpoints."""
import pytest
from fastapi import status
from unittest.mock import patch, Mock, MagicMock
from datetime import datetime, timedelta
import uuid


class TestInvoiceEndpoints:
    """Test invoice CRUD endpoints"""

    def test_begin_upload_success(self, client, test_forecast_item):
        """Test successful invoice upload initiation"""
        # Debug: Print the forecast item details
        print(f"Test forecast item ID: {test_forecast_item.id}")
        print(f"Test forecast item user_id: {test_forecast_item.user_id}")
        
        upload_data = {
            "line_item_id": test_forecast_item.id,
            "file_name": "test_invoice.pdf",
            "mime_type": "application/pdf",
            "file_size": 1024000  # 1MB
        }
        
        # Mock Supabase storage response
        mock_upload_url = {
            "signedURL": "https://mock-signed-url.com/upload"
        }
        
        with patch('api.endpoints.invoices.supabase') as mock_supabase:
            mock_supabase.storage.from_.return_value.create_signed_upload_url.return_value = mock_upload_url
            
            response = client.post(f"/api/v1/line-items/{test_forecast_item.id}/invoices:begin-upload", json=upload_data)
            
            # Debug: Print response details if it fails
            if response.status_code != status.HTTP_200_OK:
                print(f"Response status: {response.status_code}")
                print(f"Response body: {response.json()}")
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert "invoice_id" in data
            assert "upload_url" in data
            assert "expires_at" in data
            assert data["upload_url"] == mock_upload_url["signedURL"]

    def test_begin_upload_invalid_file_type(self, client, test_forecast_item):
        """Test upload initiation with invalid file type"""
        upload_data = {
            "line_item_id": test_forecast_item.id,
            "file_name": "test_invoice.txt",
            "mime_type": "text/plain",
            "file_size": 1024
        }
        
        response = client.post(f"/api/v1/line-items/{test_forecast_item.id}/invoices:begin-upload", json=upload_data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "not allowed" in response.json()["detail"]

    def test_begin_upload_file_too_large(self, client, test_forecast_item):
        """Test upload initiation with file too large"""
        upload_data = {
            "line_item_id": test_forecast_item.id,
            "file_name": "test_invoice.pdf",
            "mime_type": "application/pdf",
            "file_size": 11 * 1024 * 1024  # 11MB (exceeds 10MB limit)
        }
        
        response = client.post(f"/api/v1/line-items/{test_forecast_item.id}/invoices:begin-upload", json=upload_data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "exceeds maximum" in response.json()["detail"]

    def test_begin_upload_line_item_not_found(self, client):
        """Test upload initiation with non-existent line item"""
        upload_data = {
            "line_item_id": 99999,
            "file_name": "test_invoice.pdf",
            "mime_type": "application/pdf",
            "file_size": 1024
        }
        
        response = client.post("/api/v1/line-items/99999/invoices:begin-upload", json=upload_data)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "Not Found" in response.json()["detail"]

    def test_complete_upload_success(self, client, test_invoice_pending):
        """Test successful upload completion"""
        with patch('api.endpoints.invoices.supabase') as mock_supabase:
            mock_supabase.storage.from_.return_value.get_public_url.return_value = "https://mock-url.com"
            
            response = client.post(f"/api/v1/line-items/{test_invoice_pending.line_item_id}/invoices/{test_invoice_pending.id}:complete")
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["id"] == test_invoice_pending.id
            assert data["status"] == "uploaded"

    def test_complete_upload_invoice_not_found(self, client):
        """Test upload completion with non-existent invoice"""
        response = client.post("/api/v1/line-items/1/invoices/99999:complete")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_complete_upload_not_pending(self, client, test_invoice_uploaded):
        """Test upload completion with non-pending invoice"""
        response = client.post(f"/api/v1/line-items/{test_invoice_uploaded.line_item_id}/invoices/{test_invoice_uploaded.id}:complete")
        
        assert response.status_code == status.HTTP_409_CONFLICT
        assert "not in pending status" in response.json()["detail"]

    def test_list_invoices_success(self, client, test_invoice_uploaded):
        """Test listing invoices for a line item"""
        response = client.get(f"/api/v1/line-items/{test_invoice_uploaded.line_item_id}/invoices")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert any(invoice["id"] == test_invoice_uploaded.id for invoice in data)

    def test_list_invoices_line_item_not_found(self, client):
        """Test listing invoices for non-existent line item"""
        response = client.get("/api/v1/line-items/99999/invoices")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_view_url_success(self, client, test_invoice_uploaded):
        """Test getting signed view URL for invoice"""
        mock_signed_url = {
            "signedURL": "https://mock-signed-url.com/view"
        }
        
        with patch('api.endpoints.invoices.supabase') as mock_supabase:
            mock_supabase.storage.from_.return_value.create_signed_url.return_value = mock_signed_url
            
            response = client.get(f"/api/v1/line-items/{test_invoice_uploaded.line_item_id}/invoices/{test_invoice_uploaded.id}:view-url")
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert "view_url" in data
            assert "expires_at" in data
            assert data["view_url"] == mock_signed_url["signedURL"]

    def test_get_view_url_invoice_not_found(self, client):
        """Test getting view URL for non-existent invoice"""
        response = client.get("/api/v1/line-items/1/invoices/99999:view-url")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_invoice_success(self, client, test_invoice_uploaded):
        """Test successful invoice deletion"""
        with patch('api.endpoints.invoices.supabase') as mock_supabase:
            mock_supabase.storage.from_.return_value.remove.return_value = None
            
            response = client.delete(f"/api/v1/line-items/{test_invoice_uploaded.line_item_id}/invoices/{test_invoice_uploaded.id}")
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert "deleted successfully" in data["message"]

    def test_delete_invoice_not_found(self, client):
        """Test deleting non-existent invoice"""
        response = client.delete("/api/v1/line-items/1/invoices/99999")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_authentication_required(self, client_no_auth, test_forecast_item):
        """Test that all endpoints require authentication"""
        endpoints = [
            ("POST", f"/api/v1/line-items/{test_forecast_item.id}/invoices:begin-upload"),
            ("POST", f"/api/v1/line-items/{test_forecast_item.id}/invoices/1:complete"),
            ("GET", f"/api/v1/line-items/{test_forecast_item.id}/invoices"),
            ("GET", f"/api/v1/line-items/{test_forecast_item.id}/invoices/1:view-url"),
            ("DELETE", f"/api/v1/line-items/{test_forecast_item.id}/invoices/1")
        ]
        
        for method, endpoint in endpoints:
            if method == "POST":
                response = client_no_auth.post(endpoint, json={})
            elif method == "GET":
                response = client_no_auth.get(endpoint)
            elif method == "DELETE":
                response = client_no_auth.delete(endpoint)
            
            assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_user_isolation(self, client_different_user, test_invoice_uploaded):
        """Test that users can only access their own invoices"""
        # Try to access another user's invoice
        response = client_different_user.get(f"/api/v1/line-items/{test_invoice_uploaded.line_item_id}/invoices")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_file_validation_edge_cases(self, client, test_forecast_item):
        """Test edge cases in file validation"""
        # Test exactly at size limit
        upload_data = {
            "line_item_id": test_forecast_item.id,
            "file_name": "test_invoice.pdf",
            "mime_type": "application/pdf",
            "file_size": 10 * 1024 * 1024  # Exactly 10MB
        }
        
        with patch('api.endpoints.invoices.supabase') as mock_supabase:
            mock_supabase.storage.from_.return_value.create_signed_upload_url.return_value = {
                "signedURL": "https://mock-url.com"
            }
            
            response = client.post(f"/api/v1/line-items/{test_forecast_item.id}/invoices:begin-upload", json=upload_data)
            assert response.status_code == status.HTTP_200_OK

        # Test different allowed MIME types
        allowed_types = ["application/pdf", "image/png", "image/jpeg", "image/jpg"]
        for mime_type in allowed_types:
            upload_data["mime_type"] = mime_type
            upload_data["file_name"] = f"test.{mime_type.split('/')[-1]}"
            
            with patch('api.endpoints.invoices.supabase') as mock_supabase:
                mock_supabase.storage.from_.return_value.create_signed_upload_url.return_value = {
                    "signedURL": "https://mock-url.com"
                }
                
                response = client.post(f"/api/v1/line-items/{test_forecast_item.id}/invoices:begin-upload", json=upload_data)
                assert response.status_code == status.HTTP_200_OK

    def test_storage_error_handling(self, client, test_forecast_item):
        """Test handling of Supabase storage errors"""
        upload_data = {
            "line_item_id": test_forecast_item.id,
            "file_name": "test_invoice.pdf",
            "mime_type": "application/pdf",
            "file_size": 1024
        }
        
        # Test storage failure during upload initiation
        with patch('api.endpoints.invoices.supabase') as mock_supabase:
            mock_supabase.storage.from_.return_value.create_signed_upload_url.return_value = None
            
            response = client.post(f"/api/v1/line-items/{test_forecast_item.id}/invoices:begin-upload", json=upload_data)
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR

    def test_orphan_cleanup_scenario(self, client, test_invoice_pending):
        """Test scenario where file upload fails but database record exists"""
        # Simulate file not found in storage during completion
        with patch('api.endpoints.invoices.supabase') as mock_supabase:
            mock_supabase.storage.from_.return_value.get_public_url.return_value = None
            
            response = client.post(f"/api/line-items/{test_invoice_pending.line_item_id}/invoices/{test_invoice_pending.id}:complete")
            
            assert response.status_code == status.HTTP_400_BAD_REQUEST
            assert "not found in storage" in response.json()["detail"]

import pytest
from fastapi import status
from unittest.mock import Mock, patch
import json


class TestAuthenticationRouters:
    """Test authentication endpoints"""

    def test_register_success(self, client, mock_supabase):
        """Test successful user registration"""
        # Mock successful registration
        mock_user = Mock()
        mock_user.user.id = "new-user-id"
        mock_user.user.email = "newuser@example.com"
        
        mock_supabase.auth.admin.get_user_by_email.return_value = Mock(user=None)
        mock_supabase.auth.admin.create_user.return_value = mock_user
        
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "newuser@example.com",
                "password": "testpassword123",
                "user_metadata": {"name": "Test User"}
            }
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["message"] == "User created successfully"
        assert data["email"] == "newuser@example.com"

    def test_register_existing_user(self, client, mock_supabase):
        """Test registration with existing email"""
        # Mock existing user
        existing_user = Mock()
        existing_user.user.email = "existing@example.com"
        mock_supabase.auth.admin.get_user_by_email.return_value = existing_user
        
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "existing@example.com",
                "password": "testpassword123"
            }
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert "Email already registered" in data["detail"]

    def test_register_invalid_data(self, client):
        """Test registration with invalid data"""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "invalid-email",
                "password": ""
            }
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_login_success(self, client, mock_supabase):
        """Test successful login"""
        # Mock successful login
        mock_user = Mock()
        mock_user.user.id = "user-id"
        mock_user.user.email = "test@example.com"
        mock_session = Mock()
        mock_session.access_token = "access-token"
        mock_session.refresh_token = "refresh-token"
        
        mock_response = Mock()
        mock_response.user = mock_user.user
        mock_response.session = mock_session
        
        mock_supabase.auth.sign_in_with_password.return_value = mock_response
        
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "test@example.com",
                "password": "testpassword123"
            }
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert data["user"]["email"] == "test@example.com"

    def test_login_invalid_credentials(self, client, mock_supabase):
        """Test login with invalid credentials"""
        # Mock failed login
        mock_supabase.auth.sign_in_with_password.side_effect = Exception("Invalid credentials")
        
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "test@example.com",
                "password": "wrongpassword"
            }
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_refresh_token_success(self, client, mock_supabase):
        """Test successful token refresh"""
        # Mock successful refresh
        mock_session = Mock()
        mock_session.access_token = "new-access-token"
        mock_session.refresh_token = "new-refresh-token"
        
        mock_response = Mock()
        mock_response.session = mock_session
        
        mock_supabase.auth.refresh_session.return_value = mock_response
        
        response = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": "valid-refresh-token"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["access_token"] == "new-access-token"
        assert data["refresh_token"] == "new-refresh-token"

    def test_refresh_token_invalid(self, client, mock_supabase):
        """Test token refresh with invalid token"""
        # Mock failed refresh
        mock_supabase.auth.refresh_session.side_effect = Exception("Invalid refresh token")
        
        response = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": "invalid-refresh-token"}
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_logout_success(self, client, mock_supabase):
        """Test successful logout"""
        mock_supabase.auth.sign_out.return_value = None
        
        response = client.post("/api/v1/auth/logout")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["message"] == "Successfully logged out"

    @patch('routers.get_current_user_http')
    async def test_get_current_user_http_success(self, mock_get_user, client):
        """Test successful user authentication"""
        from routers import get_current_user_http
        from fastapi.security import HTTPAuthorizationCredentials
        
        # Mock authorization credentials
        mock_creds = Mock(spec=HTTPAuthorizationCredentials)
        mock_creds.credentials = "valid-token"
        
        # Mock Supabase user response
        with patch('routers.supabase') as mock_supabase:
            mock_user = Mock()
            mock_user.user.id = "user-id"
            mock_user.user.email = "test@example.com"
            mock_user.user.role = "authenticated"
            mock_supabase.auth.get_user.return_value = mock_user
            
            result = await get_current_user_http(mock_creds)
            
            assert result['id'] == "user-id"
            assert result['email'] == "test@example.com"
            assert result['role'] == "authenticated"
            assert result['token'] == "valid-token"

    @patch('routers.get_current_user_http')
    async def test_get_current_user_http_invalid_token(self, mock_get_user, client):
        """Test authentication with invalid token"""
        from routers import get_current_user_http
        from fastapi.security import HTTPAuthorizationCredentials
        from fastapi import HTTPException
        
        # Mock authorization credentials
        mock_creds = Mock(spec=HTTPAuthorizationCredentials)
        mock_creds.credentials = "invalid-token"
        
        # Mock Supabase error
        with patch('routers.supabase') as mock_supabase:
            mock_supabase.auth.get_user.side_effect = Exception("Invalid token")
            
            with pytest.raises(HTTPException) as exc_info:
                await get_current_user_http(mock_creds)
            
            assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
            assert "Could not validate credentials" in str(exc_info.value.detail)

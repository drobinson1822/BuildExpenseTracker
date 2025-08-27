"""Mock Supabase client for testing"""
from unittest.mock import Mock

# Create mock Supabase client
mock_supabase = Mock()
mock_supabase.auth = Mock()
mock_supabase.auth.get_user = Mock()
mock_supabase.auth.admin = Mock()
mock_supabase.auth.admin.get_user_by_email = Mock()
mock_supabase.auth.admin.create_user = Mock()
mock_supabase.auth.sign_in_with_password = Mock()
mock_supabase.auth.refresh_session = Mock()
mock_supabase.auth.sign_out = Mock()

# Mock admin client
mock_supabase_admin = Mock()
mock_supabase_admin.auth = mock_supabase.auth

# Mock get_current_user function
def mock_get_current_user():
    return {
        'id': 'test-user-id',
        'email': 'test@example.com',
        'role': 'authenticated',
        'token': 'mock-token'
    }

# Export mocks
supabase = mock_supabase
supabase_admin = mock_supabase_admin
get_current_user = mock_get_current_user

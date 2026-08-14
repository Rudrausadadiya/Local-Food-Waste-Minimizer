import pytest
from rest_framework.test import APIClient
from apps.users.models import User
from apps.users.choices import UserRole

@pytest.fixture
# Function: api_client
def api_client():
    """Returns a DRF API client instance."""
    return APIClient()

@pytest.fixture
# Function: create_user
def create_user(db):
    """Factory to create a user."""
    # Method: make_user
    def make_user(**kwargs):
        kwargs.setdefault('password', 'StrongPass123!')
        kwargs.setdefault('email', 'test@example.com')
        kwargs.setdefault('first_name', 'Test')
        kwargs.setdefault('last_name', 'User')
        
        password = kwargs.pop('password')
        user = User.objects.create(**kwargs)
        user.set_password(password)
        user.save()
        return user
    return make_user

@pytest.fixture
# Function: active_user
def active_user(create_user):
    """Returns an active, email-verified user."""
    return create_user(
        email='active@example.com', 
        is_active=True, 
        is_email_verified=True
    )

@pytest.fixture
# Function: admin_user
def admin_user(create_user):
    """Returns an admin user."""
    return create_user(
        email='admin@example.com',
        role=UserRole.ADMIN,
        is_staff=True,
        is_superuser=True
    )

@pytest.fixture
# Function: auth_client
def auth_client(api_client, active_user):
    """Returns an API client authenticated with a valid user."""
    from rest_framework_simplejwt.tokens import RefreshToken
    refresh = RefreshToken.for_user(active_user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    return api_client, active_user

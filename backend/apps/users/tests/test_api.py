import pytest
from django.urls import reverse
from rest_framework import status
from apps.users.models import User

@pytest.mark.django_db
class TestAuthenticationAPI:

    def test_registration_success(self, api_client):
        """Test successful user registration."""
        url = reverse('users:register')
        payload = {
            'email': 'newuser@example.com',
            'password': 'StrongPassword123!',
            'first_name': 'New',
            'last_name': 'User'
        }
        
        response = api_client.post(url, data=payload, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['success'] is True
        assert response.data['data']['email'] == 'newuser@example.com'
        assert 'password' not in response.data['data']
        assert User.objects.filter(email='newuser@example.com').exists()

    def test_registration_validation_error(self, api_client):
        """Test registration fails with weak password and invalid email."""
        url = reverse('users:register')
        payload = {
            'email': 'not-an-email',
            'password': '123',  # Too short, fully numeric
            'first_name': '',
            'last_name': ''
        }
        
        response = api_client.post(url, data=payload, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['success'] is False
        assert 'email' in response.data['errors']
        assert 'password' in response.data['errors']
        assert 'first_name' in response.data['errors']

    def test_registration_duplicate_email(self, api_client, active_user):
        """Test registration fails if email is already taken."""
        url = reverse('users:register')
        payload = {
            'email': active_user.email,
            'password': 'StrongPassword123!',
            'first_name': 'Copy',
            'last_name': 'Cat'
        }
        
        response = api_client.post(url, data=payload, format='json')
        
        assert response.status_code == status.HTTP_409_CONFLICT
        assert response.data['code'] == 'user_already_exists'

    def test_login_success(self, api_client, active_user):
        """Test successful login returns tokens."""
        url = reverse('users:login')
        payload = {
            'email': active_user.email,
            'password': 'StrongPass123!'
        }
        
        response = api_client.post(url, data=payload, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] is True
        assert 'access' in response.data['data']['tokens']
        assert 'refresh' in response.data['data']['tokens']
        assert response.data['data']['user']['email'] == active_user.email

    def test_login_invalid_credentials(self, api_client, active_user):
        """Test login fails with incorrect password."""
        url = reverse('users:login')
        payload = {
            'email': active_user.email,
            'password': 'WrongPassword123!'
        }
        
        response = api_client.post(url, data=payload, format='json')
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.data['code'] == 'invalid_credentials'

    def test_jwt_refresh(self, api_client, active_user):
        """Test refreshing the JWT access token."""
        # First login
        login_response = api_client.post(reverse('users:login'), {
            'email': active_user.email,
            'password': 'StrongPass123!'
        }, format='json')
        
        refresh_token = login_response.data['data']['tokens']['refresh']
        
        # Then refresh
        refresh_url = reverse('users:token_refresh')
        response = api_client.post(refresh_url, {'refresh': refresh_token}, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data

    def test_profile_authenticated(self, auth_client):
        """Test viewing profile when authenticated."""
        client, user = auth_client
        url = reverse('users:profile')
        
        response = client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['data']['email'] == user.email

    def test_profile_unauthenticated(self, api_client):
        """Test viewing profile fails when not authenticated."""
        url = reverse('users:profile')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_email_verification(self, api_client, create_user):
        """Test verifying an email address."""
        unverified = create_user(email="unverified@example.com", is_email_verified=False)
        url = reverse('users:verify_email')
        
        from django.utils.http import urlsafe_base64_encode
        from django.utils.encoding import force_bytes
        from django.contrib.auth.tokens import default_token_generator
        
        uid = urlsafe_base64_encode(force_bytes(unverified.id))
        token = default_token_generator.make_token(unverified)
        
        payload = {'uidb64': uid, 'token': token}
        response = api_client.post(url, data=payload, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        
        # Refresh from db
        unverified.refresh_from_db()
        assert unverified.is_email_verified is True

    def test_password_reset(self, api_client, active_user):
        """Test resetting password with a valid token."""
        url = reverse('users:reset_password')
        
        from django.utils.http import urlsafe_base64_encode
        from django.utils.encoding import force_bytes
        from django.contrib.auth.tokens import default_token_generator
        
        uid = urlsafe_base64_encode(force_bytes(active_user.id))
        token = default_token_generator.make_token(active_user)
        
        payload = {
            'uidb64': uid,
            'token': token,
            'new_password': 'NewSuperStrongPassword123!'
        }
        
        response = api_client.post(url, data=payload, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        
        # Verify the new password works
        active_user.refresh_from_db()
        assert active_user.check_password('NewSuperStrongPassword123!') is True

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from apps.business.models import Business

User = get_user_model()

# Class: TestAuthenticationAPI
class TestAuthenticationAPI(APITestCase):

    # Method: setUp
    def setUp(self):
        self.active_user = User.objects.create_user(
            email='activeuser@example.com',
            password='StrongPass123!',
            first_name='Active',
            last_name='User',
            is_active=True,
            is_email_verified=True
        )

    # Method: test_registration_success
    def test_registration_success(self):
        """Test successful user registration."""
        url = reverse('users:register')
        payload = {
            'email': 'newuser@example.com',
            'password': 'StrongPassword123!',
            'first_name': 'New',
            'last_name': 'User'
        }
        
        response = self.client.post(url, data=payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['data']['email'], 'newuser@example.com')
        self.assertNotIn('password', response.data['data'])
        self.assertTrue(User.objects.filter(email='newuser@example.com').exists())

    # Method: test_registration_validation_error
    def test_registration_validation_error(self):
        """Test registration fails with weak password and invalid email."""
        url = reverse('users:register')
        payload = {
            'email': 'not-an-email',
            'password': '123',
            'first_name': '',
            'last_name': ''
        }
        
        response = self.client.post(url, data=payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
        self.assertIn('email', response.data['errors'])
        self.assertIn('password', response.data['errors'])
        self.assertIn('first_name', response.data['errors'])

    # Method: test_registration_duplicate_email
    def test_registration_duplicate_email(self):
        """Test registration fails if email is already taken."""
        url = reverse('users:register')
        payload = {
            'email': self.active_user.email,
            'password': 'StrongPassword123!',
            'first_name': 'Copy',
            'last_name': 'Cat'
        }
        
        response = self.client.post(url, data=payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(response.data['code'], 'user_already_exists')

    # Method: test_login_success
    def test_login_success(self):
        """Test successful login returns tokens."""
        url = reverse('users:login')
        payload = {
            'email': self.active_user.email,
            'password': 'StrongPass123!'
        }
        
        response = self.client.post(url, data=payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertIn('access', response.data['data']['tokens'])
        self.assertIn('refresh', response.data['data']['tokens'])
        self.assertEqual(response.data['data']['user']['email'], self.active_user.email)

    # Method: test_login_invalid_credentials
    def test_login_invalid_credentials(self):
        """Test login fails with incorrect password."""
        url = reverse('users:login')
        payload = {
            'email': self.active_user.email,
            'password': 'WrongPassword123!'
        }
        
        response = self.client.post(url, data=payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['code'], 'invalid_credentials')

    # Method: test_jwt_refresh
    def test_jwt_refresh(self):
        """Test refreshing the JWT access token."""
        login_response = self.client.post(reverse('users:login'), {
            'email': self.active_user.email,
            'password': 'StrongPass123!'
        }, format='json')
        
        refresh_token = login_response.data['data']['tokens']['refresh']
        
        refresh_url = reverse('users:token_refresh')
        response = self.client.post(refresh_url, {'refresh': refresh_token}, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)

    # Method: test_profile_authenticated
    def test_profile_authenticated(self):
        """Test viewing profile when authenticated."""
        self.client.force_authenticate(user=self.active_user)
        url = reverse('users:profile')
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['email'], self.active_user.email)

    # Method: test_profile_unauthenticated
    def test_profile_unauthenticated(self):
        """Test viewing profile fails when not authenticated."""
        url = reverse('users:profile')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # Method: test_email_verification
    def test_email_verification(self):
        """Test verifying an email address."""
        unverified = User.objects.create_user(
            email="unverified@example.com",
            password="StrongPassword123!",
            is_email_verified=False
        )
        url = reverse('users:verify_email')
        
        uid = urlsafe_base64_encode(force_bytes(unverified.id))
        token = default_token_generator.make_token(unverified)
        
        payload = {'uidb64': uid, 'token': token}
        response = self.client.post(url, data=payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        unverified.refresh_from_db()
        self.assertTrue(unverified.is_email_verified)

    # Method: test_password_reset
    def test_password_reset(self):
        """Test resetting password with a valid token."""
        url = reverse('users:reset_password')
        
        uid = urlsafe_base64_encode(force_bytes(self.active_user.id))
        token = default_token_generator.make_token(self.active_user)
        
        payload = {
            'uidb64': uid,
            'token': token,
            'new_password': 'NewSuperStrongPassword123!'
        }
        
        response = self.client.post(url, data=payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.active_user.refresh_from_db()
        self.assertTrue(self.active_user.check_password('NewSuperStrongPassword123!'))

    # Method: test_vendor_and_ngo_registration_creates_pending_business
    def test_vendor_and_ngo_registration_creates_pending_business(self):
        """Test vendor and NGO registration initializes business profile as PENDING."""
        url = reverse('users:register')
        vendor_payload = {
            'email': 'bakery@example.com',
            'password': 'StrongPassword123!',
            'first_name': 'Baker',
            'last_name': 'Smith',
            'role': 'VENDOR',
            'business_name': 'Bakery Delight',
            'registration_number': 'FSSAI123456789'
        }
        res = self.client.post(url, data=vendor_payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data['data']['business_status'], 'PENDING')

        ngo_payload = {
            'email': 'rescue@example.com',
            'password': 'StrongPassword123!',
            'first_name': 'Rescue',
            'last_name': 'Team',
            'role': 'NGO',
            'business_name': 'Food Care Org',
            'registration_number': 'DARPAN9876'
        }
        res2 = self.client.post(url, data=ngo_payload, format='json')
        self.assertEqual(res2.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res2.data['data']['business_status'], 'PENDING')

    # Method: test_vendor_and_ngo_credential_privacy_isolation
    def test_vendor_and_ngo_credential_privacy_isolation(self):
        """Test each vendor/NGO can only see their own business details and credentials."""
        vendor1 = User.objects.create_user(email="v1@example.com", password="Pass123!", role="VENDOR")
        vendor2 = User.objects.create_user(email="v2@example.com", password="Pass123!", role="VENDOR")

        biz1 = Business.objects.create(owner=vendor1, business_name="V1 Biz", slug="v1-biz", business_email="v1@biz.com", business_phone="1234567890")
        biz2 = Business.objects.create(owner=vendor2, business_name="V2 Biz", slug="v2-biz", business_email="v2@biz.com", business_phone="0987654321")

        self.client.force_authenticate(user=vendor1)
        res = self.client.get('/api/v1/business/businesses/')
        items = res.data.get('data', res.data) if isinstance(res.data, dict) else res.data
        if isinstance(items, dict) and 'results' in items:
            items = items['results']
        ids = [str(b['id']) for b in items]
        self.assertIn(str(biz1.id), ids)
        self.assertNotIn(str(biz2.id), ids)

    # Method: test_login_rate_limiting
    def test_login_rate_limiting(self):
        """Test that LoginAPIView returns HTTP 429 Too Many Requests when rate limit is exceeded."""
        url = '/api/v1/users/auth/login/'
        payload = {'email': self.active_user.email, 'password': 'StrongPass123!'}

        from django.core.cache import cache
        cache.clear()

        try:
            responses = [self.client.post(url, data=payload, format='json') for _ in range(11)]
            status_codes = [r.status_code for r in responses]
            self.assertIn(status.HTTP_429_TOO_MANY_REQUESTS, status_codes)
        finally:
            cache.clear()


from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from apps.users import views

app_name = 'users'

urlpatterns = [
    # Authentication Endpoints
    path('auth/register/', views.RegistrationAPIView.as_view(), name='register'),
    path('auth/login/', views.LoginAPIView.as_view(), name='login'),
    path('auth/logout/', views.LogoutAPIView.as_view(), name='logout'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Account Recovery & Verification
    path('auth/verify-email/', views.VerifyEmailAPIView.as_view(), name='verify_email'),
    path('auth/forgot-password/', views.ForgotPasswordAPIView.as_view(), name='forgot_password'),
    path('auth/reset-password/', views.ResetPasswordAPIView.as_view(), name='reset_password'),
    
    # Profile Endpoints
    path('profile/', views.ProfileAPIView.as_view(), name='profile'),

    # Admin User Management Endpoints
    path('admin/users/', views.AdminUserListView.as_view(), name='admin_user_list'),
    path('admin/users/<uuid:user_id>/toggle/', views.AdminUserToggleView.as_view(), name='admin_user_toggle'),
]

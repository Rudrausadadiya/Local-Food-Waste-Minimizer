from django.db import models
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.throttling import ScopedRateThrottle
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers

from common.responses import success_response
from apps.users.serializers import (
    RegistrationSerializer,
    LoginSerializer,
    ProfileSerializer,
    UpdateProfileSerializer,
    ForgotPasswordSerializer,
    ResetPasswordSerializer,
    VerifyEmailSerializer,
    LogoutSerializer
)
from apps.users.services import AuthService, UserService


# Class: RegistrationAPIView
class RegistrationAPIView(APIView):
    permission_classes = (AllowAny,)
    serializer_class = RegistrationSerializer

    @extend_schema(
        summary="Register a new user",
        request=RegistrationSerializer,
        responses={201: ProfileSerializer}
    )
    # Method: post
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = AuthService.register(
            email=serializer.validated_data['email'],
            password=serializer.validated_data['password'],
            first_name=serializer.validated_data['first_name'],
            last_name=serializer.validated_data['last_name'],
            role=serializer.validated_data.get('role', 'CUSTOMER'),
            business_name=serializer.validated_data.get('business_name'),
            business_type=serializer.validated_data.get('business_type'),
            registration_number=serializer.validated_data.get('registration_number'),
            gst_number=serializer.validated_data.get('gst_number')
        )
        
        return success_response(
            data=ProfileSerializer(user).data,
            message="User registered successfully.",
            status_code=status.HTTP_201_CREATED
        )


# Class: LoginAPIView
class LoginAPIView(APIView):
    permission_classes = (AllowAny,)
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'login'
    serializer_class = LoginSerializer

    @extend_schema(
        summary="Login user",
        request=LoginSerializer,
        responses={
            200: inline_serializer(
                name='LoginResponse',
                fields={
                    'user': ProfileSerializer(),
                    'tokens': serializers.DictField(child=serializers.CharField())
                }
            )
        }
    )
    # Method: post
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user, tokens = AuthService.login(
            email=serializer.validated_data['email'],
            password=serializer.validated_data['password']
        )
        
        return success_response(
            data={
                "user": ProfileSerializer(user).data,
                "tokens": tokens
            },
            message="Login successful."
        )


# Class: LogoutAPIView
class LogoutAPIView(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = LogoutSerializer

    @extend_schema(
        summary="Logout user",
        request=LogoutSerializer,
        responses={200: inline_serializer(name='LogoutResponse', fields={'success': serializers.BooleanField()})}
    )
    # Method: post
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Blacklist the refresh token
        from rest_framework_simplejwt.tokens import RefreshToken
        try:
            token = RefreshToken(serializer.validated_data['refresh'])
            token.blacklist()
        except Exception:
            # We silently ignore invalid/already blacklisted tokens on logout
            pass
            
        return success_response(message="Logged out successfully.")


# Class: VerifyEmailAPIView
class VerifyEmailAPIView(APIView):
    permission_classes = (AllowAny,)
    serializer_class = VerifyEmailSerializer

    @extend_schema(
        summary="Verify user email",
        request=VerifyEmailSerializer,
        responses={200: inline_serializer(name='VerifyEmailResponse', fields={'success': serializers.BooleanField()})}
    )
    # Method: post
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        AuthService.verify_email(
            uidb64=serializer.validated_data['uidb64'],
            token=serializer.validated_data['token']
        )
            
        return success_response(message="Email verified successfully.")


# Class: ForgotPasswordAPIView
class ForgotPasswordAPIView(APIView):
    permission_classes = (AllowAny,)
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'forgot_password'
    serializer_class = ForgotPasswordSerializer

    @extend_schema(
        summary="Request password reset",
        request=ForgotPasswordSerializer,
        responses={200: inline_serializer(name='ForgotPwdResponse', fields={'success': serializers.BooleanField()})}
    )
    # Method: post
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        AuthService.request_password_reset(
            email=serializer.validated_data['email']
        )
        
        return success_response(
            message="If an account with that email exists, a password reset link has been sent."
        )


# Class: ResetPasswordAPIView
class ResetPasswordAPIView(APIView):
    permission_classes = (AllowAny,)
    serializer_class = ResetPasswordSerializer

    @extend_schema(
        summary="Reset password",
        request=ResetPasswordSerializer,
        responses={200: inline_serializer(name='ResetPwdResponse', fields={'success': serializers.BooleanField()})}
    )
    # Method: post
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        AuthService.reset_password(
            uidb64=serializer.validated_data['uidb64'],
            token=serializer.validated_data['token'],
            new_password=serializer.validated_data['new_password']
        )
            
        return success_response(message="Password reset successfully.")


# Class: ProfileAPIView
class ProfileAPIView(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = ProfileSerializer

    @extend_schema(
        summary="Get user profile",
        responses={200: ProfileSerializer}
    )
    # Method: get
    def get(self, request, *args, **kwargs):
        return success_response(
            data=self.serializer_class(request.user).data,
            message="Profile retrieved successfully."
        )

    @extend_schema(
        summary="Update user profile (Complete)",
        request=UpdateProfileSerializer,
        responses={200: ProfileSerializer}
    )
    # Method: put
    def put(self, request, *args, **kwargs):
        serializer = UpdateProfileSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = UserService.update_profile(
            user_id=request.user.id,
            update_data=serializer.validated_data
        )
        
        return success_response(
            data=self.serializer_class(user).data,
            message="Profile updated successfully."
        )

    @extend_schema(
        summary="Update user profile (Partial)",
        request=UpdateProfileSerializer,
        responses={200: ProfileSerializer}
    )
    # Method: patch
    def patch(self, request, *args, **kwargs):
        serializer = UpdateProfileSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        
        user = UserService.update_profile(
            user_id=request.user.id,
            update_data=serializer.validated_data
        )
        
        return success_response(
            data=self.serializer_class(user).data,
            message="Profile updated successfully."
        )

    @extend_schema(
        summary="Deactivate user profile",
        responses={200: inline_serializer(name='DeactivateResponse', fields={'success': serializers.BooleanField()})}
    )
    # Method: delete
    def delete(self, request, *args, **kwargs):
        UserService.deactivate_account(user_id=request.user.id)
        return success_response(message="Account deactivated successfully.")


# Class: AdminUserListView
class AdminUserListView(APIView):
    """Admin-only: List all registered users with optional role filter."""
    permission_classes = (IsAuthenticated,)

    # Method: get
    def get(self, request, *args, **kwargs):
        if not (request.user.is_staff or getattr(request.user, 'role', '') == 'ADMIN'):
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Admin access required.")
        
        from apps.users.models import User as UserModel
        qs = UserModel.objects.all().order_by('-created_at')
        
        role = request.query_params.get('role')
        if role and role != 'ALL':
            qs = qs.filter(role=role)
        
        search = request.query_params.get('search', '').strip()
        if search:
            qs = qs.filter(
                models.Q(email__icontains=search) |
                models.Q(first_name__icontains=search) |
                models.Q(last_name__icontains=search)
            )
        
        return success_response(
            data=ProfileSerializer(qs, many=True).data,
            message="Users retrieved successfully."
        )


# Class: AdminUserToggleView
class AdminUserToggleView(APIView):
    """Admin-only: Activate or deactivate a user account."""
    permission_classes = (IsAuthenticated,)

    # Method: post
    def post(self, request, user_id, *args, **kwargs):
        if not (request.user.is_staff or getattr(request.user, 'role', '') == 'ADMIN'):
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Admin access required.")
        
        from apps.users.models import User as UserModel
        try:
            target_user = UserModel.objects.get(id=user_id)
        except UserModel.DoesNotExist:
            return success_response(message="User not found.", status_code=status.HTTP_404_NOT_FOUND)
        
        is_active = request.data.get('is_active')
        if is_active is None:
            is_active = not target_user.is_active
        
        target_user.is_active = bool(is_active)
        target_user.save(update_fields=['is_active'])
        
        # Sync associated Business and NGO statuses
        from apps.business.models import Business
        from apps.donations.models import NGO, NGOVerificationStatus

        if target_user.role in ['VENDOR', 'NGO']:
            biz_status = Business.BusinessStatus.APPROVED if target_user.is_active else Business.BusinessStatus.SUSPENDED
            Business.objects.filter(owner=target_user).update(
                business_status=biz_status,
                is_active=target_user.is_active,
                is_verified=target_user.is_active
            )
            if target_user.role == 'NGO':
                ngo_status = NGOVerificationStatus.VERIFIED if target_user.is_active else NGOVerificationStatus.REJECTED
                NGO.objects.filter(user=target_user).update(
                    verification_status=ngo_status,
                    is_active=target_user.is_active
                )
        
        return success_response(
            data=ProfileSerializer(target_user).data,
            message=f"User {'activated' if target_user.is_active else 'deactivated'} successfully."
        )

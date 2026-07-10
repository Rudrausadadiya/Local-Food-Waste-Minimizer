from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenRefreshView
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
from apps.users.exceptions import UserException


class RegistrationAPIView(APIView):
    permission_classes = (AllowAny,)
    serializer_class = RegistrationSerializer

    @extend_schema(
        summary="Register a new user",
        request=RegistrationSerializer,
        responses={201: ProfileSerializer}
    )
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = AuthService.register(
            email=serializer.validated_data['email'],
            password=serializer.validated_data['password'],
            first_name=serializer.validated_data['first_name'],
            last_name=serializer.validated_data['last_name']
        )
        
        return success_response(
            data=ProfileSerializer(user).data,
            message="User registered successfully.",
            status_code=status.HTTP_201_CREATED
        )


class LoginAPIView(APIView):
    permission_classes = (AllowAny,)
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


class LogoutAPIView(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = LogoutSerializer

    @extend_schema(
        summary="Logout user",
        request=LogoutSerializer,
        responses={200: inline_serializer(name='LogoutResponse', fields={'success': serializers.BooleanField()})}
    )
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


class VerifyEmailAPIView(APIView):
    permission_classes = (AllowAny,)
    serializer_class = VerifyEmailSerializer

    @extend_schema(
        summary="Verify user email",
        request=VerifyEmailSerializer,
        responses={200: inline_serializer(name='VerifyEmailResponse', fields={'success': serializers.BooleanField()})}
    )
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        AuthService.verify_email(
            uidb64=serializer.validated_data['uidb64'],
            token=serializer.validated_data['token']
        )
            
        return success_response(message="Email verified successfully.")


class ForgotPasswordAPIView(APIView):
    permission_classes = (AllowAny,)
    serializer_class = ForgotPasswordSerializer

    @extend_schema(
        summary="Request password reset",
        request=ForgotPasswordSerializer,
        responses={200: inline_serializer(name='ForgotPwdResponse', fields={'success': serializers.BooleanField()})}
    )
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        AuthService.request_password_reset(
            email=serializer.validated_data['email']
        )
        
        return success_response(
            message="If an account with that email exists, a password reset link has been sent."
        )


class ResetPasswordAPIView(APIView):
    permission_classes = (AllowAny,)
    serializer_class = ResetPasswordSerializer

    @extend_schema(
        summary="Reset password",
        request=ResetPasswordSerializer,
        responses={200: inline_serializer(name='ResetPwdResponse', fields={'success': serializers.BooleanField()})}
    )
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        AuthService.reset_password(
            uidb64=serializer.validated_data['uidb64'],
            token=serializer.validated_data['token'],
            new_password=serializer.validated_data['new_password']
        )
            
        return success_response(message="Password reset successfully.")


class ProfileAPIView(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = ProfileSerializer

    @extend_schema(
        summary="Get user profile",
        responses={200: ProfileSerializer}
    )
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
    def delete(self, request, *args, **kwargs):
        UserService.deactivate_account(user_id=request.user.id)
        return success_response(message="Account deactivated successfully.")

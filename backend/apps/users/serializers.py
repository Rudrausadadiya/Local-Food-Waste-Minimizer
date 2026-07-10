from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from drf_spectacular.utils import extend_schema_serializer, OpenApiExample

from apps.users.models import User
from apps.users.choices import UserRole

@extend_schema_serializer(
    examples=[
        OpenApiExample(
            'Valid Registration',
            value={
                'email': 'user@example.com',
                'password': 'StrongPassword123!',
                'first_name': 'John',
                'last_name': 'Doe'
            },
            request_only=True,
        )
    ]
)
class RegistrationSerializer(serializers.Serializer):
    """
    Serializer for validating user registration input.
    """
    email = serializers.EmailField(required=True, max_length=255)
    password = serializers.CharField(
        write_only=True, 
        required=True, 
        style={'input_type': 'password'}
    )
    first_name = serializers.CharField(required=True, max_length=150)
    last_name = serializers.CharField(required=True, max_length=150)
    
    def validate_password(self, value):
        """Apply Django's robust password validation."""
        try:
            validate_password(value)
        except DjangoValidationError as e:
            raise serializers.ValidationError(list(e.messages))
        return value

@extend_schema_serializer(
    examples=[
        OpenApiExample(
            'Valid Login',
            value={
                'email': 'user@example.com',
                'password': 'StrongPassword123!'
            },
            request_only=True,
        )
    ]
)
class LoginSerializer(serializers.Serializer):
    """
    Serializer for validating user login credentials.
    """
    email = serializers.EmailField(required=True)
    password = serializers.CharField(
        write_only=True, 
        required=True, 
        style={'input_type': 'password'}
    )

class ProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for displaying user profile information.
    """
    role_display = serializers.CharField(source='get_role_display', read_only=True)

    class Meta:
        model = User
        fields = (
            'id', 
            'email', 
            'first_name', 
            'last_name', 
            'phone_number', 
            'profile_image', 
            'role', 
            'role_display',
            'is_email_verified',
            'created_at'
        )
        read_only_fields = fields

@extend_schema_serializer(
    examples=[
        OpenApiExample(
            'Valid Profile Update',
            value={
                'first_name': 'Jane',
                'last_name': 'Smith',
                'phone_number': '+1234567890'
            },
            request_only=True,
        )
    ]
)
class UpdateProfileSerializer(serializers.Serializer):
    """
    Serializer for validating profile update input.
    """
    first_name = serializers.CharField(required=False, max_length=150)
    last_name = serializers.CharField(required=False, max_length=150)
    phone_number = serializers.CharField(required=False, max_length=20)

@extend_schema_serializer(
    examples=[
        OpenApiExample(
            'Forgot Password',
            value={
                'email': 'user@example.com'
            },
            request_only=True,
        )
    ]
)
class ForgotPasswordSerializer(serializers.Serializer):
    """
    Serializer for validating the forgot password request.
    """
    email = serializers.EmailField(required=True)

@extend_schema_serializer(
    examples=[
        OpenApiExample(
            'Reset Password',
            value={
                'uidb64': 'MQ',
                'token': 'abc123xyz456',
                'new_password': 'NewStrongPassword123!'
            },
            request_only=True,
        )
    ]
)
class ResetPasswordSerializer(serializers.Serializer):
    """
    Serializer for validating the password reset action.
    """
    uidb64 = serializers.CharField(required=True)
    token = serializers.CharField(required=True)
    new_password = serializers.CharField(
        write_only=True, 
        required=True, 
        style={'input_type': 'password'}
    )

    def validate_new_password(self, value):
        """Apply Django's robust password validation."""
        try:
            validate_password(value)
        except DjangoValidationError as e:
            raise serializers.ValidationError(list(e.messages))
        return value

@extend_schema_serializer(
    examples=[
        OpenApiExample(
            'Verify Email',
            value={
                'uidb64': 'MQ',
                'token': 'email-verification-token-123'
            },
            request_only=True,
        )
    ]
)
class VerifyEmailSerializer(serializers.Serializer):
    """
    Serializer for validating the email verification token.
    """
    uidb64 = serializers.CharField(required=True)
    token = serializers.CharField(required=True)

@extend_schema_serializer(
    examples=[
        OpenApiExample(
            'Logout',
            value={
                'refresh': 'your-refresh-token-here'
            },
            request_only=True,
        )
    ]
)
class LogoutSerializer(serializers.Serializer):
    """
    Serializer for validating the logout request (refresh token blacklisting).
    """
    refresh = serializers.CharField(required=True)

import uuid
from typing import Dict, Any, Tuple
from django.db import transaction
from django.contrib.auth import authenticate
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from rest_framework_simplejwt.tokens import RefreshToken

from apps.users.models import User
from apps.users.repositories import UserRepository
from apps.users.exceptions import (
    UserNotFound, 
    UserAlreadyExists, 
    InvalidCredentials,
    EmailNotVerified,
    AccountInactive
)
from apps.users.choices import UserRole

class AuthService:
    """
    Service layer handling authentication, registration, and account recovery.
    Contains core business logic for authentication.
    """

    @staticmethod
    @transaction.atomic
    def register(email: str, password: str, first_name: str, last_name: str, role: str = UserRole.CUSTOMER) -> User:
        """
        Register a new user in the system.
        
        Args:
            email (str): User's email.
            password (str): User's raw password.
            first_name (str): User's first name.
            last_name (str): User's last name.
            role (str, optional): User's role. Defaults to CUSTOMER.
            
        Returns:
            User: The newly registered user.
            
        Raises:
            UserAlreadyExists: If a user with the provided email already exists.
        """
        existing_user = UserRepository.get_by_email(email)
        if existing_user:
            raise UserAlreadyExists()

        user = UserRepository.create_user(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            role=role
        )
        
        # In a real scenario, trigger a celery task to send a verification email here.
        
        return user

    @staticmethod
    def login(email: str, password: str) -> Tuple[User, Dict[str, str]]:
        """
        Authenticate a user and return JWT tokens.
        
        Args:
            email (str): User's email.
            password (str): User's password.
            
        Returns:
            Tuple[User, Dict[str, str]]: The authenticated user and a dictionary containing access and refresh tokens.
            
        Raises:
            InvalidCredentials: If authentication fails.
            AccountInactive: If the user's account is deactivated.
            EmailNotVerified: If the user hasn't verified their email (optional business rule).
        """
        user = authenticate(email=email, password=password)
        
        if not user:
            raise InvalidCredentials()
            
        if not user.is_active:
            raise AccountInactive()
            
        # Optional: Require email verification before login
        # if not user.is_email_verified:
        #     raise EmailNotVerified()

        refresh = RefreshToken.for_user(user)
        tokens = {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
        
        return user, tokens

    @staticmethod
    @transaction.atomic
    def verify_email(uidb64: str, token: str) -> User:
        """
        Mark a user's email as verified via a cryptographic token.
        
        Args:
            uidb64 (str): Base64 encoded user ID.
            token (str): Cryptographic verification token.
            
        Returns:
            User: The updated user.
            
        Raises:
            UserNotFound: If the user does not exist or token is invalid.
        """
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = UserRepository.get_by_id(uuid.UUID(uid))
        except (TypeError, ValueError, OverflowError):
            user = None

        if not user or not default_token_generator.check_token(user, token):
            raise UserNotFound(detail="Invalid or expired verification link.")
            
        return UserRepository.verify_email(user)

    @staticmethod
    def request_password_reset(email: str) -> None:
        """
        Initiate a password reset process.
        
        Args:
            email (str): The email address of the user requesting a reset.
        """
        user = UserRepository.get_by_email(email)
        if not user:
            # We don't raise an exception to prevent email enumeration attacks.
            return
            
        # In a real scenario, generate a token and trigger a celery task to send the reset email here.
        pass

    @staticmethod
    @transaction.atomic
    def reset_password(uidb64: str, token: str, new_password: str) -> User:
        """
        Reset a user's password securely via token.
        
        Args:
            uidb64 (str): Base64 encoded user ID.
            token (str): Cryptographic verification token.
            new_password (str): The new password.
            
        Returns:
            User: The updated user.
            
        Raises:
            UserNotFound: If the user does not exist or token is invalid.
        """
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = UserRepository.get_by_id(uuid.UUID(uid))
        except (TypeError, ValueError, OverflowError):
            user = None

        if not user or not default_token_generator.check_token(user, token):
            raise UserNotFound(detail="Invalid or expired reset link.")
            
        return UserRepository.update_password(user, new_password)


class UserService:
    """
    Service layer handling user profile management, role assignment, and status updates.
    """

    @staticmethod
    @transaction.atomic
    def update_profile(user_id: uuid.UUID, update_data: Dict[str, Any]) -> User:
        """
        Update a user's profile information.
        
        Args:
            user_id (uuid.UUID): The UUID of the user.
            update_data (Dict[str, Any]): The data to update.
            
        Returns:
            User: The updated user.
            
        Raises:
            UserNotFound: If the user does not exist.
        """
        # Ensure we don't accidentally update sensitive fields through this method
        safe_fields = {'first_name', 'last_name', 'phone_number'}
        filtered_data = {k: v for k, v in update_data.items() if k in safe_fields}

        user = UserRepository.get_by_id(user_id)
        if not user:
            raise UserNotFound()

        return UserRepository.update_user(user, filtered_data)

    @staticmethod
    @transaction.atomic
    def change_password(user_id: uuid.UUID, old_password: str, new_password: str) -> User:
        """
        Change a user's password when they are already authenticated.
        
        Args:
            user_id (uuid.UUID): The UUID of the user.
            old_password (str): The current password.
            new_password (str): The new password.
            
        Returns:
            User: The updated user.
            
        Raises:
            UserNotFound: If the user does not exist.
            InvalidCredentials: If the old password doesn't match.
        """
        user = UserRepository.get_by_id(user_id)
        if not user:
            raise UserNotFound()
            
        if not user.check_password(old_password):
            raise InvalidCredentials(detail="Old password is incorrect.")
            
        return UserRepository.update_password(user, new_password)

    @staticmethod
    @transaction.atomic
    def assign_role(user_id: uuid.UUID, new_role: str) -> User:
        """
        Assign a new role to a user.
        
        Args:
            user_id (uuid.UUID): The UUID of the user.
            new_role (str): The new role from UserRole choices.
            
        Returns:
            User: The updated user.
            
        Raises:
            UserNotFound: If the user does not exist.
            ValueError: If the role is invalid.
        """
        if new_role not in UserRole.values:
            raise ValueError(f"Invalid role. Must be one of {UserRole.values}")
            
        user = UserRepository.get_by_id(user_id)
        if not user:
            raise UserNotFound()
            
        return UserRepository.update_user(user, {'role': new_role})

    @staticmethod
    @transaction.atomic
    def deactivate_account(user_id: uuid.UUID) -> User:
        """
        Deactivate a user's account.
        
        Args:
            user_id (uuid.UUID): The UUID of the user.
            
        Returns:
            User: The deactivated user.
            
        Raises:
            UserNotFound: If the user does not exist.
        """
        user = UserRepository.get_by_id(user_id)
        if not user:
            raise UserNotFound()
            
        return UserRepository.deactivate_user(user)

    @staticmethod
    @transaction.atomic
    def activate_account(user_id: uuid.UUID) -> User:
        """
        Activate a user's account.
        
        Args:
            user_id (uuid.UUID): The UUID of the user.
            
        Returns:
            User: The activated user.
            
        Raises:
            UserNotFound: If the user does not exist.
        """
        user = UserRepository.get_by_id(user_id)
        if not user:
            raise UserNotFound()
            
        return UserRepository.activate_user(user)

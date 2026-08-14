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
    AccountInactive
)
from apps.users.choices import UserRole

# Class: AuthService
class AuthService:
    """
    Service layer handling authentication, registration, and account recovery.
    Contains core business logic for authentication.
    """

    @staticmethod
    @transaction.atomic
    # Method: register
    def register(
        email: str, 
        password: str, 
        first_name: str, 
        last_name: str, 
        role: str = UserRole.CUSTOMER,
        business_name: str = None,
        business_type: str = None,
        registration_number: str = None,
        gst_number: str = None
    ) -> User:
        """
        Register a new user in the system.
        
        Args:
            email (str): User's email.
            password (str): User's raw password.
            first_name (str): User's first name.
            last_name (str): User's last name.
            role (str, optional): User's role. Defaults to CUSTOMER.
            business_name (str, optional): Business or NGO name.
            business_type (str, optional): Specific business type.
            registration_number (str, optional): FSSAI / Darpan registration ID.
            gst_number (str, optional): GSTIN / 80G tax cert ID.
            
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
        
        if role in [UserRole.VENDOR, UserRole.NGO]:
            from apps.business.models import Business, Branch
            from django.utils.text import slugify

            b_name = (business_name or '').strip() or (f"{first_name}'s Store" if first_name else "Merchant")
            b_type = business_type if business_type else (Business.BusinessType.NGO if role == UserRole.NGO else Business.BusinessType.VENDOR)
            
            slug = slugify(b_name)
            if Business.objects.filter(slug=slug).exists():
                slug = f"{slug}-{uuid.uuid4().hex[:6]}"
                
            biz = Business.objects.create(
                owner=user,
                business_name=b_name,
                slug=slug,
                business_type=b_type,
                business_status=Business.BusinessStatus.PENDING,
                business_email=email,
                business_phone=getattr(user, 'phone_number', '') or '',
                registration_number=registration_number or '',
                gst_number=gst_number or '',
                is_active=True,
                is_verified=False
            )
            
            Branch.objects.create(
                business=biz,
                branch_name=f"{biz.business_name} Main Branch",
                branch_code=f"BR-{uuid.uuid4().hex[:6].upper()}",
                is_main_branch=True,
                branch_status=Branch.BranchStatus.ACTIVE
            )

            if role == UserRole.NGO:
                from apps.donations.models import NGO, NGOVerificationStatus
                NGO.objects.create(
                    user=user,
                    organization_name=b_name,
                    registration_number=registration_number or f"NGO-{uuid.uuid4().hex[:6].upper()}",
                    contact_person=user.full_name,
                    email=email,
                    phone=getattr(user, 'phone_number', '') or '',
                    address='',
                    verification_status=NGOVerificationStatus.PENDING,
                    is_active=True
                )
        
        return user

    @staticmethod
    # Method: login
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
        """
        user = authenticate(email=email, password=password)
        
        if not user:
            existing_user = User.objects.filter(email=email).first()
            if existing_user and existing_user.check_password(password) and not existing_user.is_active:
                raise AccountInactive("Your account verification has been revoked by admin.")
            raise InvalidCredentials()
            
        if not user.is_active:
            raise AccountInactive("Your account verification has been revoked by admin.")
            
        if user.role in [UserRole.VENDOR, UserRole.NGO]:
            biz = user.businesses.filter(is_deleted=False).first()
            if biz:
                if not biz.is_verified:
                    raise AccountInactive("Your account verification has been revoked by admin.")
                if biz.business_status == 'SUSPENDED':
                    raise AccountInactive("Your account has been suspended by admin.")
                elif biz.business_status == 'REJECTED':
                    raise InvalidCredentials("Your business registration was rejected by admin.")
                elif biz.business_status == 'PENDING':
                    raise AccountInactive("Your account is pending admin approval.")

        refresh = RefreshToken.for_user(user)
        tokens = {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
        
        return user, tokens

    @staticmethod
    @transaction.atomic
    # Method: verify_email
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
    # Method: request_password_reset
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
    # Method: reset_password
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


# Class: UserService
class UserService:
    """
    Service layer handling user profile management, role assignment, and status updates.
    """

    @staticmethod
    @transaction.atomic
    # Method: update_profile
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
        safe_fields = {'first_name', 'last_name', 'phone_number', 'profile_image'}
        filtered_data = {k: v for k, v in update_data.items() if k in safe_fields}

        user = UserRepository.get_by_id(user_id)
        if not user:
            raise UserNotFound()

        return UserRepository.update_user(user, filtered_data)

    @staticmethod
    @transaction.atomic
    # Method: change_password
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
    # Method: assign_role
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
    # Method: deactivate_account
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
    # Method: activate_account
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

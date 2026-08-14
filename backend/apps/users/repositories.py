import uuid
from typing import Optional, Dict, Any
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
from apps.users.models import User

# Class: UserRepository
class UserRepository:
    """
    Repository layer for the User model.
    Handles all database operations for users.
    Contains strictly data access logic, no business logic.
    """

    @staticmethod
    # Method: get_by_id
    def get_by_id(user_id: uuid.UUID) -> Optional[User]:
        """
        Retrieve a user by their UUID.
        
        Args:
            user_id (uuid.UUID): The UUID of the user.
            
        Returns:
            Optional[User]: The user instance if found, None otherwise.
        """
        try:
            # Using only to fetch necessary fields if needed, 
            # but getting the full object is standard here.
            # Add select_related/prefetch_related here if FKs are added later.
            return User.objects.get(id=user_id)
        except ObjectDoesNotExist:
            return None

    @staticmethod
    # Method: get_by_email
    def get_by_email(email: str) -> Optional[User]:
        """
        Retrieve a user by their email address.
        
        Args:
            email (str): The email address of the user.
            
        Returns:
            Optional[User]: The user instance if found, None otherwise.
        """
        try:
            return User.objects.get(email=email)
        except ObjectDoesNotExist:
            return None

    @staticmethod
    @transaction.atomic
    # Method: create_user
    def create_user(
        email: str, 
        password: str, 
        first_name: str = '', 
        last_name: str = '', 
        **extra_fields: Any
    ) -> User:
        """
        Create and save a new user.
        
        Args:
            email (str): The user's email.
            password (str): The raw password.
            first_name (str): The user's first name.
            last_name (str): The user's last name.
            **extra_fields: Any additional fields (e.g., role, phone_number).
            
        Returns:
            User: The newly created user instance.
        """
        # We delegate the actual creation to the model manager 
        # which handles password hashing and email normalization.
        return User.objects.create_user(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            **extra_fields
        )

    @staticmethod
    @transaction.atomic
    # Method: update_user
    def update_user(user: User, data: Dict[str, Any]) -> User:
        """
        Update a user's attributes.
        
        Args:
            user (User): The user instance to update.
            data (Dict[str, Any]): A dictionary of fields to update.
            
        Returns:
            User: The updated user instance.
        """
        has_changes = False
        for field, value in data.items():
            if hasattr(user, field) and getattr(user, field) != value:
                setattr(user, field, value)
                has_changes = True

        if has_changes:
            # Only save the fields that were actually present in the data keys
            user.save(update_fields=list(data.keys()) + ['updated_at'])
            
        return user

    @staticmethod
    @transaction.atomic
    # Method: deactivate_user
    def deactivate_user(user: User) -> User:
        """
        Deactivate a user account (soft delete).
        
        Args:
            user (User): The user instance to deactivate.
            
        Returns:
            User: The updated user instance.
        """
        if user.is_active:
            user.is_active = False
            user.save(update_fields=['is_active', 'updated_at'])
        return user

    @staticmethod
    @transaction.atomic
    # Method: activate_user
    def activate_user(user: User) -> User:
        """
        Activate a user account.
        
        Args:
            user (User): The user instance to activate.
            
        Returns:
            User: The updated user instance.
        """
        if not user.is_active:
            user.is_active = True
            user.save(update_fields=['is_active', 'updated_at'])
        return user

    @staticmethod
    @transaction.atomic
    # Method: update_password
    def update_password(user: User, raw_password: str) -> User:
        """
        Update a user's password securely.
        
        Args:
            user (User): The user instance.
            raw_password (str): The new raw password.
            
        Returns:
            User: The updated user instance.
        """
        user.set_password(raw_password)
        user.save(update_fields=['password', 'updated_at'])
        return user

    @staticmethod
    @transaction.atomic
    # Method: verify_email
    def verify_email(user: User) -> User:
        """
        Mark a user's email as verified.
        
        Args:
            user (User): The user instance.
            
        Returns:
            User: The updated user instance.
        """
        if not user.is_email_verified:
            user.is_email_verified = True
            user.save(update_fields=['is_email_verified', 'updated_at'])
        return user

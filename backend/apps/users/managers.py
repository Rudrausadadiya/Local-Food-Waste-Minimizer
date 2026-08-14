from django.contrib.auth.models import BaseUserManager
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from typing import Any, Optional

# Class: UserManager
class UserManager(BaseUserManager):
    """
    Custom user model manager where email is the unique identifiers
    for authentication instead of usernames.
    """

    # Method: create_user
    def create_user(self, email: str, password: Optional[str] = None, **extra_fields: Any) -> Any:
        """
        Create and save a user with the given email and password.
        
        Args:
            email (str): The email address of the user.
            password (str, optional): The user's password. Defaults to None.
            **extra_fields: Additional fields to save on the user model.
            
        Returns:
            User: The created user instance.
            
        Raises:
            ValueError: If the email is not provided.
            ValidationError: If the email format is invalid.
        """
        if not email:
            raise ValueError('The Email must be set')
            
        email = self.normalize_email(email)
        
        try:
            validate_email(email)
        except ValidationError:
            raise ValueError('You must provide a valid email address')
            
        user = self.model(email=email, **extra_fields)
        
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
            
        user.save(using=self._db)
        return user

    # Method: create_superuser
    def create_superuser(self, email: str, password: Optional[str] = None, **extra_fields: Any) -> Any:
        """
        Create and save a SuperUser with the given email and password.
        
        Args:
            email (str): The email address of the superuser.
            password (str, optional): The superuser's password. Defaults to None.
            **extra_fields: Additional fields to save on the user model.
            
        Returns:
            User: The created superuser instance.
            
        Raises:
            ValueError: If is_staff or is_superuser is not True.
        """
        from apps.users.choices import UserRole
        
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_email_verified', True)
        extra_fields.setdefault('role', UserRole.ADMIN)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)

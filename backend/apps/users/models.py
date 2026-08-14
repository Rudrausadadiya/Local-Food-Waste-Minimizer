from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils.translation import gettext_lazy as _
from common.models import UUIDTimeStampedModel
from apps.users.managers import UserManager
from apps.users.choices import UserRole


# Class: User
class User(AbstractBaseUser, PermissionsMixin, UUIDTimeStampedModel):
    """
    Custom User model representing an authenticated entity in the system.
    
    Inherits from:
        AbstractBaseUser: Provides core authentication fields (password, last_login).
        PermissionsMixin: Provides Django permission system (groups, user_permissions, is_superuser).
        UUIDTimeStampedModel: Provides UUID primary key and created_at/updated_at fields.
    """
    
    email = models.EmailField(
        _('email address'),
        unique=True,
        db_index=True,
        error_messages={
            'unique': _('A user with that email already exists.'),
        }
    )
    first_name = models.CharField(_('first name'), max_length=150, blank=True)
    last_name = models.CharField(_('last name'), max_length=150, blank=True)
    phone_number = models.CharField(_('phone number'), max_length=20, blank=True)
    profile_image = models.ImageField(
        _('profile image'),
        upload_to='profile_images/',
        null=True,
        blank=True
    )
    role = models.CharField(
        _('role'),
        max_length=20,
        choices=UserRole.choices,
        default=UserRole.CUSTOMER,
        db_index=True
    )
    
    # Status flags
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_('Designates whether this user should be treated as active. '
                    'Unselect this instead of deleting accounts.')
    )
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this admin site.')
    )
    is_email_verified = models.BooleanField(
        _('email verified'),
        default=False,
        help_text=_('Designates whether this user has verified their email address.')
    )
    
    # The last_login field is provided by AbstractBaseUser
    # The created_at and updated_at fields are provided by UUIDTimeStampedModel
    # The id (UUID) field is provided by UUIDTimeStampedModel

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    # Class: Meta
    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        ordering = ['-created_at']

    # Method: __str__
    def __str__(self) -> str:
        """String representation of the User model."""
        return self.email

    @property
    # Method: full_name
    def full_name(self) -> str:
        """
        Returns the user's full name.
        
        Returns:
            str: The concatenated first and last name, or email if names are blank.
        """
        full_name = f"{self.first_name} {self.last_name}".strip()
        return full_name if full_name else self.email

from django.db import models
from django.utils.translation import gettext_lazy as _

class UserRole(models.TextChoices):
    """
    Defines the available roles for users in the system.
    
    Attributes:
        ADMIN: Has full access to the system.
        VENDOR: Can manage their own products and sales.
        CUSTOMER: Standard user who can purchase items.
        NGO: Non-governmental organization user.
    """
    ADMIN = 'ADMIN', _('Admin')
    VENDOR = 'VENDOR', _('Vendor')
    CUSTOMER = 'CUSTOMER', _('Customer')
    NGO = 'NGO', _('NGO')

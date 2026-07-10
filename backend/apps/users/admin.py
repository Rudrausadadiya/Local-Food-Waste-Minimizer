from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from apps.users.models import User
from apps.users.forms import CustomUserCreationForm, CustomUserChangeForm
from typing import Tuple, List, Dict, Any, Optional

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Admin interface for the custom User model.
    """
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm
    
    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display: Tuple[str, ...] = (
        'email', 
        'first_name', 
        'last_name', 
        'role', 
        'is_active', 
        'is_email_verified',
        'is_staff'
    )
    
    list_filter: Tuple[str, ...] = (
        'role', 
        'is_active', 
        'is_email_verified', 
        'is_staff', 
        'is_superuser'
    )
    
    search_fields: Tuple[str, ...] = (
        'email', 
        'first_name', 
        'last_name', 
        'phone_number'
    )
    
    ordering: Tuple[str, ...] = ('-created_at',)
    
    readonly_fields: Tuple[str, ...] = (
        'id', 
        'last_login', 
        'created_at', 
        'updated_at'
    )

    fieldsets: Tuple[Tuple[Optional[str], Dict[str, Any]], ...] = (
        (None, {
            'fields': ('email', 'password')
        }),
        (_('Personal info'), {
            'fields': ('first_name', 'last_name', 'phone_number', 'profile_image')
        }),
        (_('Roles & Status'), {
            'fields': ('role', 'is_active', 'is_email_verified')
        }),
        (_('Permissions'), {
            'fields': ('is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {
            'fields': ('last_login', 'created_at', 'updated_at')
        }),
    )

    add_fieldsets: Tuple[Tuple[Optional[str], Dict[str, Any]], ...] = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'first_name', 'last_name', 'role'),
        }),
    )
    
    # Customizes the ordering of fields in the search results
    search_help_text = _("Search by email, first name, last name, or phone number.")

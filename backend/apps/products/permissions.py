from rest_framework import permissions
from apps.business.models import Business

class IsBusinessOwnerOrAdmin(permissions.BasePermission):
    """
    Custom permission to only allow business owners or admins to edit products/categories.
    """

    def has_permission(self, request, view):
        if request.user and request.user.is_superuser:
            return True
            
        if request.method in permissions.SAFE_METHODS:
            return True
            
        business_id = request.data.get('business')
        if not business_id:
            return True 
            
        return Business.objects.filter(id=business_id, owner=request.user).exists()

    def has_object_permission(self, request, view, obj):
        if request.user and request.user.is_superuser:
            return True
            
        if request.method in permissions.SAFE_METHODS:
            return True
            
        return obj.business.owner == request.user

class IsBranchManager(permissions.BasePermission):
    """
    Permission class for branch managers (Read-only for products).
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return False

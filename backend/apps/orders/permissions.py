from rest_framework import permissions

class IsAdminUserOrReadOnly(permissions.IsAdminUser):
    def has_permission(self, request, view):
        is_admin = super().has_permission(request, view)
        return request.method in permissions.SAFE_METHODS or is_admin

class IsBusinessOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and hasattr(request.user, 'role') and request.user.role == 'BUSINESS_OWNER'

    def has_object_permission(self, request, view, obj):
        return hasattr(obj, 'business') and obj.business.owner == request.user

class IsCashier(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and hasattr(request.user, 'role') and request.user.role == 'CASHIER'

class IsSalesManager(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and hasattr(request.user, 'role') and request.user.role == 'SALES_MANAGER'

class IsBranchManager(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and hasattr(request.user, 'role') and request.user.role == 'BRANCH_MANAGER'

class IsCustomerReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and hasattr(request.user, 'role') and request.user.role == 'CUSTOMER' and request.method in permissions.SAFE_METHODS

class HasOrderManagementPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
            
        role = getattr(request.user, 'role', None)
        if request.method in permissions.SAFE_METHODS:
            return role in ['ADMIN', 'BUSINESS_OWNER', 'CASHIER', 'SALES_MANAGER', 'BRANCH_MANAGER', 'CUSTOMER']
            
        return role in ['ADMIN', 'BUSINESS_OWNER', 'CASHIER', 'SALES_MANAGER', 'BRANCH_MANAGER']

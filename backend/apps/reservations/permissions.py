from rest_framework import permissions

# Class: HasReservationManagementPermission
class HasReservationManagementPermission(permissions.BasePermission):
    # Method: has_permission
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
            
        role = getattr(request.user, 'role', None)
        if request.method in permissions.SAFE_METHODS:
            return role in ['ADMIN', 'BUSINESS_OWNER', 'RESERVATION_MANAGER', 'BRANCH_MANAGER', 'CUSTOMER']
            
        return role in ['ADMIN', 'BUSINESS_OWNER', 'RESERVATION_MANAGER', 'BRANCH_MANAGER']

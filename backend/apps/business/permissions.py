from rest_framework import permissions

# Class: IsBusinessOwner
class IsBusinessOwner(permissions.BasePermission):
    """
    Object-level permission to only allow owners of a business or Admin to view or edit it.
    """
    # Method: has_object_permission
    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False
        return obj.owner == request.user or request.user.is_staff or getattr(request.user, 'role', '') == 'ADMIN'

# Class: CustomerCannotCreateBusiness
class CustomerCannotCreateBusiness(permissions.BasePermission):
    """
    Global permission check for blocking customers from creating businesses.
    """
    # Method: has_permission
    def has_permission(self, request, view):
        if request.method == 'POST':
            # Assuming user role logic exists, e.g. request.user.role
            # This is a placeholder since User model isn't fully defined in context
            role = getattr(request.user, 'role', None)
            if role == 'CUSTOMER':
                return False
        return True

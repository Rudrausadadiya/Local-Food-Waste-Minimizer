from rest_framework import permissions

class IsBusinessOwner(permissions.BasePermission):
    """
    Object-level permission to only allow owners of a business to edit it.
    Assumes the model instance has an `owner` attribute.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Instance must have an attribute named `owner`.
        return obj.owner == request.user or request.user.is_staff

class CustomerCannotCreateBusiness(permissions.BasePermission):
    """
    Global permission check for blocking customers from creating businesses.
    """
    def has_permission(self, request, view):
        if request.method == 'POST':
            # Assuming user role logic exists, e.g. request.user.role
            # This is a placeholder since User model isn't fully defined in context
            role = getattr(request.user, 'role', None)
            if role == 'CUSTOMER':
                return False
        return True

from rest_framework import permissions

# Class: IsNotificationOwnerOrAdmin
class IsNotificationOwnerOrAdmin(permissions.BasePermission):
    # Method: has_permission
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    # Method: has_object_permission
    def has_object_permission(self, request, view, obj):
        role = getattr(request.user, 'role', None)
        if role == 'ADMIN':
            return True
            
        # obj could be Notification or NotificationPreference
        owner = getattr(obj, 'recipient', getattr(obj, 'user', None))
        return owner == request.user

# Class: IsAdminUser
class IsAdminUser(permissions.BasePermission):
    # Method: has_permission
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and getattr(request.user, 'role', None) == 'ADMIN'

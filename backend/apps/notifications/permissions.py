from rest_framework import permissions

class IsNotificationOwnerOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        role = getattr(request.user, 'role', None)
        if role == 'ADMIN':
            return True
            
        # obj could be Notification or NotificationPreference
        owner = getattr(obj, 'recipient', getattr(obj, 'user', None))
        return owner == request.user

class IsAdminUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and getattr(request.user, 'role', None) == 'ADMIN'

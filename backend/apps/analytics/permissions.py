from rest_framework import permissions

class IsAnalyticsViewer(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
            
        role = getattr(request.user, 'role', None)
        return role in ['ADMIN', 'BUSINESS_OWNER', 'MANAGER', 'STAFF']

class IsAnalyticsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and getattr(request.user, 'role', None) == 'ADMIN'

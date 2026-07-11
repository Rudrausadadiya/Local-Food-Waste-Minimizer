from rest_framework import permissions

class HasMarketplacePermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
            
        role = getattr(request.user, 'role', None)
        
        # Read operations
        if request.method in permissions.SAFE_METHODS:
            return role in ['ADMIN', 'BUSINESS_OWNER', 'MARKETPLACE_MANAGER', 'CUSTOMER', 'NGO']
            
        # Write operations for listings
        if view.basename == 'listing':
            return role in ['ADMIN', 'BUSINESS_OWNER', 'MARKETPLACE_MANAGER']
            
        # Write operations for customer features (orders, wishlists, reviews)
        return role in ['ADMIN', 'BUSINESS_OWNER', 'MARKETPLACE_MANAGER', 'CUSTOMER']

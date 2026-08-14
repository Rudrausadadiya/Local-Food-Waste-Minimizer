from rest_framework import permissions

# Class: HasMarketplacePermission
class HasMarketplacePermission(permissions.BasePermission):
    # Method: has_permission
    def has_permission(self, request, view):
        # Allow SAFE_METHODS (GET, HEAD, OPTIONS) for public marketplace browsing
        if request.method in permissions.SAFE_METHODS:
            return True
            
        if not request.user.is_authenticated:
            return False
            
        role = getattr(request.user, 'role', None)

        # Customers/NGOs can call wishlist and other customer-facing listing actions
        action = getattr(view, 'action', None)
        if action in ('add_to_wishlist', 'recommendations', 'retrieve', 'list'):
            return role in ['ADMIN', 'VENDOR', 'BUSINESS_OWNER', 'MARKETPLACE_MANAGER', 'CUSTOMER', 'NGO']
            
        # Mutating listing resources (create/update/delete) – Vendors/Admins only
        if view.basename == 'listing':
            return role in ['ADMIN', 'VENDOR', 'BUSINESS_OWNER', 'MARKETPLACE_MANAGER']
            
        # Write operations for customer features (orders, wishlists, reviews)
        return role in ['ADMIN', 'VENDOR', 'BUSINESS_OWNER', 'MARKETPLACE_MANAGER', 'CUSTOMER', 'NGO']

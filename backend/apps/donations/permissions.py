from rest_framework import permissions

# Class: HasDonationPermission
class HasDonationPermission(permissions.BasePermission):
    # Method: has_permission
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
            
        role = getattr(request.user, 'role', None)
        
        # Customers have zero access to the NGO/Donation module
        if role == 'CUSTOMER':
            return False
            
        if request.method in permissions.SAFE_METHODS:
            return True
            
        return role in ['ADMIN', 'BUSINESS_OWNER', 'NGO_MANAGER', 'NGO']

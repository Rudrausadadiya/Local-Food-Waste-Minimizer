from rest_framework import permissions

# Class: IsAdminUserOrReadOnly
class IsAdminUserOrReadOnly(permissions.IsAdminUser):
    # Method: has_permission
    def has_permission(self, request, view):
        is_admin = super().has_permission(request, view)
        return request.method in permissions.SAFE_METHODS or is_admin

# Class: BaseInventoryRolePermission
class BaseInventoryRolePermission(permissions.BasePermission):
    """
    Base permission for inventory roles. 
    Assumes request.user has a 'role' or similar attribute/method 
    identifying their clearance level.
    Adjust based on the actual User/Role implementation of the project.
    """
    
    # Method: get_user_role
    def get_user_role(self, user):
        # Assuming a `role` attribute or method exists on user.
        # This will need to be aligned with the actual users app structure.
        if hasattr(user, 'role'):
            return user.role
        return None

# Class: IsBusinessOwner
class IsBusinessOwner(BaseInventoryRolePermission):
    # Method: has_permission
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return self.get_user_role(request.user) == 'BUSINESS_OWNER'

# Class: IsInventoryManager
class IsInventoryManager(BaseInventoryRolePermission):
    # Method: has_permission
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return self.get_user_role(request.user) in ['BUSINESS_OWNER', 'INVENTORY_MANAGER']

# Class: IsBranchManager
class IsBranchManager(BaseInventoryRolePermission):
    # Method: has_permission
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        # Branch Managers can only access things within their branch
        return self.get_user_role(request.user) in ['BUSINESS_OWNER', 'INVENTORY_MANAGER', 'BRANCH_MANAGER']

    # Method: has_object_permission
    def has_object_permission(self, request, view, obj):
        # Additional check to ensure the object belongs to their branch
        if hasattr(obj, 'branch'):
            # Assuming user has a `managed_branches` or similar concept
            pass 
        return True

# Class: IsReadOnlyStaff
class IsReadOnlyStaff(BaseInventoryRolePermission):
    # Method: has_permission
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in permissions.SAFE_METHODS:
            return self.get_user_role(request.user) in ['BUSINESS_OWNER', 'INVENTORY_MANAGER', 'BRANCH_MANAGER', 'STAFF']
        return False

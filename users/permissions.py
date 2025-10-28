from typing import List
from rest_framework import permissions
from collections.abc import Iterable

# class HasPermission(permissions.BasePermission):
#     """
#     Check if user has specific permission through their roles.
#     Usage: permission_classes = [IsAuthenticated, HasPermission]
#     Set permission_required attribute on the view.
#     """

#     def has_permission(self, request, view):
#         # Superusers have all permissions
#         if request.user.is_superuser:
#             return True

#         # Get required permission from view
#         permission_required = getattr(view, "permission_required", None)

#         if not permission_required:
#             return False

#         # Check if user has the permission
#         return request.user.has_permission(permission_required)
    
class HasPermissions(permissions.BasePermission):
    """
    checks if the requested list of permissions is satisfied.
    update: can pass a single permission as a string. 
    usage: permissions_required = ["can-manage-products", "can-update-products"]
           permission_required = "can-manage-products"
    """

    def has_permission(self, request, view):

        if request.user.is_superuser:
            return True
        
        permissions_required = getattr(view, "permissions_required", None)
        
        if permissions_required is None:
            permissions_required = getattr(view, "permission_required", None)

        if not permissions_required:
            return False
        
        # Normalize to iterable
        # "can_edit-products" -> ["can-edit-products"]
        if isinstance(permissions_required, str) or not isinstance(permissions_required, Iterable):
            permissions_required = [permissions_required]

        for code_name in permissions_required:
            if not request.user.has_permission(code_name):
                return False

        return True
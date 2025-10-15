from rest_framework import permissions

class HasPermission(permissions.BasePermission):
    """
    Check if user has specific permission through their roles.
    Usage: permission_classes = [IsAuthenticated, HasPermission]
    Set permission_required attribute on the view.
    """

    def has_permission(self, request, view):
        # Superusers have all permissions
        if request.user.is_superuser:
            return True

        # Get required permission from view
        permission_required = getattr(view, "permission_required", None)

        if not permission_required:
            return False

        # Check if user has the permission
        return request.user.has_permission(permission_required)
    
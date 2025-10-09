from rest_framework import permissions


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Allow access only to the owner of the object or admin users.
    """

    def has_object_permission(self, request, view, obj):
        # Admin users have full access
        if request.user.is_staff or request.user.is_superuser:
            return True

        # Check if obj is User instance
        if hasattr(obj, "email"):
            return obj == request.user

        # Check if obj has user attribute (UserProfile, Address, etc.)
        if hasattr(obj, "user"):
            return obj.user == request.user

        return False


class IsStaffOrReadOnly(permissions.BasePermission):
    """
    Allow read-only access to everyone, write access only to staff.
    """

    def has_permission(self, request, view):
        # Read permissions for authenticated users
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated

        # Write permissions only for staff
        return request.user.is_staff


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
            return True

        # Check if user has the permission
        return request.user.has_permission(permission_required)


class IsOwner(permissions.BasePermission):
    """
    Allow access only to the owner of the object.
    """

    def has_object_permission(self, request, view, obj):
        # Check if obj is User instance
        if hasattr(obj, "email"):
            return obj == request.user

        # Check if obj has user attribute
        if hasattr(obj, "user"):
            return obj.user == request.user

        return False


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Allow read access to anyone, write access to admin only.
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True

        return request.user.is_staff or request.user.is_superuser
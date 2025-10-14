from rest_framework import permissions

class HasPermission(permissions.BasePermission):
    """
    Check if user has specific permission through their roles.
    Usage: permission_classes = [IsAuthenticated, HasPermission]
    Set permission_required attribute on the view.
    """

    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True

        permission_required = getattr(view, "permission_required", None)

        if not permission_required:
            return False

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
from rest_framework import generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import (
    IsAuthenticated,
    IsAdminUser,
    AllowAny,
)
from rest_framework.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from django.db.models import Q

from .models import (
    User,
    UserProfile,
    Address,
    PermissionCategory,
    Permission,
    Role,
    UserRole,
)
from .serializers import (
    UserSerializer,
    UserCreateSerializer,
    UserUpdateSerializer,
    UserDetailSerializer,
    UserProfileSerializer,
    UserProfileCreateUpdateSerializer,
    AddressSerializer,
    AddressCreateUpdateSerializer,
    PermissionCategorySerializer,
    PermissionSerializer,
    PermissionListSerializer,
    RoleSerializer,
    RoleListSerializer,
    UserRoleSerializer,
    UserRoleAssignSerializer,
)
from .permissions import (
    IsOwnerOrAdmin,
    IsStaffOrReadOnly,
    HasPermission,
)


# User Views
class UserListAPIView(generics.ListAPIView):
    """List all users - Staff/Admin only"""

    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsStaffOrReadOnly]
    queryset = User.objects.all()
    filterset_fields = ["is_active", "is_staff", "date_joined"]
    search_fields = ["email", "first_name", "last_name", "phone"]
    ordering_fields = ["date_joined", "email", "first_name", "last_name"]
    ordering = ["-date_joined"]

    def get_queryset(self):
        """Filter queryset based on user permissions"""
        queryset = super().get_queryset()

        # Non-staff users can only see active users
        if not self.request.user.is_staff:
            queryset = queryset.filter(is_active=True)

        return queryset.select_related("profile")


class UserCreateAPIView(generics.CreateAPIView):
    """Register new user - Public endpoint"""

    serializer_class = UserCreateSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        """Create user and assign default customer role"""
        user = serializer.save()

        # Assign default customer role
        try:
            customer_role = Role.objects.get(slug="customer")
            UserRole.objects.create(user=user, role=customer_role)
        except Role.DoesNotExist:
            pass

        # Create user profile
        UserProfile.objects.create(user=user)


class UserDetailAPIView(generics.RetrieveAPIView):
    """Get user details"""

    serializer_class = UserDetailSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
    queryset = User.objects.all()
    lookup_field = "pk"

    def get_queryset(self):
        return super().get_queryset().select_related("profile").prefetch_related(
            "user_roles__role__permissions"
        )


class UserUpdateAPIView(generics.UpdateAPIView):
    """Update user information"""

    serializer_class = UserUpdateSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
    queryset = User.objects.all()
    lookup_field = "pk"


class UserDeleteAPIView(generics.DestroyAPIView):
    """Delete/Deactivate user - Admin only"""

    permission_classes = [IsAuthenticated, IsAdminUser]
    queryset = User.objects.all()
    lookup_field = "pk"

    def perform_destroy(self, instance):
        """Soft delete - deactivate instead of deleting"""
        instance.is_active = False
        instance.save()


class CurrentUserAPIView(generics.RetrieveUpdateAPIView):
    """Get or update current authenticated user"""

    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == "GET":
            return UserDetailSerializer
        return UserUpdateSerializer

    def get_object(self):
        return self.request.user


# User Profile Views
class UserProfileDetailAPIView(generics.RetrieveAPIView):
    """Get user profile"""

    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
    queryset = UserProfile.objects.all()
    lookup_field = "user_id"


class UserProfileUpdateAPIView(generics.UpdateAPIView):
    """Update user profile"""

    serializer_class = UserProfileCreateUpdateSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
    queryset = UserProfile.objects.all()
    lookup_field = "user_id"


class CurrentUserProfileAPIView(generics.RetrieveUpdateAPIView):
    """Get or update current user's profile"""

    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == "GET":
            return UserProfileSerializer
        return UserProfileCreateUpdateSerializer

    def get_object(self):
        profile, created = UserProfile.objects.get_or_create(user=self.request.user)
        return profile


# Address Views
class AddressListCreateAPIView(generics.ListCreateAPIView):
    """List user addresses or create new address"""

    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return AddressCreateUpdateSerializer
        return AddressSerializer

    def get_queryset(self):
        """Get addresses for current user or specified user (admin only)"""
        user_id = self.request.query_params.get("user_id")

        if user_id and self.request.user.is_staff:
            return Address.objects.filter(user_id=user_id)

        return Address.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class AddressDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete address"""

    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]

    def get_serializer_class(self):
        if self.request.method in ["PUT", "PATCH"]:
            return AddressCreateUpdateSerializer
        return AddressSerializer

    def get_queryset(self):
        """Users can only access their own addresses"""
        if self.request.user.is_staff:
            return Address.objects.all()
        return Address.objects.filter(user=self.request.user)


class SetDefaultAddressAPIView(generics.UpdateAPIView):
    """Set address as default"""

    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
    queryset = Address.objects.all()

    def update(self, request, *args, **kwargs):
        address = self.get_object()

        # Check ownership
        if address.user != request.user and not request.user.is_staff:
            raise PermissionDenied("You don't have permission to modify this address.")

        # Unset other default addresses
        Address.objects.filter(user=address.user, is_default=True).update(
            is_default=False
        )

        # Set this as default
        address.is_default = True
        address.save()

        serializer = AddressSerializer(address)
        return Response(serializer.data)


# RBAC - Permission Category Views
class PermissionCategoryViewSet(viewsets.ModelViewSet):
    """ViewSet for permission categories"""

    queryset = PermissionCategory.objects.all()
    serializer_class = PermissionCategorySerializer
    permission_classes = [IsAuthenticated, IsStaffOrReadOnly]
    lookup_field = "slug"
    filterset_fields = ["is_active"]
    search_fields = ["name", "slug", "description"]
    ordering = ["name"]

    def get_queryset(self):
        queryset = super().get_queryset()

        # Non-staff users only see active categories
        if not self.request.user.is_staff:
            queryset = queryset.filter(is_active=True)

        return queryset.prefetch_related("permissions")


# RBAC - Permission Views
class PermissionListAPIView(generics.ListAPIView):
    """List all permissions"""

    serializer_class = PermissionListSerializer
    permission_classes = [IsAuthenticated, IsStaffOrReadOnly]
    queryset = Permission.objects.all()
    filterset_fields = ["category", "is_active"]
    search_fields = ["name", "code_name", "description"]
    ordering_fields = ["name", "code_name", "category"]
    ordering = ["category", "name"]

    def get_queryset(self):
        queryset = super().get_queryset()

        # Non-staff users only see active permissions
        if not self.request.user.is_staff:
            queryset = queryset.filter(is_active=True)

        return queryset.select_related("category")


class PermissionDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete permission"""

    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    lookup_field = "code_name"


class PermissionCreateAPIView(generics.CreateAPIView):
    """Create new permission"""

    serializer_class = PermissionSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]


# RBAC - Role Views
class RoleListAPIView(generics.ListAPIView):
    """List all roles"""

    serializer_class = RoleListSerializer
    permission_classes = [IsAuthenticated]
    queryset = Role.objects.all()
    filterset_fields = ["is_active", "is_system_role"]
    search_fields = ["name", "slug", "description"]
    ordering = ["name"]

    def get_queryset(self):
        queryset = super().get_queryset()

        # Non-staff users only see active roles
        if not self.request.user.is_staff:
            queryset = queryset.filter(is_active=True)

        return queryset.prefetch_related("permissions")


class RoleDetailAPIView(generics.RetrieveAPIView):
    """Get role details with permissions"""

    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "slug"

    def get_queryset(self):
        return super().get_queryset().prefetch_related("permissions__category")


class RoleCreateAPIView(generics.CreateAPIView):
    """Create new role"""

    serializer_class = RoleSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]


class RoleUpdateAPIView(generics.UpdateAPIView):
    """Update role"""

    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    lookup_field = "slug"


class RoleDeleteAPIView(generics.DestroyAPIView):
    """Delete role - Cannot delete system roles"""

    queryset = Role.objects.all()
    permission_classes = [IsAuthenticated, IsAdminUser]
    lookup_field = "slug"

    def perform_destroy(self, instance):
        if instance.is_system_role:
            raise PermissionDenied("System roles cannot be deleted.")
        instance.delete()


# RBAC - User Role Assignment Views
class UserRoleListAPIView(generics.ListAPIView):
    """List user role assignments"""

    serializer_class = UserRoleSerializer
    permission_classes = [IsAuthenticated, IsStaffOrReadOnly]
    queryset = UserRole.objects.all()
    filterset_fields = ["user", "role", "is_active"]
    ordering = ["-assigned_at"]

    def get_queryset(self):
        queryset = super().get_queryset().select_related("user", "role", "assigned_by")

        # Filter by user if provided
        user_id = self.request.query_params.get("user_id")
        if user_id:
            queryset = queryset.filter(user_id=user_id)

        # Non-staff users can only see their own role assignments
        if not self.request.user.is_staff:
            queryset = queryset.filter(user=self.request.user)

        return queryset


class UserRoleAssignAPIView(generics.CreateAPIView):
    """Assign role to user"""

    serializer_class = UserRoleAssignSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]


class UserRoleRevokeAPIView(generics.DestroyAPIView):
    """Revoke role from user"""

    queryset = UserRole.objects.all()
    permission_classes = [IsAuthenticated, IsAdminUser]

    def perform_destroy(self, instance):
        """Soft delete - deactivate instead of deleting"""
        instance.is_active = False
        instance.save()


class UserRoleToggleAPIView(generics.UpdateAPIView):
    """Toggle user role active status"""

    queryset = UserRole.objects.all()
    permission_classes = [IsAuthenticated, IsAdminUser]

    def update(self, request, *args, **kwargs):
        user_role = self.get_object()
        user_role.is_active = not user_role.is_active
        user_role.save()

        serializer = UserRoleSerializer(user_role)
        return Response(serializer.data)


class MyRolesAPIView(generics.ListAPIView):
    """Get current user's roles and permissions"""

    serializer_class = UserRoleSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return UserRole.objects.filter(
            user=self.request.user, is_active=True
        ).select_related("role", "assigned_by")

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)

        # Get all permissions
        permissions = set()
        for user_role in queryset:
            if user_role.role.is_active:
                role_permissions = user_role.role.get_permission_codes()
                permissions.update(role_permissions)

        return Response(
            {
                "roles": serializer.data,
                "permissions": list(permissions),
                "is_superuser": request.user.is_superuser,
            }
        )
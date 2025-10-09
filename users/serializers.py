from rest_framework import serializers
from .models import Permission, PermissionCategory, Role, User, UserProfile, Address, UserRole


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            "email",
            "password",
            "password_confirm",
            "first_name",
            "last_name",
            "phone",
            "date_of_birth",
        ]

    def validate_email(self, value):
        """Validate email is unique"""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def validate(self, attrs):
        """Validates the password match"""
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError("The passwords do not match.")
        return attrs

    def create(self, validated_data):
        """Creates the user with hashed password"""
        validated_data.pop("password_confirm")
        password = validated_data.pop("password")
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user information"""

    password = serializers.CharField(write_only=True, required=False)
    password_confirm = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = [
            "password",
            "password_confirm",
            "first_name",
            "last_name",
            "phone",
            "date_of_birth",
        ]

    def validate(self, attrs):
        """Validate passwords match if provided"""
        password = attrs.get("password")
        password_confirm = attrs.get("password_confirm")

        if password or password_confirm:
            if password != password_confirm:
                raise serializers.ValidationError("The passwords do not match")
        return attrs

    def update(self, instance, validated_data):
        """Updates user object"""
        password = validated_data.pop("password")
        validated_data.pop("password_confirm")
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


# Only for listing purpose serializer
class UserSerializer(serializers.ModelSerializer):
    """Basic user serializer for read operation"""

    full_name = serializers.CharField(source="get_full_name", read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "full_name",
            "phone",
            "date_of_birth",
            "is_active",
            "is_staff",
            "date_joined",
            "last_login",
        ]
        read_only_fields = ["id", "date_joined", "last_login", "is_active", "is_staff"]


class UserDetailSerializer(serializers.ModelSerializer):
    """Detailed user serializer including profile and roles"""

    full_name = serializers.CharField(source="get_full_name", read_only=True)
    profile = serializers.SerializerMethodField()
    roles = serializers.SerializerMethodField()
    permissions = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "full_name",
            "phone",
            "date_of_birth",
            "is_active",
            "is_staff",
            "is_superuser",
            "date_joined",
            "last_login",
            "profile",
            "roles",
            "permissions",
        ]
        read_only_fields = [
            "id",
            "date_joined",
            "last_login",
            "is_active",
            "is_staff",
            "is_superuser",
        ]

    def get_profile(self, obj):
        """Get user profile if exists"""
        try:
            from .serializers import UserProfileSerializer
            return UserProfileSerializer(obj.profile).data
        except UserProfile.DoesNotExist:
            return None

    def get_roles(self, obj):
        """Get user's active roles"""
        user_roles = obj.user_roles.filter(is_active=True).select_related("role")
        return [
            {"id": ur.role.id, "name": ur.role.name, "slug": ur.role.slug}
            for ur in user_roles
        ]

    def get_permissions(self, obj):
        """Get all permissions from user's roles"""
        if obj.is_superuser:
            return ["all"]

        permission_codes = set()
        user_roles = obj.user_roles.filter(is_active=True).select_related("role")

        for user_role in user_roles:
            if user_role.role.is_active:
                codes = user_role.role.get_permission_codes()
                permission_codes.update(codes)

        return list(permission_codes)


class UserProfileSerializer(serializers.ModelSerializer):
    """Detailed user serializer including profile and roles"""

    full_name = serializers.CharField(source="get_full_name", read_only=True)
    profile = serializers.SerializerMethodField()
    roles = serializers.SerializerMethodField()
    permissions = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "phone",
            "date_of_birth",
            "is_superuser",
            "is_active",
            "is_staff",
            "date_joined",
            "last_login",
            "profile",
            "roles",
            "permissions",
        ]
        read_only_fields = [
            "id",
            "date_joined",
            "last_login",
            "is_active",
            "is_staff",
            "is_superuser",
        ]

        def get_profile(self, obj):
            """Get user profile"""
            try:
                return UserProfileSerializer(obj.profile).data
            except UserProfile.DoesNotExist:
                return None

        def get_roles(self, obj):
            """Get user's active roles"""
            user_roles = obj.user_roles.filter(is_active=True).select_related("role")
            return [
                {
                    "id": user_role.role.id,
                    "name": user_role.role.name,
                    "slug": user_role.role.slug,
                }
                for user_role in user_roles
            ]

        def get_permissions(self, obj):
            """Get all permissions from the user's roles"""
            if obj.is_superuser:
                return ["all"]
            permission_codes = set()
            user_roles = obj.user_roles.filter(is_active=True).select_related("roles")

            for user_role in user_roles:
                if user_role.is_active:
                    codes = user_role.get_permission_codes()
                    permission_codes.update(codes)

            return list(permission_codes)


class UserProfileCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = [
            "bio",
            "avatar",
            "gender",
            "location",
            "website",
        ]


# Alias for create/update operations
UserProfileCreateUpdateSerializer = UserProfileCreateSerializer


# Serializers for addresses
# List
class AddressSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Address
        fields = [
            "id",
            "user",
            "address_type",
            "full_name",
            "phone",
            "address_line_1",
            "address_line_2",
            "city",
            "state",
            "is_default",
            "is_active",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]

# create address serializer
class AddressCreateUpdateSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Address
        fields = [
            "address_type",
            "full_name",
            "phone",
            "address_line_1",
            "address_line_2",
            "city",
            "state",
            "is_default",
        ]

    def validate_phone(self, number):
        if number and not number.is_digit():
            raise serializers.ValidationError("Phone number cannot contain anything other than number")
        elif number and len(number) > 10:
            raise serializers.ValidationError("Number should be less than 10 digits")
        return number
    
    def create(self, validated_data):
        user = self.context['request'].user
        is_default = validated_data.get("is_default", False)

        if is_default:
            Address.objects.filter(user=user, is_default=True).update(
                is_default=False
            )
        address = Address.objects.create(user=user, **validated_data)
        return address



# RABC serializers
class PermissionCategorySerializer(serializers.ModelSerializer):
    """Permission category serializer"""

    permission_count = serializers.SerializerMethodField()

    class Meta:
        model = PermissionCategory
        fields = [
            "id",
            "name",
            "slug",
            "description",
            "permission_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_permission_count(self, obj):
        """Get count of active permissions in this category"""
        return obj.permissions.filter(is_active=True).count()


class PermissionSerializer(serializers.ModelSerializer):
    """Permission serializer"""

    category = PermissionCategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=PermissionCategory.objects.all(),
        source="category",
        write_only=True,
    )

    class Meta:
        model = Permission
        fields = [
            "id",
            "name",
            "code_name",
            "description",
            "category",
            "category_id",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class PermissionListSerializer(serializers.ModelSerializer):
    """Permission serializer for lists"""

    category_name = serializers.CharField(source="category.name", read_only=True)

    class Meta:
        model = Permission
        fields = ["id", "name", "code_name", "category_name", "is_active"]


class RoleSerializer(serializers.ModelSerializer):
    """Role serializer with permissions"""

    permissions = PermissionListSerializer(many=True, read_only=True)
    permission_ids = serializers.PrimaryKeyRelatedField(
        queryset=Permission.objects.filter(is_active=True),
        many=True,
        write_only=True,
        source="permissions",
    )
    permission_count = serializers.SerializerMethodField()

    class Meta:
        model = Role
        fields = [
            "id",
            "name",
            "slug",
            "description",
            "permissions",
            "permission_ids",
            "permission_count",
            "is_active",
            "is_system_role",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "is_system_role"]

    def get_permission_count(self, obj):
        """Get count of active permissions in this role"""
        return obj.permissions.filter(is_active=True).count()

    def validate(self, attrs):
        """Prevent editing system roles"""
        if self.instance and self.instance.is_system_role:
            raise serializers.ValidationError(
                "System roles cannot be modified. Create a new role instead."
            )
        return attrs


class RoleListSerializer(serializers.ModelSerializer):
    """Lightweight role serializer for lists"""

    permission_count = serializers.SerializerMethodField()

    class Meta:
        model = Role
        fields = [
            "id",
            "name",
            "slug",
            "description",
            "permission_count",
            "is_active",
            "is_system_role",
        ]

    def get_permission_count(self, obj):
        """Get count of active permissions"""
        return obj.permissions.filter(is_active=True).count()


class UserRoleSerializer(serializers.ModelSerializer):
    """User role assignment serializer"""

    user = UserSerializer(read_only=True)
    role = RoleListSerializer(read_only=True)
    assigned_by_email = serializers.EmailField(
        source="assigned_by.email", read_only=True
    )

    class Meta:
        model = UserRole
        fields = [
            "id",
            "user",
            "role",
            "assigned_by",
            "assigned_by_email",
            "is_active",
            "assigned_at",
            "updated_at",
        ]
        read_only_fields = ["id", "assigned_at", "updated_at"]


class UserRoleAssignSerializer(serializers.ModelSerializer):
    """Serializer for assigning roles to users"""

    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source="user"
    )
    role_id = serializers.PrimaryKeyRelatedField(
        queryset=Role.objects.filter(is_active=True), source="role"
    )

    class Meta:
        model = UserRole
        fields = ["user_id", "role_id", "is_active"]

    def validate(self, attrs):
        """Validate user-role assignment doesn't already exist"""
        user = attrs["user"]
        role = attrs["role"]

        if UserRole.objects.filter(user=user, role=role).exists():
            raise serializers.ValidationError(
                f"User {user.email} already has role {role.name}"
            )

        return attrs

    def create(self, validated_data):
        """Create user role assignment"""
        validated_data["assigned_by"] = self.context["request"].user
        return super().create(validated_data)
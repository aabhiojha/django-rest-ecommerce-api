from rest_framework import serializers
from .models import (
    OTP,
    Permission,
    PermissionCategory,
    Role,
    User,
    UserProfile,
    Address,
)

# base serializer: look into
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        required=True,
        # style={"input_type": "password"}
    )

    class Meta:
        model = User
        fields = [
            "email",
            "password",
            "first_name",
            "last_name",
            "phone",
            "date_of_birth",
        ]

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def validate(self, attrs):
        try:
            validate_password(attrs["password"])
        except ValidationError as e:
            raise serializers.ValidationError({"password": list(e.messages)})
        return attrs

    def create(self, validated_data):

        user = User.objects.create_user(
            email=validated_data["email"],
            password=validated_data["password"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
            phone=validated_data["phone"],
            date_of_birth=validated_data["date_of_birth"],
        )
        return user


# Password change serializer
class PasswordChangeSerializer(serializers.ModelSerializer):
    # email = serializers.CharField()
    current_password = serializers.CharField(write_only=True, required=True)
    new_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = [
            # "email",
            "current_password",
            "new_password",
        ]

    def validate(self, attrs):
        request = self.context.get("request")

        print(request)

        user = request.user
        if user is None:
            raise serializers.ValidationError("Authentication error")

        current_password = attrs.get("current_password")
        if not user.check_password(current_password):
            raise serializers.ValidationError("Current password is incorrect")

        try:
            validate_password(attrs.get("new_password"), user=user)
        except ValidationError as e:
            raise serializers.ValidationError(
                "New password is not very basic. make it strong"
            )

        return attrs

    def save(self, **kwargs):
        request = self.context.get("request")
        user = request.user
        user.set_password(self.validated_data["new_password"])
        user.save()
        return user


# Password reset serializer
class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField(write_only=True, required=True)

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("No user found with the email address.")
        return value


# Password reset confirm serializer
class PasswordResetConfirmSerializer(serializers.Serializer):
    email = serializers.EmailField(write_only=True, required=True)
    otp = serializers.CharField(
        write_only=True, required=True, max_length=6, min_length=6
    )
    new_password = serializers.CharField(write_only=True, required=True)

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("No user found with this email address.")
        return value

    def validate_new_password(self, value):
        try:
            validate_password(value)
        except ValidationError as e:
            raise serializers.ValidationError(list(e.messages))
        return value

    def validate(self, attrs):
        # get user object
        user = User.objects.filter(email=attrs["email"]).first()
        # get the otp object
        otp_obj = OTP.objects.filter(user=user, otp=attrs["otp"]).first()

        if not otp_obj:
            raise serializers.ValidationError("The opt is invalid.")

        if otp_obj.is_expired:
            raise serializers.ValidationError("This OTP has expired.")
        return attrs


class RoleCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = [
            "name",
            "slug",
            "description",
            "permissions",
            "is_active",
            "is_system_role",
            "created_at",
            "updated_at",
        ]


# permission Serializers
class PermissionListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = [
            "id",
            "name",
            "code_name",
            "description",
            "category",
            "is_active",
        ]
        read_only_field = ["is_active", "category"]


class PermissionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = [
            "name",
            "code_name",
            "description",
            "category",
            "is_active",
        ]

class PermissionEditSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = [
            "name",
            "code_name",
            "description",
            "category",
            "is_active",
        ]

# Permission Category serializers
class PermissionCategoryListSerializer(serializers.ModelSerializer):
    permissions = PermissionListSerializer(many=True)
    class Meta:
        model = PermissionCategory
        fields = [
            "id",
            "name",
            "slug",
            "permissions",
            "description",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "name",
            "slug",
            "description",
            "permissions",
            "is_active",
            "created_at",
            "updated_at",
        ]


class PermissionCategoryCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PermissionCategory
        fields = [
            "name",
            "slug",
            "description",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "created_at",
            "updated_at",
        ]


class PermissionCategoryEditSerializer(serializers.ModelSerializer):
    class Meta:
        model = PermissionCategory
        fields = [
            "id",
            "name",
            "slug",
            "description",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]

class RoleSimpleSerializer(serializers.ModelSerializer):
    """A simple serializer to represent a role with just its name and slug."""
    class Meta:
        model = Role
        fields = ['id', 'name', 'slug']

class RoleListSerializer(serializers.ModelSerializer):
    permissions = serializers.SerializerMethodField()
    # TODO need to display permissions in permission category groups

    class Meta:
        model = Role
        # fields = ""
        fields = [
            "id",
            "name",
            "slug",
            "description",
            "permissions",
            "is_active",
            "is_system_role",
            "created_at",
            "updated_at",
        ]

    def get_permissions(self, obj):
        return obj.permissions.filter(is_active=True).values_list("code_name", flat=True)


class UserRoleCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "role",
            "id"
        ]



# Only for listing purpose serializer
class UserListSerializer(serializers.ModelSerializer):
    """Basic user serializer for read operation"""
    
    roles = RoleSimpleSerializer(many=True, read_only=True)
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
            "roles",
            "permissions",
            "date_joined",
            "last_login",
            "updated_at",
        ]

    def get_permissions(self, obj):
        """
        Returns a flat list of all unique permission code_names the user has
        through their active roles.
        """
        # This query efficiently fetches all unique permission code_names
        user_permissions = set(
            obj.roles.filter(
                is_active = True
            ).values_list("permissions__code_name", flat=True).distinct()
        )
        return sorted([p for p in user_permissions if p])


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "email",
            "first_name",
            "last_name",
            "phone",
            "date_of_birth",
            "is_superuser",
            "is_active",
            "is_staff",
        ]



class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = [
            "user",
            "avatar",
            "bio",
            "gender",
            "location",
            "website",
        ]


class UserDetailSerializer(serializers.ModelSerializer):

    # user_profile = serializers.SerializerMethodField()
    user_profile = UserProfileSerializer(
        source="profile", required=False, allow_null=True
    )

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
            "updated_at",
            "user_profile",
        ]

        read_only_fields = [
            "id",
            "email",
            "is_superuser",
            "is_active",
            "is_staff",
            "date_joined",
            "last_login",
            "updated_at",
        ]

    def update(self, instance, validated_data):
        profile_data = validated_data.pop("user_profile")
        print(instance)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if profile_data is not None:
            UserProfile.objects.update_or_create(user=instance, defaults=profile_data)

        instance.refresh_from_db()
        return instance


class UserRoleAssignSerializer(serializers.ModelSerializer):
    roles = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Role.objects.all()
    )
    
    class Meta:
        model = User
        fields = [
            "roles"
        ]

        # roles can be a list for a user
        # can assign multiple roles at once
        # M:M relationship with user and role

    def update(self, instance, validated_data):
        roles = validated_data.pop("roles", None)
        if roles is not None:
            instance.roles.set(roles)
        return super().update(instance, validated_data)
from rest_framework import serializers
from .models import (
    Permission,
    PermissionCategory,
    Role,
    User,
    UserProfile,
    Address,
    UserRole,
)

# base serializer: look into
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        required=True,
        # style={"input_type": "password"}
    )
    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        # style={"input_type": "password"}
    )

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
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def validate(self, attrs):
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError(
                {"password": "The passwords do not match"}
            )
        try:
            validate_password(attrs['password'])
        except ValidationError as e:
            raise serializers.ValidationError({"password": list(e.messages)})
        return attrs
        

    def create(self, validated_data):
        validated_data.pop("password_confirm")

        user = User.objects.create_user(
            email = validated_data['email'],
            password = validated_data['password'],
            first_name = validated_data['first_name'],
            last_name = validated_data['last_name'],
            phone = validated_data['phone'],
            date_of_birth = validated_data["date_of_birth"]
        )
        return user


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


class UserRoleCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserRole
        fields = "__all__"

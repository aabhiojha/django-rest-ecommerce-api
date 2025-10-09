# from rest_framework import serializers
# from .models import User, UserProfile, Address


# class UserCreateSerializer(serializers.ModelSerializer):
#     password = serializers.CharField(write_only=True)
#     password_confirm = serializers.CharField(write_only=True)

#     class Meta:
#         model = User
#         fields = [
#             "username",
#             "email",
#             "password",
#             "password_confirm",
#             "first_name",
#             "last_name",
#             "phone",
#             "date_of_birth",
#         ]

#     def validate(self, attrs):
#         if attrs["password"] != attrs["password_confirm"]:
#             raise serializers.ValidationError("The passwords do not match.")
#         return attrs

#     def create(self, validated_data):
#         validated_data.pop("password_confirm")
#         password = validated_data.pop("password")
#         user = User.objects.create_user(**validated_data)
#         user.set_password(password)
#         user.save()
#         return user


# class UserUpdateSerializer(serializers.ModelSerializer):
#     password = serializers.CharField(write_only=True)
#     password_confirm = serializers.CharField(write_only=True)

#     class Meta:
#         model = User
#         fields = [
#             "username",
#             "password",
#             "password_confirm",
#             "first_name",
#             "last_name",
#             "phone",
#             "date_of_birth",
#         ]

#     def validate(self, attrs):
#         password = attrs.get("password")
#         password_confirm = attrs.get("password_confirm")
#         if password or password_confirm:
#             if password != password_confirm:
#                 raise serializers.ValidationError("The passwords do not match")
#         return attrs

#     def update(self, instance, validated_data):
#         password = validated_data.pop("password")
#         validated_data.pop("password_confirm")
#         for attr, value in validated_data.items():
#             setattr(instance, attr, value)
#         if password:
#             instance.set_password(password)
#         instance.save()
#         return instance


# class UserSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         fields = [
#             "id",
#             "username",
#             "email",
#             "first_name",
#             "last_name",
#             "phone",
#             "date_of_birth",
#         ]


# class UserProfileSerializer(serializers.ModelSerializer):
#     user = UserSerializer(read_only=True)

#     class Meta:
#         model = UserProfile
#         fields = [
#             "user",
#             "user_picture",
#             "bio",
#             "gender",
#         ]


# class UserProfileCreateSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = UserProfile
#         fields = [
#             "user_picture",
#             "bio",
#             "gender",
#         ]


# # Serializers for addresses
# # List
# class UserAddressListSerializer(serializers.ModelSerializer):
#     user = UserSerializer(read_only=True)

#     class Meta:
#         model = Address
#         fields = [
#             "id",
#             "user",
#             "address",
#             "address_descripton",
#             "is_primary",
#         ]


# # Create
# class UserAddressCreateSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Address
#         fields = [
#             "address",
#             "address_descripton",
#             "is_primary",
#         ]


# # Update Address
# class UserAddressUpdateSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Address
#         fields = [
#             "address",
#             "address_descripton",
#             "is_primary",
#         ]

#     def create(self, validated_data):
#         return super().create(validated_data)

from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from .serializers import (
    PasswordChangeSerializer,
    PasswordResetConfirmSerializer,
    PasswordResetSerializer,
    PermissionCategoryEditSerializer,
    PermissionCreateSerializer,
    PermissionEditSerializer,
    PermissionListSerializer,
    RoleCreateSerializer,
    RoleListSerializer,
    UserRoleCreateSerializer,
    PermissionCategoryListSerializer,
    PermissionCategoryCreateSerializer
)
from rest_framework.permissions import IsAuthenticated
from .permissions import HasPermissions

from core.email import welcome_mail

from .models import Role, User, OTP, UserRole, Permission, PermissionCategory
from .serializers import UserSerializer, UserCreateSerializer, UserRoleListSerializer

from .utils import generate_otp
from core.email import send_otp


class UserCreateView(APIView):
    """
    Create User
    """

    serializer_class = UserCreateSerializer

    def post(self, request):
        serializer = UserCreateSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            welcome_mail(user)

            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# password change view
class ChangePasswordView(APIView):
    serializer_class = PasswordChangeSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = PasswordChangeSerializer(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            serializer.save()

            return Response(
                {"message": "Password changed successfully"}, status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ResetPasswordView(APIView):
    serializer_class = PasswordResetSerializer

    def post(self, request):
        serializer = PasswordResetSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data.get("email")

            try:
                user = User.objects.get(email=email)

                otp_code = generate_otp(user)

                # Send OTP via email
                send_otp(user, otp_code)

                return Response(
                    {"detail": "Password reset OTP has been sent to your email."},
                    status=status.HTTP_200_OK,
                )

            except User.DoesNotExist:
                return Response(
                    {"detail": "The user associated with this email does not exist."},
                    status=status.HTTP_200_OK,
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ResetPasswordConfirmView(APIView):
    """
    check if otp exists and reset the password
    requires - email, otp and new password
    """

    serializer_class = PasswordResetConfirmSerializer

    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)

        if serializer.is_valid():
            email = serializer.validated_data.get("email")
            user_otp = serializer.validated_data.get("otp")
            new_password = serializer.validated_data.get("new_password")

            try:
                user = User.objects.get(email=email)

                #  possibilities
                # - the otp for this email does not exist
                # - user enters the otp after it has expired
                # - user tries to use the same otp to reset the password after
                #      resetting the password for the first time

                # Get the OTP record
                otp_record = OTP.objects.filter(
                    user=user,
                    otp=user_otp,
                    is_active=True,
                ).first()

                # Need to check if the otp is valid and not expired
                if otp_record and not otp_record.is_expired:
                    user.set_password(new_password)
                    user.save()

                    # delete the otp after password reset is complete
                    otp_record.delete()

                    return Response(
                        {"detail": "Password reset successful."},
                        status=status.HTTP_200_OK,
                    )

            except User.DoesNotExist:
                return Response(
                    {"error": "User not found."}, status=status.HTTP_404_NOT_FOUND
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



# Permission category views
class ListPermissionCategoriesView(APIView):
    serializer_class = PermissionCategoryListSerializer
    permission_classes = [IsAuthenticated, HasPermissions]
    permissions_required = ["can_manage_permissions"]

    def get(self, request):
        permission_category = PermissionCategory.objects.all()
        serializer = PermissionCategoryListSerializer(permission_category, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class CreatePermissionCategoriesView(APIView):
    serializer_class = PermissionCategoryCreateSerializer
    permission_classes = [IsAuthenticated, HasPermissions]
    permissions_required = ["can_manage_permissions"]

    def post(self, request):
        permission_category = request.data
        serializer = PermissionCategoryCreateSerializer(data=permission_category)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DeletePermissionCategoryView(APIView):
    lookup_field = "pk"
    permission_classes = [IsAuthenticated, HasPermissions]
    permissions_required = ["can_manage_permissions"]

    def delete(self, request, pk):
        # get the object
        permission_category = PermissionCategory.objects.get(id=pk)
        if not permission_category:
            return Response({"error":f"The category with id={pk} does not exist"}, status=status.HTTP_404_NOT_FOUND)
        permission_category.delete()
        return Response({"mesasge":f"The category {permission_category} has been deleted"}, status=status.HTTP_200_OK)


class EditPermissionCategoryView(APIView):
    serializer_class = PermissionCategoryCreateSerializer
    permission_classes = [IsAuthenticated, HasPermissions]
    permissions_required = ["can_manage_permissions"]
    lookup_field = "pk"

    def patch(self, request, pk):
        permission_category = PermissionCategory.objects.get(id=pk)
        serializer = PermissionCategoryEditSerializer(permission_category,data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            
# Permission Related views
class ListPermissionsView(APIView):
    serializer_class = PermissionListSerializer
    permission_classes = [IsAuthenticated, HasPermissions]
    permissions_required = ["can_manage_permissions"]

    def get(self, request):
        permission = Permission.objects.all()
        serializer = PermissionListSerializer(permission, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class CreatePermissionsView(APIView):
    serializer_class = PermissionCreateSerializer
    permission_classes = [IsAuthenticated, HasPermissions]
    permissions_required = ["can_manage_permissions"]

    def post(self, request):
        permission_category = request.data
        serializer = PermissionCreateSerializer(data=permission_category)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DeletePermissionView(APIView):
    lookup_field = "pk"
    permission_classes = [IsAuthenticated, HasPermissions]
    permissions_required = ["can_manage_permissions"]

    def delete(self, request, pk):
        # get the object
        permission = Permission.objects.get(id=pk)
        if not permission:
            return Response({"error":f"The permission with id={pk} does not exist"}, status=status.HTTP_404_NOT_FOUND)
        permission.delete()
        return Response({"mesasge":f"The permission {permission} has been deleted"},             status=status.HTTP_204_NO_CONTENT
)


class EditPermissionView(APIView):
    serializer_class = PermissionEditSerializer
    permission_classes = [IsAuthenticated, HasPermissions]
    permissions_required = ["can_manage_permissions"]
    lookup_field = "pk"

    def patch(self, request, pk):
        permission = Permission.objects.get(id=pk)
        serializer = PermissionEditSerializer(permission,data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        


# role ko lagi views
# userrole


class ListRolesView(APIView):
    """Lists all the roles in db"""
    serializer_class = RoleListSerializer

    def get(self, request):
        roles = Role.objects.all()
        serializer = RoleListSerializer(roles, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CreateRoleView(APIView):
    serializer_class = RoleCreateSerializer
    permission_classes = [IsAuthenticated, HasPermissions]
    permissions_required = "can_manage_roles"

    def post(self, request):
        serializer = RoleCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RoleCRUDView(APIView):
    permission_classes = [IsAuthenticated, HasPermissions]
    permissions_required = "can_manage_roles"

    def get(self, request, pk):
        role = Role.objects.get(pk=pk)
        serializer = RoleListSerializer(role)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, pk):
        role = Role.objects.get(pk=pk)
        serializer = RoleCreateSerializer(instance=role, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        role = Role.objects.get(pk=pk)

        role.delete()
        return Response(
            {"message": f"Role '{role.name}' has been deleted successfully."},
            status=status.HTTP_204_NO_CONTENT
        )






class UserRoleAssignView(APIView):
    """Assigns User with Role"""
    serializer_class = UserRoleCreateSerializer
    permission_classes = [IsAuthenticated, HasPermissions]
    permissions_required = "can_manage_roles"

    def post(self, request):
        serializer = UserRoleCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserRoleListView(APIView):
    """Lists the roles a user has"""

    serializer_class = UserRoleListSerializer

    def get(self, request):
        user_roles = UserRole.objects.all()
        serializer = UserRoleListSerializer(user_roles, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

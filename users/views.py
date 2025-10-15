from rest_framework import generics
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from .serializers import (
    PasswordChangeSerializer,
    PasswordResetConfirmSerializer,
    PasswordResetSerializer,
    RoleCreateSerializer,
    RoleListSerializer,
    UserRoleCreateSerializer,
)
from rest_framework.permissions import IsAuthenticated
from .permissions import HasPermission

from core.email import welcome_mail

from .models import Role, User, OTP, UserRole
from .serializers import UserSerializer, UserCreateSerializer, UserRoleListSerializer

from .utils import generate_otp
from core.email import send_otp


class UserCreateView(APIView):
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
                    status=status.HTTP_200_OK
                )
            
            except User.DoesNotExist:
                return Response(
                    {"detail": "The user associated with this email does not exist."},
                    status=status.HTTP_200_OK
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
                
                # TODO possibilities
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
                        status=status.HTTP_200_OK
                    )
                    
            except User.DoesNotExist:
                return Response(
                    {"error": "User not found."},
                    status=status.HTTP_404_NOT_FOUND
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# role ko lagi view chaiyo
# permission ko lagi chadiana
# userrole
class CreateRoleView(APIView):
    serializer_class = RoleCreateSerializer
    # permission_classes = [IsAuthenticated]
    permission_classes = [IsAuthenticated, HasPermission]
    permission_required = "can_manage_roles"

    def post(self, request):
        serializer = RoleCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserRoleCreateView(APIView):
    serializer_class = UserRoleCreateSerializer

    def post(self, request):
        serializer = UserRoleCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserRoleListView(APIView):
    serializer_class = UserRoleListSerializer

    def get(self, request):
        user_roles = UserRole.objects.all()
        serializer = UserRoleListSerializer(user_roles, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class ListRolesView(APIView):
    serializer_class = RoleListSerializer

    def get(self, request):
        roles = Role.objects.all()
        serializer = RoleListSerializer(roles, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
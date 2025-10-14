from rest_framework import generics
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from .serializers import (
    PasswordChangeSerializer,
    PasswordResetConfirmSerializer,
    PasswordResetSerializer,
    RoleCreateSerializer,
    UserRoleCreateSerializer,
)
from rest_framework.permissions import IsAuthenticated
from .permissions import HasPermission

from core.email import welcome_mail

from .models import Role, User, OTP
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
        serializer = PasswordResetSerializer(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            # send an otp to the user i.e. to the email mentioned by the request
            # print(serializer.validated_data.get("email"))

            email = serializer.validated_data.get("email")
            user = User.objects.get(email=email)

            otp_code = generate_otp()
            
            # function to send mail to the email address
            send_otp(user, otp_code)

            print(otp_code)

            OTP.objects.create(user=user, otp=otp_code)

            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ResetPasswordConfirmView(APIView):
    serializer_class = PasswordResetConfirmSerializer

    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)

        if serializer.is_valid():
            email = serializer.validated_data.get("email")
            # print(email)
            user_otp = serializer.validated_data.get("user_otp")
            # print(user_otp)
            new_password = serializer.validated_data.get("new_password")
            # print(new_password)

            user = User.objects.get(email=email)
            # print(user)
            
            opt_record = OTP.objects.filter(
                user=user, 
                otp=user_otp
                ).exists()
            # print(opt_record)

            if opt_record:
                user.set_password(new_password)
                user.save()
                return Response({"message":"Password reset successful"}, status=status.HTTP_200_OK)
        
        return Response({"message":"Invalid or expired OTP"}, status=status.HTTP_200_OK)


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
        serializer = UserRoleListSerializer()
        print(serializer)
        return Response(serializer.data, status=status.HTTP_200_OK)

from rest_framework import generics
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from .serializers import (
    PasswordChangeSerializer,
    RoleCreateSerializer,
    UserRoleCreateSerializer,
)
from rest_framework.permissions import IsAuthenticated
from .permissions import HasPermission

# from django.core.mail import send_mail
from core.email import welcome_mail

from .models import Role, User
from .serializers import UserSerializer, UserCreateSerializer, UserRoleListSerializer


# class UserCreateView(generics.CreateAPIView):
#     serializer_class = UserCreateSerializer
#     queryset = User.objects.all()


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
            user = serializer.save()
            print(user)

            return Response(serializer.data, status=status.HTTP_200_OK)
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
        serializer = UserRoleListSerializer()
        print(serializer)
        return Response(serializer.data, status=status.HTTP_200_OK)

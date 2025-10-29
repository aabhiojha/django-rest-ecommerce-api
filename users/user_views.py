from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics

from users.models import User, UserProfile
from core.email import welcome_mail

from .serializers import UserDetailSerializer, UserListSerializer, UserCreateSerializer, UserUpdateSerializer
from core.permissions import HasPermissions


class ListUsersView(APIView):
    serializer_class = UserListSerializer
    permission_classes = [IsAuthenticated, HasPermissions]
    permissions_required = ["can_view_users"]

    def get(self, request):
        users = User.objects.all()
        serializer = UserListSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserCreateView(APIView):
    serializer_class = UserCreateSerializer

    def post(self, request):
        serializer = UserCreateSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            welcome_mail(user)

            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserUpdateDeleteView(APIView):
    serializer_class = UserUpdateSerializer
    permission_classes = [IsAuthenticated, HasPermissions]
    permissions_required = ["can_edit_user"]

    def patch(self, request, pk):
        user = User.objects.get(id=pk)
        serializer = UserUpdateSerializer(user,data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        user = get_object_or_404(User, id=pk)
        user.delete()
        return Response({"message":f"User {user} is successfully deleted."}, status=status.HTTP_200_OK)


class UserProfileDetailView(APIView):
    serializer_class = UserDetailSerializer
    permission_classes = [IsAuthenticated, HasPermissions]
    permissions_required = ["can_view_users"]

    def get(self, request, pk):
        user = User.objects.get(pk=pk)
        serializer = UserDetailSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CurrentUserView(APIView):
    serializer_class = UserDetailSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserDetailSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request):
        serializer = UserDetailSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

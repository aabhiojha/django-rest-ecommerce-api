from rest_framework.generics import ListAPIView, CreateAPIView
from .serializers import UserListSerializer, UserCreateSerializer


class UserRegisterAPIView(CreateAPIView):
    serializer_class = UserCreateSerializer


class UserListAPIView(ListAPIView):
    serializer_class = UserListSerializer

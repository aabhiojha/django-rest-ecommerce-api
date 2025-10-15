# ## User Endpoints

# - `GET /api/users/` - List users (admin/staff)
# - `POST /api/users/` - Create user (admin)
# - `GET /api/users/me/` - Get current user profile
# - `PUT /api/users/me/` - Update current user
# - `PATCH /api/users/me/` - Partial update current user
# - `GET /api/users/{id}/` - Get specific user (admin/staff)
# - `PUT /api/users/{id}/` - Update user (admin)
# - `PATCH /api/users/{id}/` - Partial update user (admin)
# - `DELETE /api/users/{id}/` - Deactivate user (admin)

from rest_framework.views import APIView

from users.models import User
from .serializers import UserSerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework import generics

# class ListUsersView(APIView):
#     serializer_class = UserSerializer
#     permission_classes = [IsAuthenticated]
#     queryset = User.objects.all()

    # def get(self, request):
    #     users = User.objects.all()
    #     serializer = UserSerializer(users, many=True)
    #     return Response(serializer.data, status=status.HTTP_200_OK)


class ListUsersView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class= UserSerializer


class CurrentUserView(APIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "pk"

    # def get(self, request):
    #     serializer = UserSerializer(request.user)
    #     return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, *args, **kwargs):
        serializer = UserSerializer(request.user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request):
        serializer = UserSerializer(request.user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



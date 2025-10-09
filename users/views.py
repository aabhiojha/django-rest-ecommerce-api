# from django.shortcuts import render

# # Create your views here.
# from rest_framework.generics import (
#     CreateAPIView,
#     RetrieveAPIView,
#     UpdateAPIView,
#     ListAPIView,
# )
# from rest_framework.authtoken.views import ObtainAuthToken
# from rest_framework.authtoken.models import Token
# from rest_framework.response import Response
# from .serializers import (
#     UserAddressCreateSerializer,
#     UserCreateSerializer,
#     UserProfileSerializer,
#     UserUpdateSerializer,
#     UserAddressListSerializer,
#     UserAddressUpdateSerializer,
# )
# from accounts.models import User
# from rest_framework.permissions import IsAuthenticated, IsAdminUser
# from rest_framework.views import APIView
# from .models import Address, UserProfile


# # POST /auth/register/ - User registration
# # POST /auth/login/ - User login
# # POST /auth/logout/ - User logout
# # POST /auth/refresh/ - Token refresh
# # GET /users/me/ - Get current user
# # PUT /users/me/ - Update user profile
# # GET /users/me/addresses/ - List user addresses
# # POST /users/me/addresses/ - Add new address
# # PUT /users/me/addresses/{id}/ - Update address
# # DELETE /users/me/addresses/{id}/ - Delete address


# # User login and register.
# class UserRegisterAPIView(CreateAPIView):
#     serializer_class = UserCreateSerializer


# class UserLoginAPIView(ObtainAuthToken):
#     def post(self, request, *args, **kwargs):
#         serializer = self.serializer_class(
#             data=request.data, context={"request": request}
#         )
#         serializer.is_valid(raise_exception=True)
#         user = serializer.validated_data["user"]
#         token, created = Token.objects.get_or_create(user=user)
#         return Response(
#             {
#                 "token": token.key,
#                 "user_id": user.pk,
#                 "email": user.email,
#                 "username": user.username,
#             }
#         )


# # SHow the authenticated user's profile
# class UserMeAPIView(RetrieveAPIView):
#     serializer_class = UserProfileSerializer
#     permission_classes = [IsAuthenticated]

#     def get_object(self):
#         return UserProfile.objects.get(user=self.request.user)


# class UserUpdateAPIView(UpdateAPIView):
#     serializer_class = UserUpdateSerializer
#     permission_classes = [IsAuthenticated]

#     def get_object(self):
#         return User.objects.get(user=self.request.user)


# # create/make the user's profile
# class UserProfileCreateAPIView(CreateAPIView):
#     serializer_class = UserProfileSerializer
#     permission_classes = [IsAuthenticated]


# # create and list addresses
# # auth/users/me/addresses/
# # get all addresses of request user
# class UserAddressListAPIView(ListAPIView):
#     permission_classes = [IsAuthenticated]
#     serializer_class = UserAddressListSerializer

#     def get_queryset(self):
#         return Address.objects.filter(user=self.request.user)
#         # return Address.objects.all()


# # add address for the user
# class UserAddressAddAPIView(CreateAPIView):
#     permission_classes = [IsAuthenticated]
#     serializer_class = UserAddressCreateSerializer

#     def perform_create(self, serializer):
#         # Automatically set the user to the current authenticated user
#         serializer.save(user=self.request.user)


# # update address
# class UserAddressUpdateAPIView(UpdateAPIView):
#     permission_classes = [IsAuthenticated]
#     serializer_class = UserAddressUpdateSerializer

#     def get_queryset(self):
#         return Address.objects.filter(user=self.request.user)

#     def get_object(self):
#         # Get the specific address by ID, but only if it belongs to the current user
#         address_id = self.kwargs.get("pk")
#         try:
#             return Address.objects.get(id=address_id, user=self.request.user)
#         except Address.DoesNotExist:
#             from rest_framework.exceptions import NotFound

#             raise NotFound(
#                 "Address not found or you don't have permission to update it."
#             )

#     def perform_update(self, serializer):
#         # Ensure the user field is always set to the current user
#         serializer.save(user=self.request.user)

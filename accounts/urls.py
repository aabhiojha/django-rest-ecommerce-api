from django.urls import path
from . import views

urlpatterns = [
    path("register/", views.UserRegisterAPIView.as_view()),
    path("login/", views.UserLoginAPIView.as_view()),
    path("users/me/", views.UserMeAPIView.as_view()),
    path("users/me/", views.UserUpdateAPIView.as_view()),
    path("create-profile/", views.UserProfileCreateAPIView.as_view()),
    path("address/list/", views.UserAddressListAPIView.as_view()),
    path("address/add/", views.UserAddressAddAPIView.as_view()),
    path("address/update/<int:pk>/", views.UserAddressUpdateAPIView.as_view()),
]

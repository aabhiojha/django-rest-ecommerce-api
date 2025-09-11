from django.urls import path, include
from . import views

urlpatterns = [
    path("register/", views.UserRegisterAPIView.as_view()),
    path("login/", views.UserListAPIView.as_view()),
]

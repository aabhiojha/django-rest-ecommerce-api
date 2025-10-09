from django.urls import path
from . import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    # JWT token
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # User CRUD
    path("auth/user/list/", views.UserListAPIView.as_view()),
    path("auth/user/create/", views.UserCreateAPIView.as_view()),

]
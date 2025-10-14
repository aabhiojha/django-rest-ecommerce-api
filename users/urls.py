from django.urls import path
from . import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    # JWT token
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    # user specific
    path("user/create/", views.UserCreateView.as_view(), name="user-create"),
    path("user/password/change/", views.ChangePasswordView.as_view()),
    path("user/password/reset/", views.ResetPasswordView.as_view()),
    path("user/password/reset/confirm/", views.ResetPasswordConfirmView.as_view()),
    # role
    path("role/create/", views.CreateRoleView.as_view()),
    path("user/role/assign/", views.UserRoleCreateView.as_view()),
    path("user/role/list/", views.UserRoleListView.as_view()),

]

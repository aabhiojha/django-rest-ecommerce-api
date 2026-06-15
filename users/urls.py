from django.urls import path
from . import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from . import user_views

urlpatterns = [
    # JWT token
    path("token", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh", TokenRefreshView.as_view(), name="token_refresh"),
    # user specific
    path("user/list", user_views.ListUsersView.as_view()),
    path("user/register", user_views.UserCreateView.as_view(), name="user-create"),
    path("user/password/change", views.ChangePasswordView.as_view()),
    path("user/password/reset", views.ResetPasswordView.as_view()),
    path("user/password/reset/confirm", views.ResetPasswordConfirmView.as_view()),
    path("user/<int:pk>",user_views.UserProfileDetailView.as_view()),
    path("user/me", user_views.CurrentUserView.as_view()),
    # Permission category
    path("permission/category/list", views.ListPermissionCategoriesView.as_view()),
    path("permission/category/create", views.CreatePermissionCategoriesView.as_view()),
    path("permission/category/delete/<int:pk>", views.DeletePermissionCategoryView.as_view()),
    path("permission/category/edit/<int:pk>",views.EditPermissionCategoryView.as_view()),
    # Permission
    path("permission/list",views.ListPermissionsView.as_view()),
    path("permission/create",views.CreatePermissionsView.as_view()),
    path("permission/delete/<int:pk>",views.DeletePermissionView.as_view()),
    path("permission/edit/<int:pk>",views.EditPermissionView.as_view()),
    # role
    path("role/list", views.ListRolesView.as_view()),
    path('role/create', views.CreateRoleView.as_view()),
    path("role/<int:pk>", views.RoleCRUDView.as_view()),
    # User-Role assignment    
    path("user/role/assign/<int:pk>", views.UserRoleAssignView.as_view()),
    # path("user/role/list/", views.UserRoleListView.as_view()),
]
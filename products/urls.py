from django.urls import path
from . import views

urlpatterns = [
    path("category/", views.CategoryListCreateAPIView.as_view()),
    path("category/<int:pk>/", views.CategoryDetailAPIView.as_view()),
    path("", views.ProductListAPIView.as_view()),
]

from django.urls import path
from . import views

urlpatterns = [
    path("category/", views.CategoryListCreateAPIView.as_view()),
    path("category/<int:pk>/", views.CategoryDetailAPIView.as_view()),
    path("list/", views.ProductListAPIView.as_view()),
    path("detail/<int:pk>/", views.ProductDetailAPIView.as_view()),
]

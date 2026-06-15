from django.urls import path
from . import views

urlpatterns = [
    path("category/list", views.CategoryListAPIView.as_view()),
    path("category/create", views.CategoryCreateAPIView.as_view()),
    path("category/<int:pk>", views.CategoryDetailAPIView.as_view()),
    path("list", views.ProductListAPIView.as_view()),

    # seller specific
    path("create", views.ProductCreateAPIView.as_view()),
    path("update/<int:pk>", views.ProductUpdateAPIView.as_view()),
    path("detail/<int:pk>", views.ProductDetailAPIView.as_view()),
    path("delete/<int:pk>", views.ProductDeleteAPIView.as_view()),
    path("my_list",views.SellerProductListAPIView.as_view()),
    path("orders/list", views.SellerProductOrdersAPIView.as_view()),
    path("transaction/seller", views.SellerStatsAPIView.as_view()),
]

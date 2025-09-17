from django.urls import path
from . import views

urlpatterns = [
    path("list/cart/", views.CartListAPIView.as_view()),
    path("list/items/", views.CartItemsListAPIView.as_view()),
    path("item/add/", views.CartItemAddAPIView.as_view()),
    path("item/update/<int:pk>/", views.CartItemQuantityUpdateAPIView.as_view()),
    path("item/delete/<int:pk>/", views.CartItemQuantityDeleteAPIView.as_view()),
]

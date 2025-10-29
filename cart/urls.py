from django.urls import path
from . import views

urlpatterns = [
    path("list/carts/", views.CartListAPIView.as_view()),
    path("list/items/", views.CartItemsListAPIView.as_view()),
    path("item/add/", views.CartItemAddAPIView.as_view()),
    path("item/update/<int:pk>/", views.CartItemQuantityUpdateAPIView.as_view()),
    path("item/delete/<int:pk>/", views.CartItemDeleteAPIView.as_view()),
    path("favorite/list/", views.ListFavouriteAPIView.as_view()),
    path("favorite/create/", views.CreateFavouriteAPIView.as_view()),
    path("favorite/delete/", views.DeleteFavouriteAPIView.as_view()),
]

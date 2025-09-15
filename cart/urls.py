from django.urls import path
from . import views

urlpatterns = [
    path("list/", views.CartListAPIView.as_view()),
    path("items/", views.CartItemsListAPIView.as_view()),
]

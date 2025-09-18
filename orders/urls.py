from django.urls import path
from .views import (
    OrderListCreateAPIView,
    OrderDetailAPIView,
    OrderItemsCreateAPIView,
    OrderItemListView,
    UserOrdersListView,
)

urlpatterns = [
    path("", OrderListCreateAPIView.as_view(), name="order-list-create"),
    path("<str:pk>/", OrderDetailAPIView.as_view(), name="order-detail"),
    path("items/create/", OrderItemsCreateAPIView.as_view(), name="orderitem-create"),
    path("<str:order_id>/items/", OrderItemListView.as_view(), name="orderitem-list"),
    path("user/orders/", UserOrdersListView.as_view(), name="user-orders"),
]

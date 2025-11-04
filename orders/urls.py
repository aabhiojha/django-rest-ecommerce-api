from django.urls import path
from .views import (
    DiscountCodeCRUD,
    OrderListAPIView,
    # OrderCreateAPIView,
    OrderDetailAPIView,
    OrderItemsCreateAPIView,
    OrderItemListView,
    UpdateOrderStatusView,
    UserOrdersListView,
    OrderListAllAPIView
)

urlpatterns = [
    path("list/", OrderListAPIView.as_view(), name="order-list"),
    path("list/all/", OrderListAllAPIView.as_view(), name="order-lists"),
    path("<str:pk>/", OrderDetailAPIView.as_view(), name="order-detail"),
    path("items/create/", OrderItemsCreateAPIView.as_view(), name="orderitem-create"),
    path("<str:order_id>/items/", OrderItemListView.as_view(), name="orderitem-list"),
    path("user/orders/", UserOrdersListView.as_view(), name="user-orders"),
    path("update_status/<str:pk>/", UpdateOrderStatusView.as_view(), name="update_order_status"),
    path('discounts/', DiscountCodeCRUD.as_view(), name='discount-list-create'),
    path('discounts/<str:code_name>/', DiscountCodeCRUD.as_view(), name='discount-detail'),
]

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from orders.models import Order, OrderItems
from .serializers import (
    OrderItemsCreateSerializer,
    OrderSerializer,
    OrderItemSerializer,
)


class OrderListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Only show orders for the authenticated user
        return Order.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        # Automatically set the user to the authenticated user
        serializer.save(user=self.request.user)


class OrderDetailAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)


class OrderItemsCreateAPIView(generics.CreateAPIView):
    serializer_class = OrderItemsCreateSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Ensure the order belongs to the authenticated user
        order = serializer.validated_data["order"]
        if order.user != request.user:
            return Response(
                {"error": "You can only add items to your own orders"},
                status=status.HTTP_403_FORBIDDEN,
            )

        result = serializer.save()
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.to_representation(result),
            status=status.HTTP_201_CREATED,
            headers=headers,
        )


class OrderItemListView(generics.ListAPIView):
    serializer_class = OrderItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        order_id = self.kwargs.get("order_id")
        order = get_object_or_404(Order, id=order_id, user=self.request.user)
        return OrderItems.objects.filter(order=order)


class UserOrdersListView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related(
            "order_items"
        )

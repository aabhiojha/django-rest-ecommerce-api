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
        # gets the orders of authenticated user
        return Order.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        # this sets the user to the authenticated user
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
        # if someone is creating order for the first time
        # also meaning if they didn't pass order, new one is created
        if "order" not in request.data:
            order = Order.objects.create(user=request.user, status="pending")
            request.data["order"] = order.id

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # check to see if user has that order
        order = serializer.validated_data.get("order")
        if order.user != request.user:
            return Response(
                {"error": "You can only add items to your own orders"},
                status=status.HTTP_403_FORBIDDEN,
            )

        result = serializer.save()
        return Response(
            serializer.to_representation(result),
            status=status.HTTP_201_CREATED,
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
        return Order.objects.filter(user=self.request.user)

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView # Import APIView

from orders.models import Order, OrderItems
from .serializers import (
    OrderItemsCreateSerializer,
    OrderSerializer,
    OrderItemSerializer,
)


class OrderListAPIView(APIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request):
        orders = Order.objects.filter(user=request.user)
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    
class OrderCreateAPIView(APIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = OrderSerializer(data=request.data)
        if serializer.is_valid():
            # Set the user to the authenticated user before saving
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class OrderDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk, user):
        """Helper method to get an order object or raise a 404 error."""
        return get_object_or_404(Order, id=pk, user=user)

    def get(self, request, pk):
        """Handles GET requests to retrieve a single order's details."""
        order = self.get_object(pk, request.user)
        serializer = OrderSerializer(order)
        return Response(serializer.data)

    def put(self, request, pk):
        """Handles PUT requests to update an order."""
        order = self.get_object(pk, request.user)
        serializer = OrderSerializer(instance=order, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        """Handles PATCH requests to partially update an order."""
        order = self.get_object(pk, request.user)
        serializer = OrderSerializer(instance=order, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OrderItemsCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        """Handles POST requests to add an item to an order."""
        mutable_data = request.data.copy()

        # if someone is creating order for the first time
        # also meaning if they didn't pass order, new one is created
        if "order" not in mutable_data:
            order = Order.objects.create(user=request.user, status="pending")
            mutable_data["order"] = order.id

        serializer = OrderItemsCreateSerializer(data=mutable_data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # check to see if user has that order
        order = serializer.validated_data.get("order")
        if order.user != request.user:
            return Response(
                {"error": "You can only add items to your own orders"},
                status=status.HTTP_403_FORBIDDEN,
            )

        instance = serializer.save()
        # Use the serializer's representation for the output
        output_serializer = OrderItemsCreateSerializer(instance)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)


class OrderItemListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, order_id):
        """Handles GET requests to list items for a specific order."""
        # Ensure the user owns the order they are trying to view items for
        order = get_object_or_404(Order, id=order_id, user=request.user)
        order_items = OrderItems.objects.filter(order=order)
        serializer = OrderItemSerializer(order_items, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserOrdersListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Handles GET requests to list all orders for the authenticated user."""
        orders = Order.objects.filter(user=request.user)
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
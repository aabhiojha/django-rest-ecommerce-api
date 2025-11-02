from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView  # Import APIView

from orders.filters import OrderFilter
from orders.models import Order, OrderItems
from .serializers import (
    OrderItemsCreateSerializer,
    OrderSerializer,
    OrderItemSerializer,
    UpdateOrderStatusSerializer
)

from core.permissions import HasPermissions

class OrderListAPIView(APIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated, HasPermissions]
    permissions_required = ["can_view_own_orders"]

    def get(self, request):
        orders = Order.objects.filter(user=request.user)
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# class OrderListAllAPIView(APIView):
#     serializer_class = OrderSerializer
#     permission_classes = [IsAuthenticated, HasPermissions]
#     permissions_required = ["can_view_own_orders"]
#     filter = OrderFilter

#     def get(self, request):
#         orders = Order.objects.all()
#         serializer = OrderSerializer(orders, many=True)
#         return Response(serializer.data, status=status.HTTP_200_OK)


# filters chaiyooo
class OrderListAllAPIView(generics.ListAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated, HasPermissions]
    permissions_required = ["can_manage_all_orders"]
    filterset_class = OrderFilter


# class OrderCreateAPIView(APIView):
#     serializer_class = OrderSerializer
#     permission_classes = [IsAuthenticated, HasPermissions]
#     permissions_required = ["can_place_orders"]

#     def post(self, request):
#         serializer = OrderSerializer(data=request.data)
#         if serializer.is_valid():
#             # Set the user to the authenticated user before saving
#             serializer.save(user=request.user)
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OrderDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]
    permission_classes = [IsAuthenticated, HasPermissions]
    permissions_required = ["can_view_own_orders"]

    def get_object(self, pk, user):
        return get_object_or_404(Order, id=pk, user=user)

    def get(self, request, pk):
        order = self.get_object(pk, request.user)
        serializer = OrderSerializer(order)
        return Response(serializer.data)

    def put(self, request, pk):
        order = self.get_object(pk, request.user)
        serializer = OrderSerializer(instance=order, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        order = self.get_object(pk, request.user)
        serializer = OrderSerializer(instance=order, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OrderItemsCreateAPIView(APIView):
    permission_classes = [IsAuthenticated, HasPermissions]
    permissions_required = ["can_place_orders"]

    def post(self, request, *args, **kwargs):
        mutable_data = request.data.copy()

        # if someone is creating order for the first time
        # also meaning if they didn't pass order, new one is created
        if "order" not in mutable_data:
            order = Order.objects.create(user=request.user, status="pending")
            mutable_data["order"] = order.id

        serializer = OrderItemsCreateSerializer(data=mutable_data, context=self.request.user)
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
    permission_classes = [IsAuthenticated, HasPermissions]
    permissions_required = ["can_view_own_orders"]

    def get(self, request, order_id):
        """Handles GET requests to list items for a specific order."""
        # Ensure the user owns the order they are trying to view items for
        order = get_object_or_404(Order, id=order_id, user=request.user)
        order_items = OrderItems.objects.filter(order=order)
        serializer = OrderItemSerializer(order_items, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserOrdersListView(APIView):
    permission_classes = [IsAuthenticated, HasPermissions]
    permissions_required = ["can_view_own_orders"]

    def get(self, request):
        """Handles GET requests to list all orders for the authenticated user."""
        orders = Order.objects.filter(user=request.user)
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

# seller can override orde_status
class UpdateOrderStatusView(APIView):
    permission_classes = [IsAuthenticated, HasPermissions]
    permissions_required = ["can_override_order_status"]
    serializer_class = UpdateOrderStatusSerializer

    def patch(self, request,pk):
        data = request.data
        order = Order.objects.get(id=pk)
        serializer = UpdateOrderStatusSerializer(order,data=data, partial=True)
        if serializer.is_valid():
            # Set the user to the authenticated user before saving
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

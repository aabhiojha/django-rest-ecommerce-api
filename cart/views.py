from rest_framework import generics
from .models import Cart, CartItem
from .serializers import (
    CartItemSerializer,
    CartSerializer,
    UpdateCartItemQuantitySerializer,
    AddItemSerializer,
)
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.permissions import IsAuthenticated
from core.permissions import HasPermissions
from rest_framework.views import APIView


# only admin can list all the carts
class CartListAPIView(APIView):
    permission_classes = [IsAuthenticated, HasPermissions]
    permissions_required = "can_manage_all_carts"

    def get(self, request):
        carts = Cart.objects.all()
        serializer = CartSerializer(carts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# List cart items of the requesting user
class CartItemsListAPIView(APIView):
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated, HasPermissions]
    permissions_required = ["can_manage_own_cart"]

    def get(self, request):
        try:
            # getting cart of the requesting user
            cart = Cart.objects.get(user=request.user)
        except Cart.DoesNotExist:
            return Response([], status=status.HTTP_200_OK)

        # items of the cart of that user
        queryset = CartItem.objects.filter(cart=cart)
        serializer = CartItemSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CartItemAddAPIView(APIView):
    serializer_class = AddItemSerializer
    permission_classes = [IsAuthenticated, HasPermissions]
    permissions_required = ["can_manage_own_cart"]

    def post(self, request):
        # context is a way to pass additional information to serializer.
        # in this case, its used to get request user.
        # i couldv'e done this in view itself but handeling things in serializer is cool ig.
        serializer = AddItemSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CartItemQuantityUpdateAPIView(APIView):
    serializer_class = UpdateCartItemQuantitySerializer    
    permission_classes = [IsAuthenticated, HasPermissions]
    permissions_required = ["can_manage_own_cart"]
    # This is needed in generics. not here
    # lookup_field = "pk"

    def patch(self, request, pk):
        user = request.user
        try:
            cart_item = CartItem.objects.get(id=pk, cart__user=user)
            print(cart_item)
        except CartItem.DoesNotExist:
            return Response(
                "The CartItem doesn't exist or isn't owned by you.", status=status.HTTP_400_BAD_REQUEST
            )
        serializer = UpdateCartItemQuantitySerializer(
            cart_item, data=request.data, partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CartItemDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated, HasPermissions]
    permissions_required = ["can_manage_own_cart"]

    def delete(self, request, pk):
        try:
            cart_item = CartItem.objects.get(id=pk, cart__user=request.user)
            print(cart_item)
        except CartItem.DoesNotExist:
            return Response(
                "The CartItem doesn't exist or isn't owned by you.", status=status.HTTP_400_BAD_REQUEST
            )
        cart_item.delete()
        return Response(f"The {cart_item.product.name} was deleted from cart.")

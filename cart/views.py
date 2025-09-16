from rest_framework import generics
from .models import Cart, CartItem
from .serializers import (
    CartItemSerializer,
    CartSerializer,
    UpdateCartItemSerializer,
    AddItemSerializer,
)
from rest_framework.response import Response
from rest_framework import status


class CartItemsListAPIView(generics.ListAPIView):
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer


class CartListAPIView(generics.ListAPIView):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer

    def get_object(self):
        return super().get_object()


class CartItemAddAPIView(generics.CreateAPIView):
    serializer_class = AddItemSerializer
    queryset = CartItem.objects.all()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

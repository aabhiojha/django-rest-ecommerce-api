from rest_framework import generics
from .models import Cart, CartItem
from .serializers import CartItemSerializer, CartSerializer


class CartItemsListAPIView(generics.ListAPIView):
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer


class CartListAPIView(generics.ListAPIView):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer

    def get_object(self):
        return super().get_object()

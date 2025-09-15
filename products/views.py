from rest_framework import generics
from .serializers import (
    CategoryListSerializer,
    CategoryDetailSerializer,
    CategoryCreateSerializer,
    ProductListSerializer,
)

from .models import Category, ProductVarient, ProductImage, ProductAttribute, Product


class CategoryListCreateAPIView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategoryListSerializer


class CategoryDetailAPIView(generics.RetrieveAPIView):
    queryset = Category.objects.all()
    lookup_field = "pk"
    serializer_class = CategoryDetailSerializer


class CategoryCreateAPIView(generics.CreateAPIView):
    serializer_class = CategoryCreateSerializer


# Product
class ProductListAPIView(generics.ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductListSerializer

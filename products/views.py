from rest_framework import generics
from .serializers import (
    CategoryListSerializer,
    CategoryDetailSerializer,
    CategoryCreateSerializer,
    ProductListSerializer,
    ProductDetailSerializer,
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
    filterset_fields = ["category"]


class ProductDetailAPIView(generics.RetrieveAPIView):
    queryset = Product.objects.select_related("category").prefetch_related(
        "images", "varients", "attributes"
    )
    lookup_field = "pk"
    serializer_class = ProductDetailSerializer

    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)

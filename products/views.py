from rest_framework import generics

# from rest_framework import filters
# from django_filters.rest_framework import DjangoFilterBackend
from .serializers import (
    CategoryListSerializer,
    CategoryDetailSerializer,
    CategoryCreateSerializer,
    ProductListSerializer,
    ProductDetailSerializer,
)

from .models import Category, ProductVarient, ProductImage, ProductAttribute, Product

from .pagination import ProductCursorPagination
from .filters import ProductFilter


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
    queryset = Product.objects.all().order_by("-created_at")
    serializer_class = ProductListSerializer
    pagination_class = ProductCursorPagination
    # filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = ProductFilter
    search_fields = ["name", "brand", "description", "sku"]


class ProductDetailAPIView(generics.RetrieveAPIView):
    queryset = Product.objects.select_related("category").prefetch_related(
        "images", "varients", "attributes"
    )
    lookup_field = "pk"
    serializer_class = ProductDetailSerializer
